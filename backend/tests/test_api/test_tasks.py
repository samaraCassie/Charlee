"""Tests for Tasks API endpoints."""

from fastapi import status
from datetime import date, timedelta


class TestTasksAPI:
    """Test suite for Tasks CRUD operations."""

    def test_create_task(self, client, sample_big_rock):
        """Should create task with valid data."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        response = client.post(
            "/api/v1/tasks",
            json={
                "description": "New test task",
                "type": "task",
                "big_rock_id": sample_big_rock.id,
                "deadline": tomorrow,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data["description"] == "New test task"
        assert data["type"] == "task"
        assert "id" in data

    def test_create_task_invalid_big_rock(self, client):
        """Should return 404 for non-existent Big Rock (now validated)."""
        response = client.post(
            "/api/v1/tasks",
            json={"description": "Test task", "type": "task", "big_rock_id": 9999},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_tasks(self, client, sample_task):
        """Should list all tasks."""
        response = client.get("/api/v1/tasks")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total" in data
        assert "tasks" in data
        assert len(data["tasks"]) >= 1

    def test_list_tasks_with_filters(self, client, sample_task):
        """Should filter tasks by status."""
        response = client.get("/api/v1/tasks?status=pending")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "tasks" in data
        for task in data["tasks"]:
            assert task["status"] == "pending"

    def test_get_task(self, client, sample_task):
        """Should get task by ID."""
        response = client.get(f"/api/v1/tasks/{sample_task.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == sample_task.id
        assert data["description"] == sample_task.description

    def test_update_task(self, client, sample_task):
        """Should update task."""
        response = client.patch(f"/api/v1/tasks/{sample_task.id}", json={"status": "in_progress"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "in_progress"

    def test_delete_task(self, client, sample_task):
        """Should delete task."""
        response = client.delete(f"/api/v1/tasks/{sample_task.id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deletion
        get_response = client.get(f"/api/v1/tasks/{sample_task.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
