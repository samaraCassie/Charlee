"""Tests for Big Rocks API endpoints."""

from fastapi import status


class TestBigRocksAPI:
    """Test suite for Big Rocks CRUD operations."""

    def test_create_big_rock(self, client):
        """Should create Big Rock with valid data."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Career", "color": "#3b82f6", "active": True},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["name"] == "Career"
        assert data["color"] == "#3b82f6"
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data

    def test_create_big_rock_missing_name(self, client):
        """Should return 422 for missing required field."""
        response = client.post("/api/v1/big-rocks", json={"color": "#ff0000"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_big_rocks(self, client, sample_big_rock):
        """Should list all Big Rocks."""
        response = client.get("/api/v1/big-rocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "big_rocks" in data
        assert len(data["big_rocks"]) >= 1
        # Name may be HTML-escaped in response
        assert "Health" in data["big_rocks"][0]["name"]
        assert "Wellness" in data["big_rocks"][0]["name"]

    def test_get_big_rock(self, client, sample_big_rock):
        """Should get Big Rock by ID."""
        response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_big_rock.id
        # Name may be HTML-escaped in response
        assert "Health" in data["name"]
        assert "Wellness" in data["name"]

    def test_get_big_rock_not_found(self, client):
        """Should return 404 for non-existent ID."""
        response = client.get("/api/v1/big-rocks/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_big_rock(self, client, sample_big_rock):
        """Should update Big Rock."""
        response = client.patch(f"/api/v1/big-rocks/{sample_big_rock.id}", json={"name": "Health"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Health"

    def test_delete_big_rock(self, client, sample_big_rock):
        """Should soft delete Big Rock (set active=False)."""
        response = client.delete(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft deletion - should still exist but with active=False
        get_response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["active"] is False
