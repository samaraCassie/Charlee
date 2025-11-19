"""Notification Listener - Subscribes to Event Bus and creates notifications."""

import logging
from datetime import datetime

from database.config import SessionLocal
from integration.event_bus import EventBus, Event
from integration.event_types import EventType
from services.notification_service import NotificationService
from api.websockets import get_connection_manager

logger = logging.getLogger(__name__)


class NotificationListener:
    """
    Listener that subscribes to Event Bus events and creates notifications.

    Listens to relevant events (task deadlines, capacity warnings, cycle changes, etc.)
    and creates appropriate notifications for users.
    """

    def __init__(self, event_bus: EventBus):
        """
        Initialize notification listener.

        Args:
            event_bus: Event bus instance to subscribe to
        """
        self.event_bus = event_bus
        self.connection_manager = get_connection_manager()

        # Subscribe to relevant events
        self._subscribe_to_events()

        logger.info("NotificationListener initialized and subscribed to events")

    def _subscribe_to_events(self):
        """Subscribe to all relevant event types."""
        # Task events
        self.event_bus.subscribe(
            EventType.TASK_DEADLINE_APPROACHING, self.handle_task_deadline_approaching
        )
        self.event_bus.subscribe(EventType.TASK_OVERDUE, self.handle_task_overdue)

        # Capacity events
        self.event_bus.subscribe(EventType.OVERLOAD_DETECTED, self.handle_overload_detected)
        self.event_bus.subscribe(EventType.CAPACITY_CRITICAL, self.handle_capacity_critical)

        # Wellness events
        self.event_bus.subscribe(EventType.CYCLE_PHASE_CHANGED, self.handle_cycle_phase_changed)

        logger.info("NotificationListener subscribed to all relevant events")

    # ==================== Event Handlers ====================

    async def handle_task_deadline_approaching(self, event: Event):
        """
        Handle TASK_DEADLINE_APPROACHING event.

        Expected payload:
        {
            "user_id": int,
            "task_id": int,
            "task_description": str,
            "deadline": str (ISO format),
            "hours_until_deadline": float
        }
        """
        payload = event.payload
        user_id = payload.get("user_id")
        task_id = payload.get("task_id")
        task_description = payload.get("task_description")
        deadline_str = payload.get("deadline")

        if not all([user_id, task_id, task_description, deadline_str]):
            logger.warning("Missing required fields in TASK_DEADLINE_APPROACHING event")
            return

        try:
            deadline = datetime.fromisoformat(deadline_str)

            # Create notification using service
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                notification = notification_service.send_task_due_soon_notification(
                    user_id=user_id,
                    task_id=task_id,
                    task_description=task_description,
                    deadline=deadline,
                )

                if notification:
                    logger.info(
                        f"Created task deadline notification for user {user_id}",
                        extra={
                            "notification_id": notification.id,
                            "user_id": user_id,
                            "task_id": task_id,
                        },
                    )

                    # Send via WebSocket if user is connected
                    await self._broadcast_notification(user_id, notification)

            finally:
                db.close()

        except Exception as e:
            logger.error(
                f"Error handling TASK_DEADLINE_APPROACHING event: {e}",
                extra={"event": event.to_dict()},
                exc_info=True,
            )

    async def handle_task_overdue(self, event: Event):
        """
        Handle TASK_OVERDUE event.

        Expected payload:
        {
            "user_id": int,
            "task_id": int,
            "task_description": str,
            "deadline": str (ISO format)
        }
        """
        payload = event.payload
        user_id = payload.get("user_id")
        task_id = payload.get("task_id")
        task_description = payload.get("task_description")

        if not all([user_id, task_id, task_description]):
            logger.warning("Missing required fields in TASK_OVERDUE event")
            return

        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                notification = notification_service.send_notification(
                    user_id=user_id,
                    notification_type="task_due_soon",
                    title="Task Overdue!",
                    message=f"'{task_description}' is now overdue. Complete it ASAP.",
                    metadata={
                        "task_id": task_id,
                        "priority": "critical",
                        "action_url": f"/tasks/{task_id}",
                    },
                )

                if notification:
                    logger.info(f"Created task overdue notification for user {user_id}")
                    await self._broadcast_notification(user_id, notification)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling TASK_OVERDUE event: {e}", exc_info=True)

    async def handle_overload_detected(self, event: Event):
        """
        Handle OVERLOAD_DETECTED event.

        Expected payload:
        {
            "user_id": int,
            "current_load_percentage": float,
            "overload_hours": float
        }
        """
        payload = event.payload
        user_id = payload.get("user_id")
        load_percentage = payload.get("current_load_percentage")
        overload_hours = payload.get("overload_hours")

        if not all([user_id is not None, load_percentage is not None, overload_hours is not None]):
            logger.warning("Missing required fields in OVERLOAD_DETECTED event")
            return

        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                notification = notification_service.send_capacity_overload_notification(
                    user_id=user_id,
                    current_load_percentage=load_percentage,
                    overload_hours=overload_hours,
                )

                if notification:
                    logger.info(f"Created capacity overload notification for user {user_id}")
                    await self._broadcast_notification(user_id, notification)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling OVERLOAD_DETECTED event: {e}", exc_info=True)

    async def handle_capacity_critical(self, event: Event):
        """
        Handle CAPACITY_CRITICAL event.

        Expected payload:
        {
            "user_id": int,
            "current_load_percentage": float
        }
        """
        payload = event.payload
        user_id = payload.get("user_id")
        load_percentage = payload.get("current_load_percentage", 100.0)

        if user_id is None:
            logger.warning("Missing user_id in CAPACITY_CRITICAL event")
            return

        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                notification = notification_service.send_notification(
                    user_id=user_id,
                    notification_type="capacity_overload",
                    title="CRITICAL: Capacity Exceeded!",
                    message=f"You're at {load_percentage:.0f}% capacity. Immediate action required!",
                    metadata={
                        "priority": "critical",
                        "load_percentage": load_percentage,
                        "action_url": "/capacity",
                    },
                )

                if notification:
                    logger.info(f"Created critical capacity notification for user {user_id}")
                    await self._broadcast_notification(user_id, notification)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling CAPACITY_CRITICAL event: {e}", exc_info=True)

    async def handle_cycle_phase_changed(self, event: Event):
        """
        Handle CYCLE_PHASE_CHANGED event.

        Expected payload:
        {
            "user_id": int,
            "new_phase": str,
            "old_phase": str,
            "recommendations": list[str] (optional)
        }
        """
        payload = event.payload
        user_id = payload.get("user_id")
        new_phase = payload.get("new_phase")
        recommendations = payload.get("recommendations")

        if not all([user_id, new_phase]):
            logger.warning("Missing required fields in CYCLE_PHASE_CHANGED event")
            return

        try:
            db = SessionLocal()
            try:
                notification_service = NotificationService(db)
                notification = notification_service.send_cycle_phase_change_notification(
                    user_id=user_id,
                    new_phase=new_phase,
                    recommendations=recommendations,
                )

                if notification:
                    logger.info(
                        f"Created cycle phase change notification for user {user_id}",
                        extra={
                            "user_id": user_id,
                            "new_phase": new_phase,
                        },
                    )
                    await self._broadcast_notification(user_id, notification)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling CYCLE_PHASE_CHANGED event: {e}", exc_info=True)

    # ==================== Helper Methods ====================

    async def _broadcast_notification(self, user_id: int, notification):
        """
        Broadcast notification to user via WebSocket if connected.

        Args:
            user_id: User ID
            notification: Notification model instance
        """
        try:
            notification_data = {
                "type": "notification",
                "data": {
                    "id": notification.id,
                    "type": notification.type,
                    "title": notification.title,
                    "message": notification.message,
                    "read": notification.read,
                    "extra_data": notification.extra_data,
                    "created_at": (
                        notification.created_at.isoformat() if notification.created_at else None
                    ),
                },
            }

            await self.connection_manager.send_notification_to_user(user_id, notification_data)

        except Exception as e:
            logger.error(
                f"Error broadcasting notification via WebSocket: {e}",
                extra={
                    "user_id": user_id,
                    "notification_id": notification.id,
                },
                exc_info=True,
            )


def initialize_notification_listener(event_bus: EventBus) -> NotificationListener:
    """
    Initialize and return notification listener.

    Args:
        event_bus: Event bus instance

    Returns:
        NotificationListener instance
    """
    return NotificationListener(event_bus)
