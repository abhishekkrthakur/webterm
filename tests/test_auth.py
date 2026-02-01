"""Tests for authentication module."""

from unittest.mock import patch

from webterm.api.auth import (
    AUTH_COOKIE_NAME,
    get_login_page,
    is_auth_enabled,
    verify_token,
)


class TestIsAuthEnabled:
    """Tests for is_auth_enabled function."""

    def test_auth_disabled_when_no_token(self):
        """Test auth is disabled when token is None."""
        with patch("webterm.api.auth.settings") as mock_settings:
            mock_settings.token = None
            assert is_auth_enabled() is False

    def test_auth_disabled_when_empty_token(self):
        """Test auth is disabled when token is empty string."""
        with patch("webterm.api.auth.settings") as mock_settings:
            mock_settings.token = ""
            assert is_auth_enabled() is False

    def test_auth_enabled_when_token_set(self):
        """Test auth is enabled when token is set."""
        with patch("webterm.api.auth.settings") as mock_settings:
            mock_settings.token = "secret-token"
            assert is_auth_enabled() is True


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_verify_valid_token(self):
        """Test verification of valid token."""
        with patch("webterm.api.auth.settings") as mock_settings:
            mock_settings.token = "correct-token"
            with patch("webterm.api.auth.is_auth_enabled", return_value=True):
                assert verify_token("correct-token") is True

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        with patch("webterm.api.auth.settings") as mock_settings:
            mock_settings.token = "correct-token"
            with patch("webterm.api.auth.is_auth_enabled", return_value=True):
                assert verify_token("wrong-token") is False

    def test_verify_when_auth_disabled(self):
        """Test verification always passes when auth is disabled."""
        with patch("webterm.api.auth.is_auth_enabled", return_value=False):
            assert verify_token("any-token") is True
            assert verify_token("") is True


class TestGetLoginPage:
    """Tests for get_login_page function."""

    def test_returns_html(self):
        """Test that login page returns HTML."""
        html = get_login_page()
        assert "<!DOCTYPE html>" in html
        assert "<title>WebTerm - Login</title>" in html
        assert '<form id="login-form">' in html
        assert 'type="password"' in html

    def test_contains_login_form(self):
        """Test that login page contains necessary form elements."""
        html = get_login_page()
        assert "token" in html
        assert "Login" in html
        assert "/auth/login" in html


class TestAuthCookieName:
    """Tests for AUTH_COOKIE_NAME constant."""

    def test_cookie_name(self):
        """Test the auth cookie name."""
        assert AUTH_COOKIE_NAME == "webterm_auth"
