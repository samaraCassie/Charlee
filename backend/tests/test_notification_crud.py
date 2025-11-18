"""Tests for notification CRUD operations."""

import pytest
from datetime import datetime, timezone

from database import crud
from database.schemas import (
    NotificationCreate,
    NotificationUpdate,
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
)


class TestNotificationCRUD:
    """Test cases for notification CRUD operations."""

    def test_create_notification(self, db, sample_user):
        """Should create a notification."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="task_due_soon",
            title="Task Due Soon",
            message="Your task is due in 2 hours",
            extra_data={"task_id": 1, "priority": "high"},
        )

        notification = crud.create_notification(db, notification_data)

        assert notification.id is not None
        assert notification.user_id == sample_user.id
        assert notification.type == "task_due_soon"
        assert notification.title == "Task Due Soon"
        assert notification.read is False
        assert notification.extra_data["task_id"] == 1

    def test_get_notification(self, db, sample_user):
        """Should retrieve a notification by ID."""
        # Create notification
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Test",
            message="Test message",
        )
        created = crud.create_notification(db, notification_data)

        # Retrieve it
        notification = crud.get_notification(db, created.id, sample_user.id)

        assert notification is not None
        assert notification.id == created.id
        assert notification.user_id == sample_user.id

    def test_get_notification_wrong_user(self, db, sample_user):
        """Should NOT retrieve notification from another user."""
        # Create notification
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Test",
            message="Test message",
        )
        created = crud.create_notification(db, notification_data)

        # Try to get with wrong user_id
        notification = crud.get_notification(db, created.id, user_id=999)

        assert notification is None

    def test_get_notifications_all(self, db, sample_user):
        """Should retrieve all notifications for a user."""
        # Create multiple notifications
        for i in range(5):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Notification {i}",
                message=f"Message {i}",
            )
            crud.create_notification(db, notification_data)

        notifications = crud.get_notifications(db, sample_user.id)

        assert len(notifications) == 5

    def test_get_notifications_unread_only(self, db, sample_user):
        """Should filter unread notifications."""
        # Create 3 unread, 2 read
        for i in range(3):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Unread {i}",
                message="Unread",
            )
            crud.create_notification(db, notification_data)

        for i in range(2):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Read {i}",
                message="Read",
            )
            notif = crud.create_notification(db, notification_data)
            notif.read = True
            db.commit()

        unread = crud.get_notifications(db, sample_user.id, unread_only=True)

        assert len(unread) == 3

    def test_get_notifications_by_type(self, db, sample_user):
        """Should filter notifications by type."""
        # Create different types
        types = ["task_due_soon", "capacity_overload", "system"]
        for notif_type in types:
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type=notif_type,
                title=f"{notif_type} notification",
                message="Test",
            )
            crud.create_notification(db, notification_data)

        filtered = crud.get_notifications(db, sample_user.id, notification_type="task_due_soon")

        assert len(filtered) == 1
        assert filtered[0].type == "task_due_soon"

    def test_count_unread_notifications(self, db, sample_user):
        """Should count unread notifications correctly."""
        # Create 3 unread, 2 read
        for i in range(3):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Unread {i}",
                message="Unread",
            )
            crud.create_notification(db, notification_data)

        for i in range(2):
            notification_data = NotificationCreate(
                user_id=sample_user.id,
                type="system",
                title=f"Read {i}",
                message="Read",
            )
            notif = crud.create_notification(db, notification_data)
            notif.read = True
            db.commit()

        count = crud.count_unread_notifications(db, sample_user.id)

        assert count == 3

    def test_mark_notification_as_read(self, db, sample_user):
        """Should mark notification as read."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="Test",
            message="Test",
        )
        notification = crud.create_notification(db, notification_data)

        assert notification.read is False
        assert notification.read_at is None

        # Mark as read
        updated = crud.mark_notification_as_read(db, notification.id, sample_user.id)

        assert updated.read is True
        assert updated.read_at is not None

    def test_mark_all_notifications_as_read(self, db, sample_user):
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

        # Mark all as read
        count = crud.mark_all_notifications_as_read(db, sample_user.id)

        assert count == 5

        # Verify all are read
        notifications = crud.get_notifications(db, sample_user.id)
        assert all(n.read for n in notifications)

    def test_delete_notification(self, db, sample_user):
        """Should delete a notification."""
        notification_data = NotificationCreate(
            user_id=sample_user.id,
            type="system",
            title="To Delete",
            message="This will be deleted",
        )
        notification = crud.create_notification(db, notification_data)

        # Delete it
        success = crud.delete_notification(db, notification.id, sample_user.id)

        assert success is True

        # Verify it's gone
        deleted = crud.get_notification(db, notification.id, sample_user.id)
        assert deleted is None


