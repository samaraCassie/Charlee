"""Tests for Big Rocks API endpoints."""

from fastapi import status


class TestBigRocksAPI:
    """Test suite for Big Rocks CRUD operations."""

    def test_create_big_rock(self, client, auth_headers):
        """Should create Big Rock with valid data."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Career", "color": "#3b82f6", "active": True},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["name"] == "Career"
        assert data["color"] == "#3b82f6"
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_big_rock_missing_name(self, client, auth_headers):
        """Should return 422 for missing required field."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"color": "#ff0000"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_big_rock_without_auth(self, client):
        """Should return 403 without authentication."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Career", "color": "#3b82f6"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_big_rocks(self, client, sample_big_rock, auth_headers):
        """Should list all Big Rocks for authenticated user."""
        response = client.get("/api/v1/big-rocks", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "big_rocks" in data
        assert len(data["big_rocks"]) >= 1
        # Name may be HTML-escaped in response
        assert "Health" in data["big_rocks"][0]["name"]
        assert "Wellness" in data["big_rocks"][0]["name"]

    def test_get_big_rock(self, client, sample_big_rock, auth_headers):
        """Should get Big Rock by ID for authenticated user."""
        response = client.get(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_big_rock.id
        # Name may be HTML-escaped in response
        assert "Health" in data["name"]
        assert "Wellness" in data["name"]

    def test_get_big_rock_not_found(self, client, auth_headers):
        """Should return 404 for non-existent ID."""
        response = client.get("/api/v1/big-rocks/9999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_big_rock(self, client, sample_big_rock, auth_headers):
        """Should update Big Rock for authenticated user."""
        response = client.patch(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            json={"name": "Health"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Health"

    def test_delete_big_rock(self, client, sample_big_rock, auth_headers):
        """Should soft delete Big Rock (set active=False) for authenticated user."""
        response = client.delete(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft deletion - should still exist but with active=False
        get_response = client.get(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["active"] is False
