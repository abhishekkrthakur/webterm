"""Shared test fixtures."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from webterm.api.app import create_app
from webterm.core.config import Settings


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    return create_app()


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def settings_no_auth():
    """Settings with authentication disabled."""
    return Settings(token=None)


@pytest.fixture
def settings_with_auth():
    """Settings with authentication enabled."""
    return Settings(token="test-secret-token")


@pytest.fixture
def auth_client(app):
    """Create a test client with auth token set."""
    with patch("webterm.core.config.settings") as mock_settings:
        mock_settings.token = "test-secret-token"
        client = TestClient(app)
        # Login to get cookie
        client.post("/auth/login", json={"token": "test-secret-token"})
        yield client


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing."""
    # Create some test files
    (temp_dir / "file1.txt").write_text("Hello World")
    (temp_dir / "file2.py").write_text("print('test')")
    (temp_dir / "subdir").mkdir()
    (temp_dir / "subdir" / "nested.txt").write_text("Nested content")
    return temp_dir
