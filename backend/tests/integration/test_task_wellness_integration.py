"""Integration tests for Task-Wellness Integration."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from database.models import Task, User, BigRock
from integration.task_wellness_integration import TaskWellnessIntegration
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
        role="user",
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
def task_wellness(db_session, event_bus, context_manager):
    """Create a TaskWellnessIntegration instance."""
    return TaskWellnessIntegration(
        db_session=db_session, event_bus=event_bus, context_manager=context_manager
    )


def test_initialization(task_wellness):
    """Test TaskWellnessIntegration initialization."""
    assert task_wellness.db is not None
    assert task_wellness.event_bus is not None
    assert task_wellness.context is not None


def test_event_subscriptions(task_wellness):
    """Test that events are subscribed correctly."""
    # Check that event handlers are registered
    subscribers = task_wellness.event_bus.subscribers

    assert EventType.CYCLE_PHASE_CHANGED in subscribers
    assert EventType.ENERGY_LOW in subscribers
    assert EventType.TASK_CREATED in subscribers


def test_on_cycle_phase_changed_menstrual(db_session, task_wellness, context_manager):
    """Test task adjustment during menstrual phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create test tasks
    task1 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Regular task",
        type="task",
        status="pending",
    )
    task2 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Fixed appointment",
        type="fixed_appointment",
        status="pending",
    )
    db_session.add_all([task1, task2])
    db_session.commit()

    # Trigger cycle phase change to menstrual
    event = Event(
        tipo=EventType.CYCLE_PHASE_CHANGED,
        modulo_origem=ModuleName.WELLNESS_COACH,
        payload={"nova_fase": "menstrual", "energia_esperada": 0.5},
    )

    task_wellness.on_cycle_phase_changed(event)

    # Verify event was processed (no exceptions)
    assert True


def test_on_cycle_phase_changed_ovulation(db_session, task_wellness):
    """Test task adjustment during ovulation phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create task with meeting keyword
    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Reunião com cliente",
        type="task",
        status="pending",
    )
    db_session.add(task)
    db_session.commit()

    event = Event(
        tipo=EventType.CYCLE_PHASE_CHANGED,
        modulo_origem=ModuleName.WELLNESS_COACH,
        payload={"nova_fase": "ovulacao", "energia_esperada": 0.9},
    )

    task_wellness.on_cycle_phase_changed(event)

    # Check that adjustment is positive for meetings during ovulation
    adjustment = task_wellness._calculate_priority_adjustment(task, "ovulacao", 0.9)
    assert adjustment == 1


def test_on_cycle_phase_changed_luteal(db_session, task_wellness):
    """Test task adjustment during luteal phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create task in progress
    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task in progress",
        type="task",
        status="in_progress",
    )
    db_session.add(task)
    db_session.commit()

    event = Event(
        tipo=EventType.CYCLE_PHASE_CHANGED,
        modulo_origem=ModuleName.WELLNESS_COACH,
        payload={"nova_fase": "lutea", "energia_esperada": 0.7},
    )

    task_wellness.on_cycle_phase_changed(event)

    # Check that adjustment is positive for in-progress tasks during luteal
    adjustment = task_wellness._calculate_priority_adjustment(task, "lutea", 0.7)
    assert adjustment == 1


def test_on_energy_low(task_wellness):
    """Test low energy event handler."""
    event = Event(tipo=EventType.ENERGY_LOW, modulo_origem=ModuleName.WELLNESS_COACH, payload={})

    # Should not raise any exceptions
    task_wellness.on_energy_low(event)
    assert True


def test_on_task_created_heavy_during_menstrual(db_session, task_wellness, context_manager):
    """Test task creation of heavy task during menstrual phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Set context to menstrual with low energy
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 3})

    # Create heavy task
    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Desenvolver nova feature complexa",
        type="task",
        status="pending",
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    event = Event(
        tipo=EventType.TASK_CREATED,
        modulo_origem=ModuleName.TASK_MANAGER,
        payload={"task_id": task.id},
    )

    # Should log warning but not raise exception
    task_wellness.on_task_created(event)
    assert True


def test_on_task_created_light_during_menstrual(db_session, task_wellness, context_manager):
    """Test task creation of light task during menstrual phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Set context to menstrual with low energy
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 3})

    # Create light task
    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Review email",
        type="task",
        status="pending",
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    event = Event(
        tipo=EventType.TASK_CREATED,
        modulo_origem=ModuleName.TASK_MANAGER,
        payload={"task_id": task.id},
    )

    # Should process without warning
    task_wellness.on_task_created(event)
    assert True


