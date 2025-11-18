"""Tests for notification API routes."""

import pytest
from fastapi import status

from api.auth.security import create_access_token
from database import crud
from database.schemas import NotificationCreate, NotificationPreferenceCreate


class TestNotificationRoutes:
    """Test cases for notification API routes."""

    @pytest.fixture
    def auth_headers(self, sample_user):
        """Create authentication headers with valid JWT token."""
        access_token = create_access_token(
            data={"user_id": sample_user.id, "username": sample_user.username}
        )
        return {"Authorization": f"Bearer {access_token}"}

    def test_get_notifications(self, client, db, sample_user, auth_headers):
        """Should list all notifications for authenticated user."""
        # Create some notifications
        for i in range(3):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Notification {i}",
                message=f"Message {i}",
            )
            crud.create_notification(db, notification_data)

        response = client.get("/api/v2/notifications/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["notifications"]) == 3
        assert data["unread_count"] == 3

    def test_get_notifications_unread_only(self, client, db, sample_user, auth_headers):
        """Should filter unread notifications."""
        # Create 2 unread, 1 read
        for i in range(2):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Unread {i}",
                message="Unread",
            )
            crud.create_notification(db, notification_data)

        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Read",
            message="Read",
        )
        notif = crud.create_notification(db, notification_data)
        notif.read = True
        db.commit()

        response = client.get(
            "/api/v2/notifications/", params={"unread_only": True}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2

    def test_get_notifications_by_type(self, client, db, sample_user, auth_headers):
        """Should filter notifications by type."""
        # Create different types
        for notif_type in ["task_due_soon", "capacity_overload", "system"]:
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type=notif_type,
                title=notif_type,
                message="Test",
            )
            crud.create_notification(db, notification_data)

        response = client.get(
            "/api/v2/notifications/",
            params={"notification_type": "task_due_soon"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["notifications"][0]["type"] == "task_due_soon"

    def test_get_notifications_pagination(self, client, db, sample_user, auth_headers):
        """Should support pagination."""
        # Create 10 notifications
        for i in range(10):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Notification {i}",
                message="Test",
            )
            crud.create_notification(db, notification_data)

        response = client.get(
            "/api/v2/notifications/", params={"skip": 3, "limit": 5}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["notifications"]) == 5

    def test_get_notification_by_id(self, client, db, sample_user, auth_headers):
        """Should retrieve a single notification by ID."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Test Notification",
            message="Test message",
        )
        notification = crud.create_notification(db, notification_data)

        response = client.get(f"/api/v2/notifications/{notification.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == notification.id
        assert data["title"] == "Test Notification"

    def test_get_notification_not_found(self, client, auth_headers):
        """Should return 404 for non-existent notification."""
        response = client.get("/api/v2/notifications/999", headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_notification_as_read(self, client, db, sample_user, auth_headers):
        """Should mark notification as read."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Unread",
            message="Mark me as read",
        )
        notification = crud.create_notification(db, notification_data)

        response = client.patch(
            f"/api/v2/notifications/{notification.id}/read", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["read"] is True
        assert data["read_at"] is not None

    def test_mark_all_notifications_as_read(self, client, db, sample_user, auth_headers):
        """Should mark all notifications as read."""
        # Create 5 unread notifications
        for i in range(5):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Notification {i}",
                message="Unread",
            )
            crud.create_notification(db, notification_data)

        response = client.post("/api/v2/notifications/mark-all-read", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated_count"] == 5

        # Verify all are read
        response = client.get(
            "/api/v2/notifications/", params={"unread_only": True}, headers=auth_headers
        )
        assert response.json()["total"] == 0

    def test_delete_notification(self, client, db, sample_user, auth_headers):
        """Should delete a notification."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="To Delete",
            message="This will be deleted",
        )
        notification = crud.create_notification(db, notification_data)

        response = client.delete(f"/api/v2/notifications/{notification.id}", headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        response = client.get(f"/api/v2/notifications/{notification.id}", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_notification_preferences(self, client, db, sample_user, auth_headers):
        """Should list all notification preferences."""
        response = client.get("/api/v2/notifications/preferences/", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should auto-create 6 default preferences
        assert data["total"] == 6
        assert len(data["preferences"]) == 6

    def test_get_notification_preference_by_type(self, client, db, sample_user, auth_headers):
        """Should retrieve preference for specific type."""
        # Create preference
        preference_data = NotificationPreferenceCreate(
            notification_type="task_due_soon",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        response = client.get(
            "/api/v2/notifications/preferences/task_due_soon", headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["notification_type"] == "task_due_soon"
        assert data["enabled"] is True

    def test_update_notification_preference(self, client, db, sample_user, auth_headers):
        """Should update notification preference."""
        # Create preference
        preference_data = NotificationPreferenceCreate(
            notification_type="capacity_overload",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        # Update it
        update_data = {
            "enabled": False,
            "email_enabled": True,
        }
        response = client.patch(
            "/api/v2/notifications/preferences/capacity_overload",
            json=update_data,
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["enabled"] is False
        assert data["email_enabled"] is True
        assert data["in_app_enabled"] is True  # Unchanged

    def test_delete_notification_preference(self, client, db, sample_user, auth_headers):
        """Should delete notification preference."""
        # Create preference
        preference_data = NotificationPreferenceCreate(
            notification_type="achievement",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        response = client.delete(
            "/api/v2/notifications/preferences/achievement", headers=auth_headers
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        response = client.get("/api/v2/notifications/preferences/achievement", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_notifications_require_authentication(self, client):
        """Should require authentication for all endpoints."""
        # No auth headers
        response = client.get("/api/v2/notifications/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.post("/api/v2/notifications/mark-all-read")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = client.get("/api/v2/notifications/preferences/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
