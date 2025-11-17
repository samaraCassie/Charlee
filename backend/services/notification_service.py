"""Notification service for creating and managing notifications."""

import logging
from datetime import datetime, timezone
from typing import Literal, Optional

from sqlalchemy.orm import Session

from database import crud
from database.models import Notification, NotificationPreference
from database.schemas import NotificationCreate

logger = logging.getLogger(__name__)


# Type for notification types
NotificationType = Literal[
    "task_due_soon",
    "capacity_overload",
    "cycle_phase_change",
    "freelance_invoice_ready",
    "system",
    "achievement",
]


class NotificationService:
    """
    Service for creating and managing notifications.

    Handles checking user preferences, creating notifications,
    and broadcasting them through various channels (in-app, email, WebSocket).
    """

    def __init__(self, db: Session):
        """
        Initialize notification service.

        Args:
            db: Database session
        """
        self.db = db

    def send_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[dict] = None,
    ) -> Optional[Notification]:
        """
        Send a notification to a user.

        Checks user preferences before sending. Only sends if user has
        not disabled this notification type.

        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            metadata: Optional metadata (task_id, priority, action_url, etc.)

        Returns:
            Created Notification if sent, None if user has disabled this type
        """
        # Check if user has notification preferences set
        preference = crud.get_notification_preference(self.db, user_id, notification_type)

        # If no preference, create default (enabled)
        if not preference:
            logger.info(
                f"No preference found for user {user_id}, type {notification_type}. Creating default."
            )
            crud.get_or_create_default_preferences(self.db, user_id)
            preference = crud.get_notification_preference(self.db, user_id, notification_type)

        # Check if notifications are enabled for this type
        if preference and not preference.enabled:
            logger.info(
                f"Notification {notification_type} disabled for user {user_id}. Not sending.",
                extra={
                    "user_id": user_id,
                    "notification_type": notification_type,
                },
            )
            return None

        # Check if in-app notifications are enabled
        if preference and not preference.in_app_enabled:
            logger.info(
                f"In-app notifications disabled for user {user_id}, type {notification_type}",
                extra={
                    "user_id": user_id,
                    "notification_type": notification_type,
                },
            )
            return None

        # Create the notification
        notification_data = NotificationCreate(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            metadata=metadata,
        )

        notification = crud.create_notification(self.db, notification_data)

        logger.info(
            f"Notification created: {notification.id}",
            extra={
                "notification_id": notification.id,
                "user_id": user_id,
                "type": notification_type,
                "title": title,
            },
        )

        # TODO: Send email if email_enabled
        # TODO: Send push notification if push_enabled
        # TODO: Broadcast via WebSocket for real-time delivery

        return notification

    def send_task_due_soon_notification(
        self,
        user_id: int,
        task_id: int,
        task_description: str,
        deadline: datetime,
    ) -> Optional[Notification]:
        """
        Send notification for task approaching deadline.

        Args:
            user_id: User ID
            task_id: Task ID
            task_description: Task description
            deadline: Task deadline

        Returns:
            Created notification or None if disabled
        """
        # Calculate time until deadline
        now = datetime.now(timezone.utc)
        deadline_aware = deadline if deadline.tzinfo else deadline.replace(tzinfo=timezone.utc)
        time_diff = deadline_aware - now
        hours_until = time_diff.total_seconds() / 3600

        if hours_until < 24:
            urgency = "today"
        elif hours_until < 48:
            urgency = "tomorrow"
        else:
            days = int(hours_until / 24)
            urgency = f"in {days} days"

        title = f"Task due {urgency}"
        message = f"'{task_description}' is due {urgency}. Time to wrap it up!"

        metadata = {
            "task_id": task_id,
            "deadline": deadline.isoformat(),
            "priority": "high" if hours_until < 24 else "medium",
            "action_url": f"/tasks/{task_id}",
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="task_due_soon",
            title=title,
            message=message,
            metadata=metadata,
        )

    def send_capacity_overload_notification(
        self,
        user_id: int,
        current_load_percentage: float,
        overload_hours: float,
    ) -> Optional[Notification]:
        """
        Send notification for capacity overload.

        Args:
            user_id: User ID
            current_load_percentage: Current workload percentage
            overload_hours: Hours over capacity

        Returns:
            Created notification or None if disabled
        """
        title = "Capacity Overload Warning"
        message = (
            f"You're at {current_load_percentage:.0f}% capacity - "
            f"{overload_hours:.1f}h over limit. Consider reprioritizing tasks."
        )

        metadata = {
            "priority": "high",
            "load_percentage": current_load_percentage,
            "overload_hours": overload_hours,
            "action_url": "/capacity",
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="capacity_overload",
            title=title,
            message=message,
            metadata=metadata,
        )

    def send_cycle_phase_change_notification(
        self,
        user_id: int,
        new_phase: str,
        recommendations: Optional[list[str]] = None,
    ) -> Optional[Notification]:
        """
        Send notification for menstrual cycle phase change.

        Args:
            user_id: User ID
            new_phase: New cycle phase (menstrual, follicular, ovulation, luteal)
            recommendations: Optional phase-specific recommendations

        Returns:
            Created notification or None if disabled
        """
        phase_names = {
            "menstrual": "Menstrual Phase",
            "follicular": "Follicular Phase",
            "ovulation": "Ovulation Phase",
            "luteal": "Luteal Phase",
        }

        title = f"Cycle Phase: {phase_names.get(new_phase, new_phase.title())}"
        message = f"You've entered the {phase_names.get(new_phase, new_phase)} of your cycle."

        if recommendations:
            message += f" Recommendations: {', '.join(recommendations[:3])}"

        metadata = {
            "phase": new_phase,
            "priority": "low",
            "recommendations": recommendations,
            "action_url": "/wellness",
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="cycle_phase_change",
            title=title,
            message=message,
            metadata=metadata,
        )

    def send_freelance_invoice_ready_notification(
        self,
        user_id: int,
        opportunity_id: int,
        client_name: str,
        invoice_amount: float,
    ) -> Optional[Notification]:
        """
        Send notification for ready freelance invoice.

        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            client_name: Client name
            invoice_amount: Invoice amount

        Returns:
            Created notification or None if disabled
        """
        title = "Invoice Ready"
        message = f"Invoice for {client_name} (R$ {invoice_amount:,.2f}) is ready to send"

        metadata = {
            "opportunity_id": opportunity_id,
            "priority": "medium",
            "client_name": client_name,
            "invoice_amount": invoice_amount,
            "action_url": f"/freelance/opportunities/{opportunity_id}",
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="freelance_invoice_ready",
            title=title,
            message=message,
            metadata=metadata,
        )

    def send_system_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        priority: str = "low",
    ) -> Optional[Notification]:
        """
        Send generic system notification.

        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            priority: Priority level (low, medium, high, critical)

        Returns:
            Created notification or None if disabled
        """
        metadata = {
            "priority": priority,
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="system",
            title=title,
            message=message,
            metadata=metadata,
        )

    def send_achievement_notification(
        self,
        user_id: int,
        achievement_title: str,
        achievement_description: str,
    ) -> Optional[Notification]:
        """
        Send achievement/gamification notification.

        Args:
            user_id: User ID
            achievement_title: Achievement name
            achievement_description: Description of achievement

        Returns:
            Created notification or None if disabled
        """
        title = f"Achievement Unlocked: {achievement_title}"
        message = achievement_description

        metadata = {
            "priority": "low",
            "achievement": achievement_title,
        }

        return self.send_notification(
            user_id=user_id,
            notification_type="achievement",
            title=title,
            message=message,
            metadata=metadata,
        )


def get_notification_service(db: Session) -> NotificationService:
    """
    Factory function to get notification service instance.

    Args:
        db: Database session

    Returns:
        NotificationService instance
    """
    return NotificationService(db)
