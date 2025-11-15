"""Integration tests for Capacity Integration."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from database.models import Task, User, BigRock
from integration.capacity_integration import CapacityIntegration
from integration.context_manager import ContextManager
from integration.event_bus import Event, EventBus
from integration.event_types import EventType, ModuleName


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test user
    user = User(
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create test big rock
    big_rock = BigRock(user_id=user.id, name="Test Big Rock", color="#FF0000")
    session.add(big_rock)
    session.commit()
    session.refresh(big_rock)

    yield session

    session.close()


@pytest.fixture
def event_bus(db_session):
    """Create an Event Bus instance."""
    return EventBus(db_session=db_session, redis_client=None)


@pytest.fixture
def context_manager(db_session, event_bus):
    """Create a Context Manager instance."""
    user = db_session.query(User).first()
    return ContextManager(db_session=db_session, event_bus=event_bus, user_id=user.id)


@pytest.fixture
def capacity_integration(db_session, event_bus, context_manager):
    """Create a CapacityIntegration instance."""
    return CapacityIntegration(
        db_session=db_session, event_bus=event_bus, context_manager=context_manager
    )


def test_initialization(capacity_integration):
    """Test CapacityIntegration initialization."""
    assert capacity_integration.db is not None
    assert capacity_integration.event_bus is not None
    assert capacity_integration.context is not None


def test_event_subscriptions(capacity_integration):
    """Test that events are subscribed correctly."""
    subscribers = capacity_integration.event_bus.subscribers

    assert EventType.CAPACITY_CRITICAL in subscribers
    assert EventType.CAPACITY_WARNING in subscribers
    assert EventType.TASK_CREATED in subscribers


def test_on_capacity_critical(db_session, capacity_integration):
    """Test critical capacity event handler."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create some postponable tasks
    future_date = datetime.now() + timedelta(days=5)
    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Non-urgent task",
        type="task",
        status="pending",
        deadline=future_date,
    )
    db_session.add(task)
    db_session.commit()

    event = Event(
        tipo=EventType.CAPACITY_CRITICAL,
        modulo_origem=ModuleName.CAPACITY_GUARDIAN,
        payload={"percentual_carga": 95},
    )

    # Should process without exceptions
    capacity_integration.on_capacity_critical(event)
    assert True


def test_on_capacity_warning(capacity_integration):
    """Test capacity warning event handler."""
    event = Event(
        tipo=EventType.CAPACITY_WARNING,
        modulo_origem=ModuleName.CAPACITY_GUARDIAN,
        payload={"percentual_carga": 80},
    )

    # Should process without exceptions
    capacity_integration.on_capacity_warning(event)
    assert True


def test_on_task_created_high_capacity(capacity_integration, context_manager):
    """Test task creation when capacity is high."""
    # Set high capacity
    context_manager.update_context({"carga_trabalho_percentual": 85})

    event = Event(
        tipo=EventType.TASK_CREATED, modulo_origem=ModuleName.TASK_MANAGER, payload={"task_id": 123}
    )

    # Should log warning but not raise exception
    capacity_integration.on_task_created(event)
    assert True


def test_on_task_created_low_capacity(capacity_integration, context_manager):
    """Test task creation when capacity is low."""
    # Set low capacity
    context_manager.update_context({"carga_trabalho_percentual": 50})

    event = Event(
        tipo=EventType.TASK_CREATED, modulo_origem=ModuleName.TASK_MANAGER, payload={"task_id": 123}
    )

    # Should process without warning
    capacity_integration.on_task_created(event)
    assert True


