"""Edge case tests for API robustness."""

from datetime import date, timedelta

from fastapi import status


class TestBigRockEdgeCases:
    """Edge case tests for Big Rocks API."""

    def test_create_big_rock_with_unicode_name(self, client, auth_headers):
        """Should handle Unicode characters in name."""
        response = client.post(
            "/api/v1/big-rocks",
            json={
                "name": "健康 & 🌱 Wellness",
                "color": "#00ff00",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "健康" in data["name"]
        assert "Wellness" in data["name"]

    def test_create_big_rock_with_max_length_name(self, client, auth_headers):
        """Should accept name at maximum length (100 chars)."""
        long_name = "A" * 100
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": long_name, "color": "#123456"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_big_rock_with_special_characters(self, client, auth_headers):
        """Should handle special characters safely."""
        response = client.post(
            "/api/v1/big-rocks",
            json={
                "name": "Health & Wellness <test>",
                "color": "#ffffff",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Should be HTML escaped
        assert "&lt;" in data["name"] or "<" not in data["name"]

    def test_create_big_rock_with_null_color(self, client, auth_headers):
        """Should accept null color."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Test Rock", "color": None},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["color"] is None

    def test_update_big_rock_with_empty_payload(self, client, sample_big_rock, auth_headers):
        """Should handle empty update payload."""
        response = client.patch(
            f"/api/v1/big-rocks/{sample_big_rock.id}",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK


class TestTaskEdgeCases:
    """Edge case tests for Tasks API."""

    def test_create_task_with_very_long_description(self, client, auth_headers):
        """Should handle very long descriptions (up to 5000 chars)."""
        long_description = "A" * 5000
        response = client.post(
            "/api/v1/tasks",
            json={
                "description": long_description,
                "type": "task",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_task_with_newlines(self, client, auth_headers):
        """Should preserve newlines in description."""
        description = "Line 1\nLine 2\nLine 3"
        response = client.post(
            "/api/v1/tasks",
            json={
                "description": description,
                "type": "task",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Newlines should be present (or escaped)
        assert "Line 1" in data["description"]
        assert "Line 2" in data["description"]

    def test_create_task_with_past_deadline(self, client, auth_headers):
        """Should accept past deadlines (no business logic validation)."""
        past_date = (date.today() - timedelta(days=30)).isoformat()
        response = client.post(
            "/api/v1/tasks",
            json={
                "description": "Past deadline task",
                "type": "task",
                "deadline": past_date,
            },
            headers=auth_headers,
        )
        # Should succeed - business logic doesn't prevent past dates
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_task_with_far_future_deadline(self, client, auth_headers):
        """Should accept very far future deadlines."""
        future_date = (date.today() + timedelta(days=3650)).isoformat()  # 10 years
        response = client.post(
            "/api/v1/tasks",
            json={
                "description": "Far future task",
                "type": "task",
                "deadline": future_date,
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_list_tasks_with_large_limit(self, client, sample_task, auth_headers):
        """Should handle large limit values gracefully."""
        response = client.get("/api/v1/tasks?limit=10000", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "tasks" in data

    def test_list_tasks_with_large_skip(self, client, auth_headers):
        """Should handle large skip values without error."""
        response = client.get("/api/v1/tasks?skip=100000", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0  # No tasks at that offset

    def test_update_nonexistent_task(self, client, auth_headers):
        """Should return 404 for nonexistent task update."""
        response = client.patch(
            "/api/v1/tasks/99999",
            json={"description": "Updated"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_already_completed_task(self, client, sample_task, auth_headers):
        """Should handle completing an already completed task."""
        # First completion
        client.post(f"/api/v1/tasks/{sample_task.id}/complete", headers=auth_headers)

        # Second completion
        response = client.post(f"/api/v1/tasks/{sample_task.id}/complete", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

    def test_reopen_pending_task(self, client, sample_task, auth_headers):
        """Should handle reopening a task that isn't completed."""
        response = client.post(f"/api/v1/tasks/{sample_task.id}/reopen", headers=auth_headers)
        # Should succeed even if not completed
        assert response.status_code == status.HTTP_200_OK


class TestConcurrencyEdgeCases:
    """Edge case tests for concurrent operations."""

    def test_create_multiple_big_rocks_same_name(self, client, auth_headers):
        """Should allow multiple Big Rocks with same name."""
        big_rock_data = {"name": "Duplicate Name", "color": "#111111"}

        response1 = client.post("/api/v1/big-rocks", json=big_rock_data, headers=auth_headers)
        response2 = client.post("/api/v1/big-rocks", json=big_rock_data, headers=auth_headers)

        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response1.json()["id"] != response2.json()["id"]

    def test_delete_same_task_twice(self, client, sample_task, auth_headers):
        """Should handle double deletion gracefully."""
        # First deletion
        response1 = client.delete(f"/api/v1/tasks/{sample_task.id}", headers=auth_headers)
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        # Second deletion should fail
        response2 = client.delete(f"/api/v1/tasks/{sample_task.id}", headers=auth_headers)
        assert response2.status_code == status.HTTP_404_NOT_FOUND


class TestInputBoundaryConditions:
    """Tests for input boundary conditions."""

    def test_create_task_with_empty_string_description(self, client, auth_headers):
        """Should reject empty description."""
        response = client.post(
            "/api/v1/tasks",
            json={"description": "", "type": "task"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_task_with_whitespace_only_description(self, client, auth_headers):
        """Should reject whitespace-only description."""
        response = client.post(
            "/api/v1/tasks",
            json={"description": "   ", "type": "task"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_big_rock_with_invalid_color_format(self, client, auth_headers):
        """Should reject invalid color formats."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Test", "color": "not-a-color"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_big_rock_with_hex_without_hash(self, client, auth_headers):
        """Should reject hex color without # prefix."""
        response = client.post(
            "/api/v1/big-rocks",
            json={"name": "Test", "color": "123456"},
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
