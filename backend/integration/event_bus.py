"""Event Bus - Pub/Sub system for inter-module communication."""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional

from redis import Redis
from sqlalchemy.orm import Session

from database.models import SystemEvent
from integration.event_types import EventType, ModuleName

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Event data structure for the Event Bus."""

    tipo: EventType
    modulo_origem: ModuleName
    payload: Dict[str, Any]
    prioridade: int = 5
    timestamp: Optional[str] = field(default=None)

    def __post_init__(self):
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "tipo": self.tipo.value if isinstance(self.tipo, EventType) else self.tipo,
            "modulo_origem": (
                self.modulo_origem.value
                if isinstance(self.modulo_origem, ModuleName)
                else self.modulo_origem
            ),
            "payload": self.payload,
            "prioridade": self.prioridade,
            "timestamp": self.timestamp,
        }


class EventBus:
    """
    Event Bus for inter-module communication.

    Provides pub/sub architecture allowing modules to communicate
    asynchronously without tight coupling.
    """

    def __init__(self, db_session: Session, redis_client: Optional[Redis] = None):
        """
        Initialize Event Bus.

        Args:
            db_session: SQLAlchemy database session
            redis_client: Optional Redis client for real-time pub/sub
        """
        self.db = db_session
        self.redis = redis_client
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task: Optional[asyncio.Task] = None
        self._is_running = False

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)
        logger.info(f"📡 {handler.__name__} subscribed to {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self.subscribers and handler in self.subscribers[event_type]:
            self.subscribers[event_type].remove(handler)
            logger.info(f"📡 {handler.__name__} unsubscribed from {event_type.value}")

    async def publish(self, event: Event) -> int:
        """
        Publish an event to the bus.

        Args:
            event: Event to publish

        Returns:
            Event ID from database
        """
        try:
            # Save to database
            db_event = SystemEvent(
                tipo=(event.tipo.value if isinstance(event.tipo, EventType) else event.tipo),
                modulo_origem=(
                    event.modulo_origem.value
                    if isinstance(event.modulo_origem, ModuleName)
                    else event.modulo_origem
                ),
                payload=event.payload,
                prioridade=event.prioridade,
            )

            self.db.add(db_event)
            self.db.commit()
            self.db.refresh(db_event)

            event_id = db_event.id

            # Publish to Redis for real-time processing (if available)
            if self.redis:
                try:
                    channel = f"charlee:events:{event.tipo.value if isinstance(event.tipo, EventType) else event.tipo}"
                    message = {
                        "id": event_id,
                        "payload": event.payload,
                        "timestamp": event.timestamp,
                    }
                    self.redis.publish(channel, json.dumps(message))
                except Exception as e:
                    logger.warning(f"Failed to publish to Redis: {e}")

            # Add to processing queue
            await self.event_queue.put(event)

            logger.info(
                f"📤 Event published: {event.tipo.value if isinstance(event.tipo, EventType) else event.tipo} "
                f"from {event.modulo_origem.value if isinstance(event.modulo_origem, ModuleName) else event.modulo_origem} "
                f"(ID: {event_id})"
            )

            return event_id

        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            self.db.rollback()
            raise

    async def process_events(self) -> None:
        """Event processing loop - runs continuously to process queued events."""
        logger.info("🔄 Event Bus processing started")
        self._is_running = True

        while self._is_running:
            try:
                # Get event from queue
                event = await self.event_queue.get()

                # Get event type
                event_type = (
                    event.tipo if isinstance(event.tipo, EventType) else EventType(event.tipo)
                )

                # Notify subscribers
                if event_type in self.subscribers:
                    for handler in self.subscribers[event_type]:
                        try:
                            # Execute handler (async or sync)
                            if asyncio.iscoroutinefunction(handler):
                                await handler(event)
                            else:
                                handler(event)
                        except Exception as e:
                            logger.error(f"Error in event handler {handler.__name__}: {e}")

                # Mark as processed in database
                self.db.query(SystemEvent).filter(
                    SystemEvent.tipo
                    == (event.tipo.value if isinstance(event.tipo, EventType) else event.tipo),
                    SystemEvent.modulo_origem
                    == (
                        event.modulo_origem.value
                        if isinstance(event.modulo_origem, ModuleName)
                        else event.modulo_origem
                    ),
                    SystemEvent.criado_em == event.timestamp,
                    not SystemEvent.processado,
                ).update({"processado": True, "processado_em": datetime.now(timezone.utc)})

                self.db.commit()

                # Mark task as done
                self.event_queue.task_done()

            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self.db.rollback()

    def start_processing(self) -> None:
        """Start the event processing loop."""
        if not self._processing_task or self._processing_task.done():
            self._processing_task = asyncio.create_task(self.process_events())
            logger.info("✅ Event Bus processing started")

    async def stop_processing(self) -> None:
        """Stop the event processing loop."""
        self._is_running = False

        if self._processing_task:
            # Wait for current event to finish processing
            await self.event_queue.join()
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        logger.info("🛑 Event Bus processing stopped")

    def get_recent_events(
        self, event_type: Optional[EventType] = None, limit: int = 50
    ) -> List[SystemEvent]:
        """
        Get recent events from database.

        Args:
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return

        Returns:
            List of SystemEvent objects
        """
        query = self.db.query(SystemEvent)

        if event_type:
            query = query.filter(SystemEvent.tipo == event_type.value)

        events = (
            query.order_by(SystemEvent.prioridade.desc(), SystemEvent.criado_em.desc())
            .limit(limit)
            .all()
        )

        return events

    def get_unprocessed_events(self, limit: int = 100) -> List[SystemEvent]:
        """
        Get unprocessed events.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of unprocessed SystemEvent objects
        """
        events = (
            self.db.query(SystemEvent)
            .filter(not SystemEvent.processado)
            .order_by(SystemEvent.prioridade.desc(), SystemEvent.criado_em)
            .limit(limit)
            .all()
        )

        return events

    def get_event_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get event statistics.

        Args:
            hours: Time window in hours

        Returns:
            Dictionary with event statistics
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        total_events = (
            self.db.query(SystemEvent).filter(SystemEvent.criado_em >= cutoff_time).count()
        )

        processed_events = (
            self.db.query(SystemEvent)
            .filter(SystemEvent.criado_em >= cutoff_time, SystemEvent.processado)
            .count()
        )

        unprocessed_events = (
            self.db.query(SystemEvent)
            .filter(SystemEvent.criado_em >= cutoff_time, not SystemEvent.processado)
            .count()
        )

        # Events by type
        from sqlalchemy import func

        events_by_type = (
            self.db.query(SystemEvent.tipo, func.count(SystemEvent.id))
            .filter(SystemEvent.criado_em >= cutoff_time)
            .group_by(SystemEvent.tipo)
            .all()
        )

        # Events by module
        events_by_module = (
            self.db.query(SystemEvent.modulo_origem, func.count(SystemEvent.id))
            .filter(SystemEvent.criado_em >= cutoff_time)
            .group_by(SystemEvent.modulo_origem)
            .all()
        )

        return {
            "time_window_hours": hours,
            "total_events": total_events,
            "processed_events": processed_events,
            "unprocessed_events": unprocessed_events,
            "processing_rate": ((processed_events / total_events * 100) if total_events > 0 else 0),
            "events_by_type": dict(events_by_type),
            "events_by_module": dict(events_by_module),
        }