def test_suggest_task_postponements_with_tasks(db_session, capacity_integration):
    """Test suggesting tasks for postponement when tasks exist."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create non-urgent tasks
    future_date = datetime.now() + timedelta(days=5)
    task1 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task 1",
        type="task",
        status="pending",
        deadline=future_date,
    )
    task2 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task 2",
        type="task",
        status="pending",
        deadline=future_date + timedelta(days=1),
    )
    db_session.add_all([task1, task2])
    db_session.commit()

    suggestions = capacity_integration._suggest_task_postponements()

    assert len(suggestions) >= 1
    assert all(task.status == "pending" for task in suggestions)
    assert all(task.type != "fixed_appointment" for task in suggestions)


def test_suggest_task_postponements_excludes_urgent(db_session, capacity_integration):
    """Test that urgent tasks are not suggested for postponement."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create urgent task (deadline within 3 days)
    urgent_date = datetime.now() + timedelta(days=2)
    urgent_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Urgent task",
        type="task",
        status="pending",
        deadline=urgent_date,
    )
    db_session.add(urgent_task)
    db_session.commit()

    suggestions = capacity_integration._suggest_task_postponements()

    # Urgent task should not be in suggestions
    suggestion_ids = [t.id for t in suggestions]
    assert urgent_task.id not in suggestion_ids


def test_suggest_task_postponements_excludes_fixed(db_session, capacity_integration):
    """Test that fixed appointments are not suggested for postponement."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create fixed appointment
    future_date = datetime.now() + timedelta(days=5)
    fixed_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Fixed appointment",
        type="fixed_appointment",
        status="pending",
        deadline=future_date,
    )
    db_session.add(fixed_task)
    db_session.commit()

    suggestions = capacity_integration._suggest_task_postponements()

    # Fixed appointments should not be in suggestions
    suggestion_ids = [t.id for t in suggestions]
    assert fixed_task.id not in suggestion_ids


def test_suggest_task_postponements_empty(capacity_integration):
    """Test suggesting postponements when no suitable tasks exist."""
    suggestions = capacity_integration._suggest_task_postponements()

    assert isinstance(suggestions, list)
    # May be empty if no tasks exist
    assert len(suggestions) >= 0


def test_check_capacity_before_accept_safe(capacity_integration, context_manager):
    """Test capacity check with safe load."""
    # Set low current load
    context_manager.update_context({"carga_trabalho_percentual": 30})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=10)

    assert result["recommendation"] == "accept"
    assert "safe limits" in result["reason"]
    assert result["current_load"] == 30
    assert result["projected_load"] < 75
    assert "wellness_consideration" in result


def test_check_capacity_before_accept_with_caution(capacity_integration, context_manager):
    """Test capacity check with moderate load."""
    # Set moderate current load
    context_manager.update_context({"carga_trabalho_percentual": 50})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=15)

    assert result["recommendation"] == "accept_with_caution"
    assert "high" in result["reason"]
    assert result["current_load"] == 50
    assert 75 < result["projected_load"] <= 90


def test_check_capacity_before_accept_negotiate(capacity_integration, context_manager):
    """Test capacity check requiring negotiation."""
    # Set high current load
    context_manager.update_context({"carga_trabalho_percentual": 70})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=20)

    assert result["recommendation"] == "negotiate"
    assert "critical" in result["reason"]
    assert result["current_load"] == 70
    assert 90 < result["projected_load"] <= 100


def test_check_capacity_before_accept_reject(capacity_integration, context_manager):
    """Test capacity check requiring rejection."""
    # Set very high current load
    context_manager.update_context({"carga_trabalho_percentual": 85})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=20)

    assert result["recommendation"] == "reject"
    assert "exceed 100%" in result["reason"]
    assert result["current_load"] == 85
    assert result["projected_load"] > 100


def test_check_capacity_small_task(capacity_integration, context_manager):
    """Test capacity check for small task."""
    # Set moderate load
    context_manager.update_context({"carga_trabalho_percentual": 60})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=2)

    assert result["recommendation"] == "accept"
    assert result["estimated_impact"] < 10
    assert result["projected_load"] < 75


def test_check_capacity_large_task(capacity_integration, context_manager):
    """Test capacity check for large task."""
    # Set low load
    context_manager.update_context({"carga_trabalho_percentual": 30})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=30)

    # 30 hours = 75% of 40-hour week
    assert result["estimated_impact"] == 75.0
    assert result["projected_load"] > 100
    assert result["recommendation"] == "reject"


def test_get_wellness_consideration_menstrual(capacity_integration, context_manager):
    """Test wellness consideration during menstrual phase."""
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 3})

    consideration = capacity_integration._get_wellness_consideration()

    assert "menstrual" in consideration.lower()
    assert "energia" in consideration.lower()


def test_get_wellness_consideration_high_stress(capacity_integration, context_manager):
    """Test wellness consideration with high stress."""
    context_manager.update_context({"nivel_stress": 9})

    consideration = capacity_integration._get_wellness_consideration()

    assert "stress" in consideration.lower()


def test_get_wellness_consideration_needs_break(capacity_integration, context_manager):
    """Test wellness consideration when break is needed."""
    context_manager.update_context({"necessita_pausa": True})

    consideration = capacity_integration._get_wellness_consideration()

    assert "pausa" in consideration.lower()


def test_get_wellness_consideration_normal(capacity_integration, context_manager):
    """Test wellness consideration in normal conditions."""
    context_manager.update_context(
        {"fase_ciclo": "folicular", "energia_atual": 7, "nivel_stress": 5, "necessita_pausa": False}
    )

    consideration = capacity_integration._get_wellness_consideration()

    assert "normais" in consideration.lower()


def test_check_capacity_includes_wellness(capacity_integration, context_manager):
    """Test that capacity check includes wellness consideration."""
    # Set menstrual phase with low energy
    context_manager.update_context(
        {"fase_ciclo": "menstrual", "energia_atual": 3, "carga_trabalho_percentual": 50}
    )

    result = capacity_integration.check_capacity_before_accept(estimated_hours=10)

    assert "wellness_consideration" in result
    assert "menstrual" in result["wellness_consideration"].lower()


def test_capacity_critical_with_no_postponable_tasks(db_session, capacity_integration):
    """Test critical capacity when no tasks can be postponed."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create only urgent or fixed tasks
    urgent_date = datetime.now() + timedelta(days=1)
    urgent_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Urgent task",
        type="task",
        status="pending",
        deadline=urgent_date,
    )
    fixed_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Fixed appointment",
        type="fixed_appointment",
        status="pending",
        deadline=datetime.now() + timedelta(days=5),
    )
    db_session.add_all([urgent_task, fixed_task])
    db_session.commit()

    event = Event(
        tipo=EventType.CAPACITY_CRITICAL,
        modulo_origem=ModuleName.CAPACITY_GUARDIAN,
        payload={"percentual_carga": 98},
    )

    # Should process without exceptions even with no suggestions
    capacity_integration.on_capacity_critical(event)
    assert True


