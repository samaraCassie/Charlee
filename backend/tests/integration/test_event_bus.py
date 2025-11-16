"""Integration tests for Event Bus system."""

import asyncio
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from database.models import SystemEvent
from integration.event_bus import Event, EventBus
from integration.event_types import EventType, ModuleName


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def event_bus(db_session):
    """Create an Event Bus instance."""
    return EventBus(db_session=db_session, redis_client=None)


@pytest.mark.asyncio
async def test_publish_event(event_bus, db_session):
    """Test publishing an event to the bus."""
    event = Event(
        tipo=EventType.TASK_CREATED,
        modulo_origem=ModuleName.TASK_MANAGER,
        payload={"task_id": 123, "description": "Test task"},
        prioridade=5,
    )

    event_id = await event_bus.publish(event)

    assert event_id is not None
    assert event_id > 0

    # Verify event was saved to database
    db_event = db_session.query(SystemEvent).filter(SystemEvent.id == event_id).first()
    assert db_event is not None
    assert db_event.tipo == "task_created"
    assert db_event.modulo_origem == "task_manager"
    assert db_event.payload["task_id"] == 123


@pytest.mark.asyncio
async def test_event_subscription(event_bus):
    """Test subscribing to events."""
    received_events = []

    def handler(event: Event):
        received_events.append(event)

    event_bus.subscribe(EventType.TASK_COMPLETED, handler)

    assert EventType.TASK_COMPLETED in event_bus.subscribers
    assert handler in event_bus.subscribers[EventType.TASK_COMPLETED]


@pytest.mark.asyncio
async def test_event_processing(event_bus, db_session):
    """Test event processing by subscribers."""
    received_events = []

    def handler(event: Event):
        received_events.append(event)

    event_bus.subscribe(EventType.TASK_COMPLETED, handler)

    # Start processing
    event_bus.start_processing()

    # Publish event
    event = Event(
        tipo=EventType.TASK_COMPLETED,
        modulo_origem=ModuleName.TASK_MANAGER,
        payload={"task_id": 456},
    )

    await event_bus.publish(event)

    # Wait for processing
    await asyncio.sleep(0.1)

    # Stop processing
    await event_bus.stop_processing()

    # Verify handler was called
    assert len(received_events) == 1
    assert received_events[0].payload["task_id"] == 456


@pytest.mark.asyncio
async def test_get_recent_events(event_bus, db_session):
    """Test retrieving recent events."""
    # Publish multiple events
    for i in range(5):
        event = Event(
            tipo=EventType.TASK_CREATED,
            modulo_origem=ModuleName.TASK_MANAGER,
            payload={"task_id": i},
        )
        await event_bus.publish(event)

    # Get recent events
    events = event_bus.get_recent_events(limit=3)

    assert len(events) == 3
    assert all(isinstance(e, SystemEvent) for e in events)


@pytest.mark.asyncio
async def test_event_stats(event_bus, db_session):
    """Test event statistics."""
    # Publish some events
    for i in range(10):
        event = Event(
            tipo=EventType.TASK_CREATED if i % 2 == 0 else EventType.TASK_COMPLETED,
            modulo_origem=ModuleName.TASK_MANAGER,
            payload={"task_id": i},
        )
        await event_bus.publish(event)

    stats = event_bus.get_event_stats(hours=24)

    assert stats["total_events"] == 10
    assert "task_created" in stats["events_by_type"]
    assert "task_completed" in stats["events_by_type"]
    assert "task_manager" in stats["events_by_module"]