class TestNotificationPreferenceCRUD:
    """Test cases for notification preference CRUD operations."""

    def test_create_notification_preference(self, db, sample_user):
        """Should create a notification preference."""
        preference_data = NotificationPreferenceCreate(
            notification_type="task_due_soon",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )

        preference = crud.create_notification_preference(db, preference_data, sample_user.id)

        assert preference.id is not None
        assert preference.user_id == sample_user.id
        assert preference.notification_type == "task_due_soon"
        assert preference.enabled is True
        assert preference.in_app_enabled is True
        assert preference.email_enabled is False

    def test_get_notification_preference(self, db, sample_user):
        """Should retrieve a notification preference."""
        preference_data = NotificationPreferenceCreate(
            notification_type="capacity_overload",
            enabled=True,
            in_app_enabled=True,
            email_enabled=True,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        preference = crud.get_notification_preference(db, sample_user.id, "capacity_overload")

        assert preference is not None
        assert preference.notification_type == "capacity_overload"
        assert preference.email_enabled is True

    def test_get_notification_preferences(self, db, sample_user):
        """Should retrieve all preferences for a user."""
        types = ["task_due_soon", "capacity_overload", "system"]
        for notif_type in types:
            preference_data = NotificationPreferenceCreate(
                notification_type=notif_type,
                enabled=True,
                in_app_enabled=True,
                email_enabled=False,
                push_enabled=False,
            )
            crud.create_notification_preference(db, preference_data, sample_user.id)

        preferences = crud.get_notification_preferences(db, sample_user.id)

        assert len(preferences) == 3

    def test_update_notification_preference(self, db, sample_user):
        """Should update a notification preference."""
        preference_data = NotificationPreferenceCreate(
            notification_type="system",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        # Update it
        updates = NotificationPreferenceUpdate(
            enabled=False,
            email_enabled=True,
        )
        updated = crud.update_notification_preference(db, "system", updates, sample_user.id)

        assert updated.enabled is False
        assert updated.email_enabled is True
        assert updated.in_app_enabled is True  # Unchanged

    def test_delete_notification_preference(self, db, sample_user):
        """Should delete a notification preference."""
        preference_data = NotificationPreferenceCreate(
            notification_type="achievement",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference_data, sample_user.id)

        # Delete it
        success = crud.delete_notification_preference(db, "achievement", sample_user.id)

        assert success is True

        # Verify it's gone
        deleted = crud.get_notification_preference(db, sample_user.id, "achievement")
        assert deleted is None

    def test_get_or_create_default_preferences(self, db, sample_user):
        """Should create default preferences if they don't exist."""
        preferences = crud.get_or_create_default_preferences(db, sample_user.id)

        # Should have 6 default types
        assert len(preferences) == 6

        # All should be enabled by default
        assert all(p.enabled for p in preferences)
        assert all(p.in_app_enabled for p in preferences)

        # Email and push should be disabled by default
        assert all(not p.email_enabled for p in preferences)
        assert all(not p.push_enabled for p in preferences)

    def test_get_or_create_default_preferences_idempotent(self, db, sample_user):
        """Should not duplicate preferences if they already exist."""
        # Call twice
        preferences1 = crud.get_or_create_default_preferences(db, sample_user.id)
        preferences2 = crud.get_or_create_default_preferences(db, sample_user.id)

        # Should still have only 6
        assert len(preferences1) == 6
        assert len(preferences2) == 6

        # Should be same preferences
        ids1 = {p.id for p in preferences1}
        ids2 = {p.id for p in preferences2}
        assert ids1 == ids2
