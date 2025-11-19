"""Tests for notification service."""

from datetime import datetime, timezone, timedelta

from services.notification_service import NotificationService
from database import crud
from database.schemas import NotificationPreferenceCreate


class TestNotificationService:
    """Test cases for NotificationService."""

    def test_send_notification_with_enabled_preference(self, db, sample_user):
        """Should send notification when preference is enabled."""
        service = NotificationService(db)

        # Create preference
        preference = NotificationPreferenceCreate(
            notification_type="task_due_soon",
            enabled=True,
            in_app_enabled=True,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference, sample_user.id)

        # Send notification
        notification = service.send_notification(
            user_id=sample_user.id,
            notification_type="task_due_soon",
            title="Test Notification",
            message="This is a test",
            extra_data={"priority": "high"},
        )

        assert notification is not None
        assert notification.user_id == sample_user.id
        assert notification.type == "task_due_soon"
        assert notification.title == "Test Notification"
        assert notification.message == "This is a test"
        assert notification.extra_data["priority"] == "high"
        assert notification.read is False

    def test_send_notification_with_disabled_preference(self, db, sample_user):
        """Should NOT send notification when preference is disabled."""
        service = NotificationService(db)

        # Create disabled preference
        preference = NotificationPreferenceCreate(
            notification_type="task_due_soon",
            enabled=False,
            in_app_enabled=False,
            email_enabled=False,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference, sample_user.id)

        # Try to send notification
        notification = service.send_notification(
            user_id=sample_user.id,
            notification_type="task_due_soon",
            title="Test Notification",
            message="This should not be sent",
        )

        assert notification is None

    def test_send_notification_creates_default_preference(self, db, sample_user):
        """Should create default preference if none exists."""
        service = NotificationService(db)

        # Send notification without existing preference
        notification = service.send_notification(
            user_id=sample_user.id,
            notification_type="system",
            title="System Notification",
            message="Test message",
        )

        assert notification is not None

        # Check that preference was created
        preference = crud.get_notification_preference(db, sample_user.id, "system")
        assert preference is not None
        assert preference.enabled is True
        assert preference.in_app_enabled is True

    def test_send_task_due_soon_notification(self, db, sample_user):
        """Should send task due soon notification with correct format."""
        service = NotificationService(db)
        deadline = datetime.now(timezone.utc) + timedelta(hours=12)

        notification = service.send_task_due_soon_notification(
            user_id=sample_user.id,
            task_id=1,
            task_description="Complete project report",
            deadline=deadline,
        )

        assert notification is not None
        assert notification.type == "task_due_soon"
        assert "today" in notification.title.lower()
        assert "Complete project report" in notification.message
        assert notification.extra_data["task_id"] == 1
        assert notification.extra_data["priority"] == "high"
        assert "/tasks/1" in notification.extra_data["action_url"]

    def test_send_task_due_soon_tomorrow(self, db, sample_user):
        """Should format message correctly for tomorrow deadline."""
        service = NotificationService(db)
        deadline = datetime.now(timezone.utc) + timedelta(hours=36)

        notification = service.send_task_due_soon_notification(
            user_id=sample_user.id,
            task_id=2,
            task_description="Review code",
            deadline=deadline,
        )

        assert notification is not None
        assert "tomorrow" in notification.title.lower()
        assert notification.extra_data["priority"] == "medium"

    def test_send_capacity_overload_notification(self, db, sample_user):
        """Should send capacity overload notification."""
        service = NotificationService(db)

        notification = service.send_capacity_overload_notification(
            user_id=sample_user.id,
            current_load_percentage=120.0,
            overload_hours=8.5,
        )

        assert notification is not None
        assert notification.type == "capacity_overload"
        assert "120%" in notification.message
        assert "8.5" in notification.message
        assert notification.extra_data["priority"] == "high"
        assert notification.extra_data["load_percentage"] == 120.0

    def test_send_cycle_phase_change_notification(self, db, sample_user):
        """Should send cycle phase change notification."""
        service = NotificationService(db)

        notification = service.send_cycle_phase_change_notification(
            user_id=sample_user.id,
            new_phase="follicular",
            recommendations=["Light exercise", "Social activities", "Creative work"],
        )

        assert notification is not None
        assert notification.type == "cycle_phase_change"
        assert "Follicular Phase" in notification.title
        assert notification.extra_data["phase"] == "follicular"
        assert notification.extra_data["priority"] == "low"
        assert len(notification.extra_data["recommendations"]) == 3

    def test_send_freelance_invoice_ready_notification(self, db, sample_user):
        """Should send freelance invoice ready notification."""
        service = NotificationService(db)

        notification = service.send_freelance_invoice_ready_notification(
            user_id=sample_user.id,
            opportunity_id=5,
            client_name="Acme Corp",
            invoice_amount=5000.00,
        )

        assert notification is not None
        assert notification.type == "freelance_invoice_ready"
        assert "Acme Corp" in notification.message
        assert "5,000.00" in notification.message
        assert notification.extra_data["opportunity_id"] == 5
        assert notification.extra_data["invoice_amount"] == 5000.00

    def test_send_system_notification(self, db, sample_user):
        """Should send system notification."""
        service = NotificationService(db)

        notification = service.send_system_notification(
            user_id=sample_user.id,
            title="System Maintenance",
            message="System will be down for maintenance",
            priority="high",
        )

        assert notification is not None
        assert notification.type == "system"
        assert notification.title == "System Maintenance"
        assert notification.extra_data["priority"] == "high"

    def test_send_achievement_notification(self, db, sample_user):
        """Should send achievement notification."""
        service = NotificationService(db)

        notification = service.send_achievement_notification(
            user_id=sample_user.id,
            achievement_title="Week Streak",
            achievement_description="You completed 7 days in a row!",
        )

        assert notification is not None
        assert notification.type == "achievement"
        assert "Week Streak" in notification.title
        assert notification.extra_data["priority"] == "low"
        assert notification.extra_data["achievement"] == "Week Streak"

    def test_notification_with_disabled_in_app(self, db, sample_user):
        """Should NOT send notification when in_app is disabled."""
        service = NotificationService(db)

        # Create preference with in_app disabled
        preference = NotificationPreferenceCreate(
            notification_type="system",
            enabled=True,
            in_app_enabled=False,  # Disabled
            email_enabled=True,
            push_enabled=False,
        )
        crud.create_notification_preference(db, preference, sample_user.id)

        notification = service.send_notification(
            user_id=sample_user.id,
            notification_type="system",
            title="Test",
            message="Should not be sent",
        )

        assert notification is None
