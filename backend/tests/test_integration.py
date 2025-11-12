"""Integration tests for complete workflows."""

from fastapi import status
from datetime import date, timedelta


class TestBigRockTaskWorkflow:
    """Integration tests for Big Rock and Task workflows."""

    def test_complete_big_rock_workflow(self, client, auth_headers):
        """Test complete workflow: create Big Rock, create Task, complete Task."""
        # Step 1: Create a Big Rock
        big_rock_response = client.post(
            "/api/v1/big-rocks",
            json={
                "name": "Health & Fitness",
                "color": "#22c55e",
                "active": True,
            },
            headers=auth_headers,
        )
        assert big_rock_response.status_code == status.HTTP_201_CREATED
        big_rock = big_rock_response.json()
        big_rock_id = big_rock["id"]

        # Step 2: Create a Task associated with the Big Rock
        task_response = client.post(
            "/api/v1/tasks",
            json={
                "description": "Morning run - 5km",
                "type": "task",
                "big_rock_id": big_rock_id,
                "deadline": (date.today() + timedelta(days=1)).isoformat(),
            },
            headers=auth_headers,
        )
        assert task_response.status_code == status.HTTP_201_CREATED
        task = task_response.json()
        task_id = task["id"]
        assert task["status"] == "pending"
        assert task["big_rock"]["id"] == big_rock_id

        # Step 3: Complete the Task
        complete_response = client.post(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
        assert complete_response.status_code == status.HTTP_200_OK
        completed_task = complete_response.json()
        assert completed_task["status"] == "completed"
        assert completed_task["completed_at"] is not None

        # Step 4: Verify Task shows up in filtered list
        list_response = client.get(
            "/api/v1/tasks", params={"status": "completed", "big_rock_id": big_rock_id}, headers=auth_headers
        )
        assert list_response.status_code == status.HTTP_200_OK
        tasks_data = list_response.json()
        assert tasks_data["total"] >= 1
        assert any(t["id"] == task_id for t in tasks_data["tasks"])

        # Step 5: Reopen the Task
        reopen_response = client.post(f"/api/v1/tasks/{task_id}/reopen", headers=auth_headers)
        assert reopen_response.status_code == status.HTTP_200_OK
        reopened_task = reopen_response.json()
        assert reopened_task["status"] == "pending"

        # Step 6: Delete the Task
        delete_task_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert delete_task_response.status_code == status.HTTP_204_NO_CONTENT

        # Step 7: Verify Task is gone
        get_task_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert get_task_response.status_code == status.HTTP_404_NOT_FOUND

        # Step 8: Delete the Big Rock
        delete_big_rock_response = client.delete(f"/api/v1/big-rocks/{big_rock_id}", headers=auth_headers)
        assert delete_big_rock_response.status_code == status.HTTP_204_NO_CONTENT

    def test_create_multiple_tasks_for_big_rock(self, client, auth_headers):
        """Test creating multiple tasks for a single Big Rock."""
        # Create Big Rock
        big_rock_response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Career", "color": "#3b82f6"},
            headers=auth_headers,
        )
        big_rock_id = big_rock_response.json()["id"]

        # Create 3 tasks
        task_ids = []
        for i in range(3):
            task_response = client.post(
                "/api/v1/tasks",
                json={
                    "description": f"Career task {i+1}",
                    "type": "task",
                    "big_rock_id": big_rock_id,
                },
                headers=auth_headers,
            )
            assert task_response.status_code == status.HTTP_201_CREATED
            task_ids.append(task_response.json()["id"])

        # Get all tasks for this Big Rock
        list_response = client.get("/api/v1/tasks", params={"big_rock_id": big_rock_id}, headers=auth_headers)
        tasks_data = list_response.json()
        assert tasks_data["total"] == 3

        # Complete all tasks
        for task_id in task_ids:
            complete_response = client.post(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
            assert complete_response.status_code == status.HTTP_200_OK

        # Verify all completed
        completed_list = client.get(
            "/api/v1/tasks", params={"big_rock_id": big_rock_id, "status": "completed"}, headers=auth_headers
        )
        assert completed_list.json()["total"] == 3


class TestErrorHandlingWorkflow:
    """Integration tests for error handling scenarios."""

    def test_create_task_with_invalid_big_rock(self, client, auth_headers):
        """Test creating a task with non-existent Big Rock."""
        response = client.post(
            "/api/v1/tasks",
            json={
                "description": "Orphan task",
                "type": "task",
                "big_rock_id": 99999,
            },
            headers=auth_headers,
        )
        # Should return 404 due to validation
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_update_nonexistent_big_rock(self, client, auth_headers):
        """Test updating a non-existent Big Rock."""
        response = client.patch(
            "/api/v1/big-rocks/99999",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_task(self, client, auth_headers):
        """Test deleting a non-existent Task."""
        response = client.delete("/api/v1/tasks/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPaginationWorkflow:
    """Integration tests for pagination."""

    def test_pagination_with_multiple_tasks(self, client, sample_big_rock, auth_headers):
        """Test pagination when creating many tasks."""
        # Create 15 tasks
        for i in range(15):
            client.post(
                "/api/v1/tasks",
                json={
                    "description": f"Task {i+1}",
                    "type": "task",
                    "big_rock_id": sample_big_rock.id,
                },
                headers=auth_headers,
            )

        # Get first page (limit 10)
        page1 = client.get("/api/v1/tasks", params={"limit": 10, "skip": 0}, headers=auth_headers)
        assert page1.status_code == status.HTTP_200_OK
        page1_data = page1.json()
        assert len(page1_data["tasks"]) == 10

        # Get second page
        page2 = client.get("/api/v1/tasks", params={"limit": 10, "skip": 10}, headers=auth_headers)
        assert page2.status_code == status.HTTP_200_OK
        page2_data = page2.json()
        assert len(page2_data["tasks"]) >= 5

        # Verify no overlap
        page1_ids = {t["id"] for t in page1_data["tasks"]}
        page2_ids = {t["id"] for t in page2_data["tasks"]}
        assert len(page1_ids & page2_ids) == 0  # No intersection


class TestHealthAndMetrics:
    """Integration tests for health check and metrics."""

    def test_health_endpoint_returns_details(self, client, db):
        """Test health endpoint returns detailed status."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "environment" in data

    def test_metrics_endpoint_exists(self, client):
        """Test Prometheus metrics endpoint exists."""
        response = client.get("/metrics")
        assert response.status_code == status.HTTP_200_OK
        # Should contain Prometheus metrics format
        assert "# HELP" in response.text or "# TYPE" in response.text

    def test_root_endpoint_returns_api_info(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "version" in data
        assert "status" in data
        assert data["status"] == "online"
        assert "docs" in data


class TestResponseHeaders:
    """Integration tests for response headers."""

    def test_request_id_header_present(self, client):
        """Test X-Request-ID header is present in responses."""
        response = client.get("/")
        assert "X-Request-ID" in response.headers
        # Should be a UUID format
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) == 36  # UUID format

    def test_response_time_header_present(self, client):
        """Test X-Response-Time header is present in responses."""
        response = client.get("/")
        assert "X-Response-Time" in response.headers
        # Should end with 'ms'
        assert response.headers["X-Response-Time"].endswith("ms")


class TestConcurrentOperations:
    """Integration tests for concurrent operations."""

    def test_create_and_delete_race_condition(self, client, auth_headers):
        """Test creating and deleting in quick succession."""
        # Create task
        create_response = client.post(
            "/api/v1/tasks",
            json={"description": "Quick task", "type": "task"},
            headers=auth_headers,
        )
        task_id = create_response.json()["id"]

        # Delete immediately
        delete_response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Try to get - should be 404
        get_response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_multiple_updates_same_task(self, client, sample_task, auth_headers):
        """Test multiple updates to the same task."""
        updates = [
            {"description": "Updated 1"},
            {"description": "Updated 2"},
            {"description": "Updated 3"},
        ]

        for update in updates:
            response = client.patch(f"/api/v1/tasks/{sample_task.id}", json=update, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

        # Get final state
        final_response = client.get(f"/api/v1/tasks/{sample_task.id}", headers=auth_headers)
        final_task = final_response.json()
        assert "Updated 3" in final_task["description"]