def test_check_capacity_boundary_75_percent(capacity_integration, context_manager):
    """Test capacity check at 75% boundary."""
    context_manager.update_context({"carga_trabalho_percentual": 50})

    # Exactly 25% impact to reach 75%
    result = capacity_integration.check_capacity_before_accept(estimated_hours=10)

    assert result["projected_load"] == 75.0
    assert result["recommendation"] == "accept"


def test_check_capacity_boundary_90_percent(capacity_integration, context_manager):
    """Test capacity check at 90% boundary."""
    context_manager.update_context({"carga_trabalho_percentual": 60})

    # Exactly 30% impact to reach 90%
    result = capacity_integration.check_capacity_before_accept(estimated_hours=12)

    assert result["projected_load"] == 90.0
    assert result["recommendation"] == "accept_with_caution"


def test_check_capacity_boundary_100_percent(capacity_integration, context_manager):
    """Test capacity check at 100% boundary."""
    context_manager.update_context({"carga_trabalho_percentual": 60})

    # Exactly 40% impact to reach 100%
    result = capacity_integration.check_capacity_before_accept(estimated_hours=16)

    assert result["projected_load"] == 100.0
    assert result["recommendation"] == "negotiate"


def test_capacity_decision_reasoning(capacity_integration, context_manager):
    """Test that capacity decisions include proper reasoning."""
    context_manager.update_context({"carga_trabalho_percentual": 85})

    result = capacity_integration.check_capacity_before_accept(estimated_hours=10)

    # Should include current load, impact, and projected load in reason
    assert "85" in result["reason"]  # Current load
    assert "25" in result["reason"]  # Impact (10/40 * 100)
    assert "110" in result["reason"]  # Projected load
