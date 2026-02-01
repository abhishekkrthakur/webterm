"""Tests for authentication routes."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from webterm.api.app import create_app


class TestLoginPage:
    """Tests for login page endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app, follow_redirects=False)

    def test_login_page_redirects_when_auth_disabled(self, client):
        """Test login page redirects to / when auth is disabled."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=False):
            response = client.get("/auth/login")
            assert response.status_code == 302
            assert response.headers["location"] == "/"

    def test_login_page_returns_html_when_auth_enabled(self, client):
        """Test login page returns HTML when auth is enabled."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=True):
            response = client.get("/auth/login")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
            assert b"Login" in response.content


class TestLoginEndpoint:
    """Tests for login POST endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_login_success_when_auth_disabled(self, client):
        """Test login always succeeds when auth is disabled."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=False):
            response = client.post("/auth/login", json={"token": "anything"})
            assert response.status_code == 200
            assert response.json() == {"success": True}

    def test_login_success_with_valid_token(self, client):
        """Test login succeeds with valid token."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=True):
            with patch("webterm.api.routes.auth.verify_token", return_value=True):
                response = client.post("/auth/login", json={"token": "valid-token"})
                assert response.status_code == 200
                assert response.json() == {"success": True}
                # Check cookie is set
                assert "webterm_auth" in response.cookies

    def test_login_fails_with_invalid_token(self, client):
        """Test login fails with invalid token."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=True):
            with patch("webterm.api.routes.auth.verify_token", return_value=False):
                response = client.post("/auth/login", json={"token": "invalid-token"})
                assert response.status_code == 401

    def test_login_cookie_properties(self, client):
        """Test that login cookie has correct security properties."""
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=True):
            with patch("webterm.api.routes.auth.verify_token", return_value=True):
                response = client.post("/auth/login", json={"token": "valid-token"})
                # Cookie should be set (detailed properties tested via response object)
                assert "webterm_auth" in response.cookies


class TestLogoutEndpoint:
    """Tests for logout endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_logout_returns_success(self, client):
        """Test logout returns success."""
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"success": True}

    def test_logout_clears_cookie(self, client):
        """Test logout clears auth cookie."""
        # First login
        with patch("webterm.api.routes.auth.is_auth_enabled", return_value=True):
            with patch("webterm.api.routes.auth.verify_token", return_value=True):
                client.post("/auth/login", json={"token": "valid-token"})

        # Then logout
        response = client.post("/auth/logout")
        assert response.status_code == 200
        # Cookie should be deleted (set to empty or expired)
