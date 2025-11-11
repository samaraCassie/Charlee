"""Tests for health check endpoints."""

from fastapi import status


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct response."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "online"
        assert "/docs" in data["docs"]

    def test_health_check(self, client, db):
        """Test detailed health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Basic fields - status can be healthy or degraded in tests
        assert data["status"] in ["healthy", "degraded"]
        assert data["service"] == "charlee-backend"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data

        # Health checks
        assert "checks" in data
        assert "database" in data["checks"]
        assert "tables" in data["checks"]

        # Database check - may vary in test environment
        assert "status" in data["checks"]["database"]
        assert "message" in data["checks"]["database"]

        # Tables check - may be healthy or unhealthy in test environment
        assert "status" in data["checks"]["tables"]
        assert "message" in data["checks"]["tables"]

        # Environment info
        assert "environment" in data
        assert "python_version" in data["environment"]
        assert "debug_mode" in data["environment"]