def test_on_task_created_missing_task_id(task_wellness):
    """Test task creation event without task_id."""
    event = Event(tipo=EventType.TASK_CREATED, modulo_origem=ModuleName.TASK_MANAGER, payload={})

    # Should handle gracefully
    task_wellness.on_task_created(event)
    assert True


def test_calculate_priority_adjustment_menstrual_low_energy(db_session, task_wellness):
    """Test priority adjustment for menstrual phase with low energy."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Regular task",
        type="task",
        status="pending",
    )

    adjustment = task_wellness._calculate_priority_adjustment(task, "menstrual", 0.5)
    assert adjustment == -1


def test_calculate_priority_adjustment_menstrual_fixed_appointment(db_session, task_wellness):
    """Test that fixed appointments are not deprioritized."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Doctor appointment",
        type="fixed_appointment",
        status="pending",
    )

    adjustment = task_wellness._calculate_priority_adjustment(task, "menstrual", 0.5)
    assert adjustment == 0  # No deprioritization for fixed appointments


def test_calculate_priority_adjustment_ovulation_meeting(db_session, task_wellness):
    """Test priority boost for meetings during ovulation."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Client reunião",
        type="task",
        status="pending",
    )

    adjustment = task_wellness._calculate_priority_adjustment(task, "ovulacao", 0.9)
    assert adjustment == 1


def test_calculate_priority_adjustment_ovulation_presentation(db_session, task_wellness):
    """Test priority boost for presentations during ovulation."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Preparar apresentação",
        type="task",
        status="pending",
    )

    adjustment = task_wellness._calculate_priority_adjustment(task, "ovulacao", 0.9)
    assert adjustment == 1


def test_is_heavy_task_by_hours(db_session, task_wellness):
    """Test heavy task detection by keyword 'migrar'."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Migrar banco de dados",
        type="task",
        status="pending",
    )

    assert task_wellness._is_heavy_task(task) is True


def test_is_heavy_task_by_keyword_desenvolvimento(db_session, task_wellness):
    """Test heavy task detection by 'desenvolvimento' keyword."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Desenvolvimento de nova API",
        type="task",
        status="pending",
    )

    assert task_wellness._is_heavy_task(task) is True


def test_is_heavy_task_by_keyword_implementar(db_session, task_wellness):
    """Test heavy task detection by 'implementar' keyword."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Implementar autenticação",
        type="task",
        status="pending",
    )

    assert task_wellness._is_heavy_task(task) is True


def test_is_not_heavy_task(db_session, task_wellness):
    """Test light task detection."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Review email",
        type="task",
        status="pending",
    )

    assert task_wellness._is_heavy_task(task) is False


def test_get_wellness_adjusted_tasks(db_session, task_wellness, context_manager):
    """Test getting wellness-adjusted task recommendations."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Create various tasks
    task1 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Light task",
        type="task",
        status="pending",
    )
    task2 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Desenvolver feature",
        type="task",
        status="pending",
    )
    db_session.add_all([task1, task2])
    db_session.commit()

    result = task_wellness.get_wellness_adjusted_tasks(limit=10)

    assert "recommended" in result
    assert "deferred" in result
    assert "reason" in result
    assert isinstance(result["recommended"], list)
    assert isinstance(result["deferred"], list)


def test_get_wellness_adjusted_tasks_menstrual_low_energy(
    db_session, task_wellness, context_manager
):
    """Test task recommendations during menstrual phase with low energy."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    # Set context to menstrual with low energy
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 3})

    # Create light and heavy tasks
    light_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Check emails",
        type="task",
        status="pending",
    )
    heavy_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Desenvolver sistema complexo",
        type="task",
        status="pending",
    )
    db_session.add_all([light_task, heavy_task])
    db_session.commit()

    result = task_wellness.get_wellness_adjusted_tasks(limit=10)

    # Light task should be recommended, heavy task deferred
    recommended_ids = [t.id for t in result["recommended"]]
    deferred_ids = [t.id for t in result["deferred"]]

    assert light_task.id in recommended_ids
    assert heavy_task.id in deferred_ids


