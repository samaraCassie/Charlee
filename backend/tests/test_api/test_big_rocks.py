"""Tests for Big Rocks API endpoints."""

from fastapi import status


class TestBigRocksAPI:
    """Test suite for Big Rocks CRUD operations."""

    def test_create_big_rock(self, client):
        """Should create Big Rock with valid data."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"nome": "Carreira", "cor": "#3b82f6", "ativo": True},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["nome"] == "Carreira"
        assert data["cor"] == "#3b82f6"
        assert data["ativo"] is True
        assert "id" in data
        assert "criado_em" in data

    def test_create_big_rock_missing_name(self, client):
        """Should return 422 for missing required field."""
        response = client.post("/api/v1/big-rocks", json={"cor": "#ff0000"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_list_big_rocks(self, client, sample_big_rock):
        """Should list all Big Rocks."""
        response = client.get("/api/v1/big-rocks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "big_rocks" in data
        assert len(data["big_rocks"]) >= 1
        assert data["big_rocks"][0]["nome"] == sample_big_rock.nome

    def test_get_big_rock(self, client, sample_big_rock):
        """Should get Big Rock by ID."""
        response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_big_rock.id
        assert data["nome"] == sample_big_rock.nome

    def test_get_big_rock_not_found(self, client):
        """Should return 404 for non-existent ID."""
        response = client.get("/api/v1/big-rocks/9999")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_big_rock(self, client, sample_big_rock):
        """Should update Big Rock."""
        response = client.patch(f"/api/v1/big-rocks/{sample_big_rock.id}", json={"nome": "Saúde"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == "Saúde"

    def test_delete_big_rock(self, client, sample_big_rock):
        """Should soft delete Big Rock (set ativo=False)."""
        response = client.delete(f"/api/v1/big-rocks/{sample_big_rock.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify soft deletion - should still exist but with ativo=False
        get_response = client.get(f"/api/v1/big-rocks/{sample_big_rock.id}")
        assert get_response.status_code == status.HTTP_200_OK
        data = get_response.json()
        assert data["ativo"] is False
