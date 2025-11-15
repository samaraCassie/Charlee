"""Integration tests for Context Manager."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.config import Base
from database.models import GlobalContext, Task, User, BigRock
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


def test_initialize_context(context_manager, db_session):
    """Test context initialization."""
    context = context_manager.current_context

    assert context is not None
    assert context.user_id == context_manager.user_id
    assert context.fase_ciclo == "folicular"
    assert context.energia_atual == 7
    assert context.carga_trabalho_percentual == 50.0
    assert context.em_sessao_foco is False
    assert context.nivel_stress == 5
    assert context.necessita_pausa is False


def test_load_existing_context(db_session, event_bus):
    """Test loading existing context."""
    user = db_session.query(User).first()

    # Create existing context
    existing_context = GlobalContext(
        user_id=user.id,
        fase_ciclo="lutea",
        energia_atual=6,
        carga_trabalho_percentual=75.0,
        nivel_stress=7,
    )
    db_session.add(existing_context)
    db_session.commit()

    # Load context
    cm = ContextManager(db_session, event_bus, user.id)

    assert cm.current_context.fase_ciclo == "lutea"
    assert cm.current_context.energia_atual == 6
    assert cm.current_context.carga_trabalho_percentual == 75.0
    assert cm.current_context.nivel_stress == 7


def test_update_context(context_manager):
    """Test context updates."""
    context_manager.update_context({"energia_atual": 9, "nivel_stress": 3})

    assert context_manager.current_context.energia_atual == 9
    assert context_manager.current_context.nivel_stress == 3


@pytest.mark.asyncio
async def test_on_cycle_phase_changed(context_manager):
    """Test cycle phase change event handler."""
    event = Event(
        tipo=EventType.CYCLE_PHASE_CHANGED,
        modulo_origem=ModuleName.WELLNESS_COACH,
        payload={"nova_fase": "ovulacao", "energia_esperada": 0.9},
    )

    context_manager.on_cycle_phase_changed(event)

    assert context_manager.current_context.fase_ciclo == "ovulacao"
    assert context_manager.current_context.energia_atual == 9  # 0.9 * 10


@pytest.mark.asyncio
async def test_on_energy_low(context_manager):
    """Test low energy event handler."""
    initial_stress = context_manager.current_context.nivel_stress

    event = Event(tipo=EventType.ENERGY_LOW, modulo_origem=ModuleName.WELLNESS_COACH, payload={})

    context_manager.on_energy_low(event)

    assert context_manager.current_context.nivel_stress == min(initial_stress + 2, 10)
    assert context_manager.current_context.necessita_pausa is True


@pytest.mark.asyncio
async def test_on_capacity_warning(context_manager):
    """Test capacity warning event handler."""
    event = Event(
        tipo=EventType.CAPACITY_WARNING,
        modulo_origem=ModuleName.CAPACITY_GUARDIAN,
        payload={"percentual_carga": 85},
    )

    context_manager.on_capacity_warning(event)

    assert context_manager.current_context.carga_trabalho_percentual == 85
    assert context_manager.current_context.nivel_stress == 8  # 85 / 10


@pytest.mark.asyncio
async def test_on_capacity_critical(context_manager):
    """Test critical capacity event handler."""
    event = Event(
        tipo=EventType.CAPACITY_CRITICAL,
        modulo_origem=ModuleName.CAPACITY_GUARDIAN,
        payload={"percentual_carga": 95},
    )

    context_manager.on_capacity_critical(event)

    assert context_manager.current_context.carga_trabalho_percentual == 95
    assert context_manager.current_context.nivel_stress == 10
    assert context_manager.current_context.necessita_pausa is True


@pytest.mark.asyncio
async def test_on_focus_started(context_manager):
    """Test focus session start event handler."""
    event = Event(
        tipo=EventType.FOCUS_SESSION_STARTED, modulo_origem=ModuleName.FOCUS_MODULE, payload={}
    )

    context_manager.on_focus_started(event)

    assert context_manager.current_context.em_sessao_foco is True


@pytest.mark.asyncio
async def test_on_focus_ended(context_manager):
    """Test focus session end event handler."""
    # Set initial energy
    context_manager.update_context({"energia_atual": 8, "em_sessao_foco": True})

    event = Event(
        tipo=EventType.FOCUS_SESSION_ENDED,
        modulo_origem=ModuleName.FOCUS_MODULE,
        payload={"qualidade_foco": 9},
    )

    context_manager.on_focus_ended(event)

    assert context_manager.current_context.em_sessao_foco is False
    assert context_manager.current_context.energia_atual == 7  # Decreased by 1


def test_should_accept_interruption_in_focus(context_manager):
    """Test interruption decision when in focus."""
    context_manager.update_context({"em_sessao_foco": True})

    assert context_manager.should_accept_interruption() is False


def test_should_accept_interruption_low_energy(context_manager):
    """Test interruption decision with low energy."""
    context_manager.update_context({"energia_atual": 3})

    assert context_manager.should_accept_interruption() is False


def test_should_accept_interruption_menstrual(context_manager):
    """Test interruption decision during menstrual phase."""
    context_manager.update_context({"fase_ciclo": "menstrual"})

    assert context_manager.should_accept_interruption() is False


def test_should_accept_interruption_high_load(context_manager):
    """Test interruption decision with high workload."""
    context_manager.update_context({"carga_trabalho_percentual": 95})

    assert context_manager.should_accept_interruption() is False


def test_should_accept_interruption_normal(context_manager):
    """Test interruption decision in normal conditions."""
    context_manager.update_context(
        {
            "em_sessao_foco": False,
            "energia_atual": 7,
            "fase_ciclo": "folicular",
            "carga_trabalho_percentual": 60,
        }
    )

    assert context_manager.should_accept_interruption() is True


def test_get_optimal_activity_menstrual(context_manager):
    """Test optimal activity during menstrual phase."""
    context_manager.update_context({"fase_ciclo": "menstrual", "energia_atual": 4})

    activity = context_manager.get_optimal_activity_type()
    assert activity == "administrative"


def test_get_optimal_activity_follicular_morning(context_manager):
    """Test optimal activity during follicular phase in morning."""
    context_manager.update_context({"fase_ciclo": "folicular", "hora_dia": 10})

    activity = context_manager.get_optimal_activity_type()
    assert activity == "strategic_planning"


def test_get_optimal_activity_follicular_afternoon(context_manager):
    """Test optimal activity during follicular phase in afternoon."""
    context_manager.update_context({"fase_ciclo": "folicular", "hora_dia": 15})

    activity = context_manager.get_optimal_activity_type()
    assert activity == "creative_development"


def test_get_optimal_activity_ovulation(context_manager):
    """Test optimal activity during ovulation."""
    context_manager.update_context({"fase_ciclo": "ovulacao"})

    activity = context_manager.get_optimal_activity_type()
    assert activity == "meetings_presentations"


def test_get_optimal_activity_luteal(context_manager):
    """Test optimal activity during luteal phase."""
    context_manager.update_context({"fase_ciclo": "lutea"})

    activity = context_manager.get_optimal_activity_type()
    assert activity == "execution_completion"


def test_needs_break_high_stress(context_manager):
    """Test needs_break with high stress."""
    context_manager.update_context({"nivel_stress": 9})

    assert context_manager.needs_break() is True


def test_needs_break_low_energy(context_manager):
    """Test needs_break with low energy."""
    context_manager.update_context({"energia_atual": 2})

    assert context_manager.needs_break() is True


def test_needs_break_pausa_flag(context_manager):
    """Test needs_break with necessita_pausa flag."""
    context_manager.update_context({"necessita_pausa": True})

    assert context_manager.needs_break() is True


def test_needs_break_normal(context_manager):
    """Test needs_break in normal conditions."""
    context_manager.update_context(
        {"nivel_stress": 5, "energia_atual": 7, "necessita_pausa": False}
    )

    assert context_manager.needs_break() is False


def test_get_context(context_manager):
    """Test getting context as dictionary."""
    context = context_manager.get_context()

    assert isinstance(context, dict)
    assert "fase_ciclo" in context
    assert "energia_atual" in context
    assert "carga_trabalho_percentual" in context
    assert "em_sessao_foco" in context
    assert "nivel_stress" in context
    assert "necessita_pausa" in context
    assert "atualizado_em" in context


def test_count_pending_tasks(db_session, context_manager):
    """Test counting pending tasks."""
    user = db_session.query(User).first()

    # Create big rock
    big_rock = BigRock(user_id=user.id, name="Test Big Rock", color="#FF0000")
    db_session.add(big_rock)
    db_session.commit()
    db_session.refresh(big_rock)

    # Create tasks
    task1 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task 1",
        type="task",
        status="pending",
    )
    task2 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task 2",
        type="task",
        status="in_progress",
    )
    task3 = Task(
        user_id=user.id,
        big_rock_id=big_rock.id,
        description="Task 3",
        type="task",
        status="completed",
    )

    db_session.add_all([task1, task2, task3])
    db_session.commit()

    count = context_manager._count_pending_tasks()

    assert count == 2  # Only Pendente and Em Andamento


def test_get_periodo_produtivo(context_manager):
    """Test getting productivity period."""
    # Morning
    assert context_manager._get_periodo_produtivo(8) == "manha"
    assert context_manager._get_periodo_produtivo(11) == "manha"

    # Afternoon
    assert context_manager._get_periodo_produtivo(14) == "tarde"
    assert context_manager._get_periodo_produtivo(17) == "tarde"

    # Evening
    assert context_manager._get_periodo_produtivo(19) == "noite"
    assert context_manager._get_periodo_produtivo(21) == "noite"

    # Late night
    assert context_manager._get_periodo_produtivo(2) == "madrugada"
    assert context_manager._get_periodo_produtivo(23) == "madrugada"
