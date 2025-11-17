"""Calendar Event Bus integration.

Publishes calendar-related events to the Event Bus for system-wide notifications
and integrations with other modules like Task Manager and Capacity Guardian.
"""

import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from database.models import CalendarConnection, CalendarConflict, CalendarEvent
from integration.event_bus import Event, EventBus
from integration.event_types import EventType, ModuleName

logger = logging.getLogger(__name__)


class CalendarEventPublisher:
    """Publishes calendar events to the Event Bus."""

    def __init__(self, db_session: Session, event_bus: Optional[EventBus] = None):
        """
        Initialize calendar event publisher.

        Args:
            db_session: SQLAlchemy database session
            event_bus: Event Bus instance (optional, created if not provided)
        """
        self.db = db_session
        self.event_bus = event_bus or EventBus(db_session)

    async def publish_connection_created(self, connection: CalendarConnection) -> int:
        """
        Publish event when calendar is connected.

        Args:
            connection: Calendar connection that was created

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_CONNECTED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "connection_id": connection.id,
                "user_id": connection.user_id,
                "provider": connection.provider,
                "calendar_id": connection.calendar_id,
                "calendar_name": connection.calendar_name,
                "sync_enabled": connection.sync_enabled,
                "sync_direction": connection.sync_direction,
            },
            prioridade=7,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_CONNECTED event",
            extra={"connection_id": connection.id, "provider": connection.provider},
        )
        return event_id

    async def publish_connection_deleted(
        self, connection_id: int, user_id: int, provider: str
    ) -> int:
        """
        Publish event when calendar is disconnected.

        Args:
            connection_id: Calendar connection ID
            user_id: User ID
            provider: Calendar provider

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_DISCONNECTED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "connection_id": connection_id,
                "user_id": user_id,
                "provider": provider,
            },
            prioridade=6,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_DISCONNECTED event",
            extra={"connection_id": connection_id, "provider": provider},
        )
        return event_id

    async def publish_sync_completed(self, connection_id: int, stats: dict[str, Any]) -> int:
        """
        Publish event when calendar sync completes.

        Args:
            connection_id: Calendar connection ID
            stats: Sync statistics

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_SYNCED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "connection_id": connection_id,
                "events_created": stats.get("events_created", 0),
                "events_updated": stats.get("events_updated", 0),
                "events_deleted": stats.get("events_deleted", 0),
                "conflicts_detected": stats.get("conflicts_detected", 0),
            },
            prioridade=5,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_SYNCED event",
            extra={"connection_id": connection_id, "stats": stats},
        )
        return event_id

    async def publish_sync_failed(self, connection_id: int, error_message: str) -> int:
        """
        Publish event when calendar sync fails.

        Args:
            connection_id: Calendar connection ID
            error_message: Error description

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_SYNC_FAILED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "connection_id": connection_id,
                "error_message": error_message,
            },
            prioridade=8,  # High priority for failures
        )

        event_id = await self.event_bus.publish(event)
        logger.warning(
            "Published CALENDAR_SYNC_FAILED event",
            extra={"connection_id": connection_id, "error": error_message},
        )
        return event_id

    async def publish_event_created(self, calendar_event: CalendarEvent) -> int:
        """
        Publish event when calendar event is created.

        Args:
            calendar_event: Calendar event that was created

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_EVENT_CREATED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "event_id": calendar_event.id,
                "connection_id": calendar_event.connection_id,
                "user_id": calendar_event.user_id,
                "task_id": calendar_event.task_id,
                "title": calendar_event.title,
                "start_time": calendar_event.start_time.isoformat(),
                "end_time": calendar_event.end_time.isoformat(),
                "source": calendar_event.source,
            },
            prioridade=6,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_EVENT_CREATED event",
            extra={"event_id": calendar_event.id, "title": calendar_event.title},
        )
        return event_id

    async def publish_event_updated(self, calendar_event: CalendarEvent) -> int:
        """
        Publish event when calendar event is updated.

        Args:
            calendar_event: Calendar event that was updated

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_EVENT_UPDATED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "event_id": calendar_event.id,
                "connection_id": calendar_event.connection_id,
                "user_id": calendar_event.user_id,
                "task_id": calendar_event.task_id,
                "title": calendar_event.title,
                "start_time": calendar_event.start_time.isoformat(),
                "end_time": calendar_event.end_time.isoformat(),
                "source": calendar_event.source,
            },
            prioridade=5,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_EVENT_UPDATED event",
            extra={"event_id": calendar_event.id, "title": calendar_event.title},
        )
        return event_id

    async def publish_event_deleted(self, event_id: int, user_id: int, title: str) -> int:
        """
        Publish event when calendar event is deleted.

        Args:
            event_id: Calendar event ID
            user_id: User ID
            title: Event title

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_EVENT_DELETED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "event_id": event_id,
                "user_id": user_id,
                "title": title,
            },
            prioridade=5,
        )

        db_event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_EVENT_DELETED event",
            extra={"event_id": event_id, "title": title},
        )
        return db_event_id

    async def publish_conflict_detected(self, conflict: CalendarConflict) -> int:
        """
        Publish event when calendar conflict is detected.

        Args:
            conflict: Calendar conflict that was detected

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_CONFLICT_DETECTED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "conflict_id": conflict.id,
                "event_id": conflict.event_id,
                "user_id": conflict.user_id,
                "conflict_type": conflict.conflict_type,
                "resolution_strategy": conflict.resolution_strategy,
            },
            prioridade=8,  # High priority for conflicts
        )

        event_id = await self.event_bus.publish(event)
        logger.warning(
            "Published CALENDAR_CONFLICT_DETECTED event",
            extra={
                "conflict_id": conflict.id,
                "conflict_type": conflict.conflict_type,
            },
        )
        return event_id

    async def publish_conflict_resolved(self, conflict: CalendarConflict) -> int:
        """
        Publish event when calendar conflict is resolved.

        Args:
            conflict: Calendar conflict that was resolved

        Returns:
            Event ID from database
        """
        event = Event(
            tipo=EventType.CALENDAR_CONFLICT_RESOLVED,
            modulo_origem=ModuleName.CALENDAR,
            payload={
                "conflict_id": conflict.id,
                "event_id": conflict.event_id,
                "user_id": conflict.user_id,
                "conflict_type": conflict.conflict_type,
                "resolution_strategy": conflict.resolution_strategy,
                "resolved_by": conflict.resolved_by,
            },
            prioridade=6,
        )

        event_id = await self.event_bus.publish(event)
        logger.info(
            "Published CALENDAR_CONFLICT_RESOLVED event",
            extra={
                "conflict_id": conflict.id,
                "resolved_by": conflict.resolved_by,
            },
        )
        return event_id


def get_calendar_event_publisher(
    db_session: Session, event_bus: Optional[EventBus] = None
) -> CalendarEventPublisher:
    """
    Get calendar event publisher instance.

    Args:
        db_session: SQLAlchemy database session
        event_bus: Optional Event Bus instance

    Returns:
        CalendarEventPublisher instance
    """
    return CalendarEventPublisher(db_session, event_bus)
