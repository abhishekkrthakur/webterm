"""Tests for FastAPI application factory."""

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from webterm.api.app import PUBLIC_PATHS, create_app


class TestCreateApp:
    """Tests for create_app function."""

    def test_create_app_returns_fastapi(self):
        """Test that create_app returns a FastAPI instance."""
        app = create_app()
        assert isinstance(app, FastAPI)

    def test_app_has_title(self):
        """Test that app has correct title."""
        app = create_app()
        assert app.title == "WebTerm"

    def test_app_has_routes(self):
        """Test that app has expected routes."""
        app = create_app()
        routes = [route.path for route in app.routes]

        # Check for expected routes
        assert "/" in routes
        assert "/health" in routes
        assert "/ws/terminal" in routes


class TestPublicPaths:
    """Tests for public paths configuration."""

    def test_public_paths_contains_auth(self):
        """Test that auth paths are public."""
        assert "/auth/login" in PUBLIC_PATHS
        assert "/auth/logout" in PUBLIC_PATHS

    def test_public_paths_contains_health(self):
        """Test that health path is public."""
        assert "/health" in PUBLIC_PATHS


class TestAuthMiddleware:
    """Tests for authentication middleware."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_public_paths_accessible_without_auth(self, client):
        """Test that public paths are accessible without authentication."""
        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/auth/login")
        # Should return 200 or redirect (302) depending on auth state
        assert response.status_code in (200, 302)

    def test_static_files_accessible(self, client):
        """Test that static files are accessible."""
        # Static files should be accessible (may 404 if file doesn't exist)
        response = client.get("/static/css/terminal.css")
        # Should not be 401
        assert response.status_code != 401

    def test_protected_routes_redirect_when_auth_enabled(self):
        """Test that protected routes redirect to login when auth is enabled."""
        app = create_app()
        with patch("webterm.api.app.is_auth_enabled", return_value=True):
            with patch("webterm.api.app.check_auth", return_value=False):
                client = TestClient(app, follow_redirects=False)
                response = client.get("/", headers={"accept": "text/html"})
                assert response.status_code == 302
                assert "/auth/login" in response.headers.get("location", "")

    def test_protected_routes_return_401_for_api(self):
        """Test that protected API routes return 401 when not authenticated."""
        app = create_app()
        with patch("webterm.api.app.is_auth_enabled", return_value=True):
            with patch("webterm.api.app.check_auth", return_value=False):
                client = TestClient(app)
                response = client.get("/api/files", headers={"accept": "application/json"})
                assert response.status_code == 401


class TestStaticFiles:
    """Tests for static file serving."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_css_served(self, client):
        """Test that CSS files are served."""
        response = client.get("/static/css/terminal.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_js_served(self, client):
        """Test that JS files are served."""
        response = client.get("/static/js/terminal.js")
        assert response.status_code == 200
        assert "javascript" in response.headers["content-type"]
