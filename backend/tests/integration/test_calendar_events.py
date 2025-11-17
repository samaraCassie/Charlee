"""Integration tests for Calendar Event Bus integration."""

import pytest
from datetime import datetime, timedelta, timezone
from database.models import CalendarConnection, CalendarEvent, CalendarConflict
from events.calendar_events import CalendarEventPublisher
from integration.event_bus import EventBus
from integration.event_types import EventType, ModuleName


@pytest.fixture
def event_bus(db):
    """Create Event Bus instance."""
    return EventBus(db)


@pytest.fixture
def calendar_publisher(db, event_bus):
    """Create Calendar Event Publisher."""
    return CalendarEventPublisher(db, event_bus)


@pytest.fixture
def sample_calendar_connection(db, sample_user):
    """Create a sample calendar connection."""
    connection = CalendarConnection(
        user_id=sample_user.id,
        provider="google",
        calendar_id="primary",
        calendar_name="Test Calendar",
        access_token="token",
        sync_enabled=True,
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@pytest.fixture
def sample_calendar_event(db, sample_user, sample_calendar_connection):
    """Create a sample calendar event."""
    event = CalendarEvent(
        connection_id=sample_calendar_connection.id,
        user_id=sample_user.id,
        external_event_id="event_123",
        title="Test Event",
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(hours=1),
        source="external",
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


class TestCalendarEventPublisher:
    """Test suite for Calendar Event Publisher."""

    @pytest.mark.asyncio
    async def test_publish_connection_created(
        self, calendar_publisher, sample_calendar_connection, db
    ):
        """Should publish CALENDAR_CONNECTED event."""
        event_id = await calendar_publisher.publish_connection_created(sample_calendar_connection)

        assert event_id is not None

        # Verify event was saved to database
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_CONNECTED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.modulo_origem == ModuleName.CALENDAR.value
        assert latest_event.payload["provider"] == "google"
        assert latest_event.payload["connection_id"] == sample_calendar_connection.id

    @pytest.mark.asyncio
    async def test_publish_connection_deleted(self, calendar_publisher, db):
        """Should publish CALENDAR_DISCONNECTED event."""
        event_id = await calendar_publisher.publish_connection_deleted(
            connection_id=1, user_id=1, provider="google"
        )

        assert event_id is not None

        # Verify event
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_DISCONNECTED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.payload["connection_id"] == 1
        assert latest_event.payload["provider"] == "google"

    @pytest.mark.asyncio
    async def test_publish_sync_completed(self, calendar_publisher, db):
        """Should publish CALENDAR_SYNCED event."""
        stats = {
            "events_created": 5,
            "events_updated": 3,
            "events_deleted": 1,
            "conflicts_detected": 0,
        }

        event_id = await calendar_publisher.publish_sync_completed(connection_id=1, stats=stats)

        assert event_id is not None

        # Verify event payload
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent).filter(SystemEvent.tipo == EventType.CALENDAR_SYNCED.value).all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.payload["events_created"] == 5
        assert latest_event.payload["events_updated"] == 3

    @pytest.mark.asyncio
    async def test_publish_sync_failed(self, calendar_publisher, db):
        """Should publish CALENDAR_SYNC_FAILED event with high priority."""
        event_id = await calendar_publisher.publish_sync_failed(
            connection_id=1, error_message="Token expired"
        )

        assert event_id is not None

        # Verify event
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_SYNC_FAILED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.prioridade == 8  # High priority for failures
        assert latest_event.payload["error_message"] == "Token expired"

    @pytest.mark.asyncio
    async def test_publish_event_created(self, calendar_publisher, sample_calendar_event, db):
        """Should publish CALENDAR_EVENT_CREATED event."""
        event_id = await calendar_publisher.publish_event_created(sample_calendar_event)

        assert event_id is not None

        # Verify event
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_EVENT_CREATED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.payload["title"] == "Test Event"
        assert latest_event.payload["source"] == "external"

    @pytest.mark.asyncio
    async def test_publish_conflict_detected(self, calendar_publisher, db, sample_calendar_event):
        """Should publish CALENDAR_CONFLICT_DETECTED event with high priority."""
        conflict = CalendarConflict(
            event_id=sample_calendar_event.id,
            user_id=sample_calendar_event.user_id,
            conflict_type="both_modified",
            charlee_version={"title": "Charlee"},
            external_version={"title": "External"},
            resolution_strategy="manual",
            status="detected",
        )
        db.add(conflict)
        db.commit()
        db.refresh(conflict)

        event_id = await calendar_publisher.publish_conflict_detected(conflict)

        assert event_id is not None

        # Verify event
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_CONFLICT_DETECTED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.prioridade == 8  # High priority for conflicts
        assert latest_event.payload["conflict_type"] == "both_modified"

    @pytest.mark.asyncio
    async def test_publish_conflict_resolved(self, calendar_publisher, db, sample_calendar_event):
        """Should publish CALENDAR_CONFLICT_RESOLVED event."""
        conflict = CalendarConflict(
            event_id=sample_calendar_event.id,
            user_id=sample_calendar_event.user_id,
            conflict_type="both_modified",
            charlee_version={"title": "Charlee"},
            external_version={"title": "External"},
            resolution_strategy="charlee_wins",
            status="detected",
        )
        db.add(conflict)
        db.commit()

        # Resolve conflict
        conflict.resolve({"title": "Charlee"}, "system_charlee")
        db.commit()
        db.refresh(conflict)

        event_id = await calendar_publisher.publish_conflict_resolved(conflict)

        assert event_id is not None

        # Verify event
        from database.models import SystemEvent

        events = (
            db.query(SystemEvent)
            .filter(SystemEvent.tipo == EventType.CALENDAR_CONFLICT_RESOLVED.value)
            .all()
        )

        assert len(events) >= 1
        latest_event = events[-1]
        assert latest_event.payload["resolved_by"] == "system_charlee"


class TestEventBusSubscriptions:
    """Test suite for Event Bus subscriptions with calendar events."""

    @pytest.mark.asyncio
    async def test_subscribe_to_calendar_connected(self, event_bus, db):
        """Should receive CALENDAR_CONNECTED events when subscribed."""
        received_events = []

        async def handler(event):
            received_events.append(event)

        # Subscribe to event
        event_bus.subscribe(EventType.CALENDAR_CONNECTED, handler)

        # Publish event
        from integration.event_bus import Event

        event = Event(
            tipo=EventType.CALENDAR_CONNECTED,
            modulo_origem=ModuleName.CALENDAR,
            payload={"connection_id": 1, "provider": "google"},
        )

        await event_bus.publish(event)

        # Process events
        if not event_bus._is_running:
            event_bus.start_processing()

        # Give time for processing
        import asyncio

        await asyncio.sleep(0.1)

        # Verify handler was called
        assert len(received_events) >= 1
        assert received_events[0].tipo == EventType.CALENDAR_CONNECTED

    @pytest.mark.asyncio
    async def test_multiple_handlers_for_sync_events(self, event_bus):
        """Should notify multiple handlers for sync events."""
        handler1_called = []
        handler2_called = []

        async def handler1(event):
            handler1_called.append(event)

        def handler2(event):
            handler2_called.append(event)

        # Subscribe both handlers
        event_bus.subscribe(EventType.CALENDAR_SYNCED, handler1)
        event_bus.subscribe(EventType.CALENDAR_SYNCED, handler2)

        # Publish event
        from integration.event_bus import Event

        event = Event(
            tipo=EventType.CALENDAR_SYNCED,
            modulo_origem=ModuleName.CALENDAR,
            payload={"connection_id": 1, "events_created": 5},
        )

        await event_bus.publish(event)

        # Process events
        if not event_bus._is_running:
            event_bus.start_processing()

        import asyncio

        await asyncio.sleep(0.1)

        # Both handlers should be called
        assert len(handler1_called) >= 1
        assert len(handler2_called) >= 1


class TestCalendarEventStatistics:
    """Test suite for calendar event statistics."""

    @pytest.mark.asyncio
    async def test_get_calendar_event_stats(self, event_bus, calendar_publisher, db):
        """Should get statistics for calendar events."""
        # Publish various calendar events
        await calendar_publisher.publish_sync_completed(
            connection_id=1, stats={"events_created": 5}
        )
        await calendar_publisher.publish_sync_failed(connection_id=1, error_message="Error")

        # Get stats
        stats = event_bus.get_event_stats(hours=24)

        assert stats["total_events"] >= 2
        assert EventType.CALENDAR_SYNCED.value in stats["events_by_type"]
        assert EventType.CALENDAR_SYNC_FAILED.value in stats["events_by_type"]
        assert ModuleName.CALENDAR.value in stats["events_by_module"]

    @pytest.mark.asyncio
    async def test_get_recent_calendar_events(self, event_bus, calendar_publisher, db):
        """Should retrieve recent calendar events."""
        # Publish some events
        await calendar_publisher.publish_sync_completed(
            connection_id=1, stats={"events_created": 3}
        )

        # Get recent events of this type
        recent_events = event_bus.get_recent_events(event_type=EventType.CALENDAR_SYNCED, limit=10)

        assert len(recent_events) >= 1
        assert recent_events[0].tipo == EventType.CALENDAR_SYNCED.value