def test_should_recommend_task_fixed_appointment(db_session, task_wellness):
    """Test that fixed appointments are always recommended."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Doctor appointment",
        type="fixed_appointment",
        status="pending",
    )

    context = {"fase_ciclo": "menstrual", "energia_atual": 2, "nivel_stress": 9}

    assert task_wellness._should_recommend_task(task, context) is True


def test_should_recommend_task_menstrual_heavy(db_session, task_wellness):
    """Test that heavy tasks are not recommended during menstrual phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Desenvolver feature",
        type="task",
        status="pending",
    )

    context = {"fase_ciclo": "menstrual", "energia_atual": 3, "nivel_stress": 5}

    assert task_wellness._should_recommend_task(task, context) is False


def test_should_recommend_task_menstrual_light(db_session, task_wellness):
    """Test that light tasks are recommended during menstrual phase."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Review email",
        type="task",
        status="pending",
    )

    context = {"fase_ciclo": "menstrual", "energia_atual": 3, "nivel_stress": 5}

    assert task_wellness._should_recommend_task(task, context) is True


def test_should_recommend_task_high_stress_urgent(db_session, task_wellness):
    """Test that urgent tasks are recommended during high stress."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    urgent_task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Urgent task",
        type="task",
        status="pending",
        deadline=datetime.now() + timedelta(days=1),
    )

    context = {"fase_ciclo": "folicular", "energia_atual": 7, "nivel_stress": 9}

    assert task_wellness._should_recommend_task(urgent_task, context) is True


def test_should_recommend_task_high_stress_not_urgent(db_session, task_wellness):
    """Test that non-urgent tasks are not recommended during high stress."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Non-urgent task",
        type="task",
        status="pending",
        deadline=datetime.now() + timedelta(days=5),
    )

    context = {"fase_ciclo": "folicular", "energia_atual": 7, "nivel_stress": 9}

    assert task_wellness._should_recommend_task(task, context) is False


def test_should_recommend_task_normal_conditions(db_session, task_wellness):
    """Test task recommendations in normal conditions."""
    user = db_session.query(User).first()
    big_rock = db_session.query(BigRock).first()

    task = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Any task",
        type="task",
        status="pending",
    )

    context = {
        "fase_ciclo": "folicular",
        "energia_atual": 7,
        "nivel_stress": 5,
        "em_sessao_foco": False,
    }

    assert task_wellness._should_recommend_task(task, context) is True


def test_get_recommendation_reason_menstrual(task_wellness, context_manager):
    """Test recommendation reason during menstrual phase."""
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 3})

    context = context_manager.get_context()
    reason = task_wellness._get_recommendation_reason(context)

    assert "menstrual" in reason.lower()
    assert "energia baixa" in reason.lower()


def test_get_recommendation_reason_high_stress(task_wellness, context_manager):
    """Test recommendation reason during high stress."""
    context_manager.update_context({"nivel_stress": 9})

    context = context_manager.get_context()
    reason = task_wellness._get_recommendation_reason(context)

    assert "stress" in reason.lower()


def test_get_recommendation_reason_focus_session(task_wellness, context_manager):
    """Test recommendation reason during focus session."""
    context_manager.update_context({"em_sessao_foco": True})

    context = context_manager.get_context()
    reason = task_wellness._get_recommendation_reason(context)

    assert "foco" in reason.lower()


def test_get_recommendation_reason_normal(task_wellness, context_manager):
    """Test recommendation reason in normal conditions."""
    context_manager.update_context(
        {
            "fase_ciclo": "folicular",
            "energia_atual": 7,
            "nivel_stress": 5,
            "em_sessao_foco": False,
        }
    )

    context = context_manager.get_context()
    reason = task_wellness._get_recommendation_reason(context)

    assert "normais" in reason.lower()
