"""Tests for configuration module."""

import os
from unittest.mock import patch

from webterm.core.config import Settings


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.host == "127.0.0.1"
        assert settings.port == 8000
        assert settings.reload is False
        assert settings.shell is None
        assert settings.max_sessions == 10
        assert settings.session_timeout == 3600
        assert settings.log_level == "INFO"
        assert settings.token is None

    def test_custom_values(self):
        """Test custom configuration values."""
        settings = Settings(
            host="0.0.0.0",
            port=9000,
            reload=True,
            shell="/bin/zsh",
            max_sessions=5,
            session_timeout=7200,
            log_level="DEBUG",
            token="secret123",
        )
        assert settings.host == "0.0.0.0"
        assert settings.port == 9000
        assert settings.reload is True
        assert settings.shell == "/bin/zsh"
        assert settings.max_sessions == 5
        assert settings.session_timeout == 7200
        assert settings.log_level == "DEBUG"
        assert settings.token == "secret123"

    def test_get_shell_with_custom_shell(self):
        """Test get_shell returns custom shell when set."""
        settings = Settings(shell="/bin/zsh")
        assert settings.get_shell() == "/bin/zsh"

    def test_get_shell_from_env(self):
        """Test get_shell falls back to SHELL env var."""
        settings = Settings(shell=None)
        with patch.dict(os.environ, {"SHELL": "/bin/fish"}):
            assert settings.get_shell() == "/bin/fish"

    def test_get_shell_default(self):
        """Test get_shell defaults to /bin/bash."""
        settings = Settings(shell=None)
        with patch.dict(os.environ, {}, clear=True):
            # Remove SHELL from env
            env = os.environ.copy()
            env.pop("SHELL", None)
            with patch.dict(os.environ, env, clear=True):
                assert settings.get_shell() == "/bin/bash"

    def test_env_prefix(self):
        """Test that environment variables with WEBTERM_ prefix are loaded."""
        with patch.dict(os.environ, {"WEBTERM_PORT": "3000", "WEBTERM_HOST": "0.0.0.0"}):
            settings = Settings()
            assert settings.port == 3000
            assert settings.host == "0.0.0.0"
