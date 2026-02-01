"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient

from webterm.api.app import create_app


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)

    def test_health_returns_healthy(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_returns_session_count(self, client):
        """Test health endpoint returns session count."""
        response = client.get("/health")
        data = response.json()
        assert "sessions" in data
        assert isinstance(data["sessions"], int)

    def test_health_no_auth_required(self, client):
        """Test health endpoint doesn't require authentication."""
        # Even with auth enabled, health should be accessible
        response = client.get("/health")
        assert response.status_code == 200
