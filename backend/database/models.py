"""SQLAlchemy database models for Charlee V1."""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship

from database.config import Base


# Helper function for timezone-aware datetime defaults
def utc_now():
    """Return current UTC datetime with timezone info."""
    return datetime.now(timezone.utc)


# ==================== Authentication Models ====================


class User(Base):
    """
    User - Authentication and user management.

    Represents users in the system with secure password storage
    and authentication capabilities.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # User profile
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # OAuth fields
    oauth_provider = Column(String(50), nullable=True)  # 'google', 'github', None (local)
    oauth_id = Column(String(255), nullable=True, index=True)  # Provider's user ID
    avatar_url = Column(String(500), nullable=True)

    # Account lockout fields
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_failed_login = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    big_rocks = relationship("BigRock", back_populates="user", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    menstrual_cycles = relationship(
        "MenstrualCycle", back_populates="user", cascade="all, delete-orphan"
    )
    daily_logs = relationship("DailyLog", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    def is_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.locked_until is None:
            return False
        # Ensure locked_until is timezone-aware
        locked_until = self.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) < locked_until

    def reset_failed_attempts(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_failed_login = None

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class RefreshToken(Base):
    """
    Refresh Token - Store refresh tokens for token rotation.

    Stores refresh tokens to enable token revocation and rotation.
    """

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)

    # Token metadata
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=utc_now)
    revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime, nullable=True)

    # Device/session tracking
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"


class AuditLog(Base):
    """
    Audit Log - Track authentication and security events.

    Records important security events for compliance and security monitoring.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)

    # Event information
    event_type = Column(
        String(50), nullable=False, index=True
    )  # 'login', 'logout', 'register', etc.
    event_status = Column(String(20), nullable=False)  # 'success', 'failure', 'blocked'
    event_message = Column(Text, nullable=True)

    # Request metadata
    ip_address = Column(String(50), nullable=True, index=True)
    user_agent = Column(String(255), nullable=True)
    request_path = Column(String(255), nullable=True)

    # Additional data (JSON)
    event_metadata = Column(JSON, nullable=True)  # Extra contextual information

    # Timestamp
    created_at = Column(DateTime, default=utc_now, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, event_type='{self.event_type}', status='{self.event_status}')>"


# ==================== Core Models ====================


class BigRock(Base):
    """
    Big Rocks - Main life pillars.

    Represents the fundamental areas/pillars that structure
    life and tasks.
    """

    __tablename__ = "big_rocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = Column(String(100), nullable=False)
    color = Column(String(20))  # For future UI (e.g., "#FF5733")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="big_rocks")
    tasks = relationship("Task", back_populates="big_rock")

    def __repr__(self):
        return f"<BigRock(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Task(Base):
    """
    Tasks - Tasks associated with Big Rocks.

    Represents tasks that can be:
    - Fixed Appointment: Events with scheduled time
    - Task: To-do with deadline
    - Continuous: Habits/routines without specific deadline
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    description = Column(Text, nullable=False)
    type = Column(
        String(20),
        CheckConstraint("type IN ('fixed_appointment', 'task', 'continuous')"),
        default="task",
    )
    deadline = Column(Date, nullable=True)
    big_rock_id = Column(Integer, ForeignKey("big_rocks.id"), nullable=True)
    status = Column(
        String(20),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')"),
        default="pending",
    )

    # Prioritization (V2)
    calculated_priority = Column(Integer, default=5)  # 1 (most urgent) to 10 (least urgent)
    priority_score = Column(Float, default=0.0)  # Score calculated by algorithm

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    big_rock = relationship("BigRock", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description[:30]}...', status='{self.status}', user_id={self.user_id})>"

    def mark_as_completed(self):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def reopen(self):
        """Reopen a completed task."""
        self.status = "pending"
        self.completed_at = None
        self.updated_at = datetime.now(timezone.utc)


# Performance indexes (created via Alembic migrations)
# CREATE INDEX idx_tasks_status ON tasks(status);
# CREATE INDEX idx_tasks_deadline ON tasks(deadline);
# CREATE INDEX idx_tasks_big_rock ON tasks(big_rock_id);


# ==================== V2 Models ====================


class MenstrualCycle(Base):
    """
    Menstrual Cycle - Well-being and pattern tracking.

    Records information about the menstrual cycle to adapt
    recommendations and planning based on current phase.
    """

    __tablename__ = "menstrual_cycles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    start_date = Column(Date, nullable=False)
    phase = Column(
        String(20),
        CheckConstraint("phase IN ('menstrual', 'follicular', 'ovulation', 'luteal')"),
        nullable=False,
    )
    # Symptoms as comma-separated list
    symptoms = Column(Text, nullable=True)  # 'fatigue,high_creativity,pain'

    # Energy and mood levels (1-10)
    energy_level = Column(Integer, CheckConstraint("energy_level BETWEEN 1 AND 10"), nullable=True)
    focus_level = Column(Integer, CheckConstraint("focus_level BETWEEN 1 AND 10"), nullable=True)
    creativity_level = Column(
        Integer, CheckConstraint("creativity_level BETWEEN 1 AND 10"), nullable=True
    )

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="menstrual_cycles")

    def __repr__(self):
        return f"<MenstrualCycle(date={self.start_date}, phase='{self.phase}', user_id={self.user_id})>"


class CyclePatterns(Base):
    """
    Cycle Patterns - Learning about productivity by phase.

    Stores patterns identified by AI about how each
    cycle phase affects productivity and well-being.
    """

    __tablename__ = "cycle_patterns"

    id = Column(Integer, primary_key=True, index=True)
    phase = Column(String(20), nullable=False)
    identified_pattern = Column(Text, nullable=False)

    # Average metrics for this phase
    average_productivity = Column(Float, default=1.0)  # Multiplier (1.0 = normal)
    average_focus = Column(Float, default=1.0)
    average_energy = Column(Float, default=1.0)

    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    suggestions = Column(Text, nullable=True)  # Suggestions separated by ;
    samples_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def __repr__(self):
        return f"<CyclePatterns(phase='{self.phase}', confidence={self.confidence_score})>"


class Workload(Base):
    """
    Workload - Capacity vs. demand analysis.

    Calculates and monitors workload per Big Rock to
    identify overloads and help with trade-off decisions.
    """

    __tablename__ = "workloads"

    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    big_rock_id = Column(Integer, ForeignKey("big_rocks.id"), nullable=True)

    # Load estimates
    estimated_hours = Column(Float, default=0.0)
    available_hours = Column(Float, default=0.0)
    load_percentage = Column(Float, default=0.0)  # (estimated/available) * 100

    # Alerts
    at_risk = Column(Boolean, default=False)
    risk_reason = Column(Text, nullable=True)

    calculated_at = Column(DateTime, default=utc_now)

    # Relationships
    big_rock = relationship("BigRock")

    def __repr__(self):
        return f"<Workload(big_rock_id={self.big_rock_id}, load={self.load_percentage}%)>"


class DailyLog(Base):
    """
    Daily Log - Habit and energy tracking.

    Daily log to learn patterns of sleep, energy and productivity.
    """

    __tablename__ = "daily_logs"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uix_user_date"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date = Column(Date, nullable=False)

    # Sleep
    wake_time = Column(String(5), nullable=True)  # HH:MM
    sleep_time = Column(String(5), nullable=True)  # HH:MM
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(
        Integer, CheckConstraint("sleep_quality BETWEEN 1 AND 10"), nullable=True
    )

    # Energy throughout the day
    morning_energy = Column(
        Integer, CheckConstraint("morning_energy BETWEEN 1 AND 10"), nullable=True
    )
    afternoon_energy = Column(
        Integer, CheckConstraint("afternoon_energy BETWEEN 1 AND 10"), nullable=True
    )
    evening_energy = Column(
        Integer, CheckConstraint("evening_energy BETWEEN 1 AND 10"), nullable=True
    )

    # Productivity
    deep_work_hours = Column(Float, default=0.0)
    completed_tasks = Column(Integer, default=0)

    # Context
    cycle_phase = Column(String(20), nullable=True)
    special_events = Column(Text, nullable=True)  # Comma-separated
    free_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User", back_populates="daily_logs")

    def __repr__(self):
        return f"<DailyLog(date={self.date}, user_id={self.user_id})>"


# ==================== Settings Model ====================


class UserSettings(Base):
    """
    User Settings - User preferences and configuration.

    Stores user-specific settings and preferences.
    """

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Display preferences
    theme = Column(String(20), default="auto")  # auto, light, dark
    density = Column(String(20), default="comfortable")  # compact, comfortable, spacious
    timezone = Column(String(50), default="America/Sao_Paulo")
    language = Column(String(10), default="pt-BR")

    # Notification preferences
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)

    # Work preferences
    work_hours_per_day = Column(Integer, default=8)
    work_days_per_week = Column(Integer, default=5)
    planning_horizon_days = Column(Integer, default=7)

    # Wellness preferences
    cycle_tracking_enabled = Column(Boolean, default=True)
    cycle_length_days = Column(Integer, default=28)

    # Integration settings (JSON for flexibility)
    integrations = Column(JSON, default={})
    # Example: {"google_calendar": {"enabled": false}, "notion": {"enabled": false}}

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<UserSettings(user_id={self.user_id}, theme='{self.theme}')>"


# ==================== Integration Layer Models (V3.1) ====================


class SystemEvent(Base):
    """
    System Event - Event Bus for inter-module communication.

    Stores all events that occur in the system for pub/sub architecture.
    Enables modules to communicate asynchronously.
    """

    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)

    # Event identification
    tipo = Column(String(100), nullable=False, index=True)
    # Examples: 'task_created', 'project_accepted', 'focus_started',
    # 'cycle_phase_changed', 'capacity_alert', 'okr_updated'

    modulo_origem = Column(String(50), nullable=False, index=True)
    # Examples: 'task_manager', 'projects', 'focus', 'wellness', 'capacity'

    # Event data
    payload = Column(JSON, nullable=False)
    # Event-specific data

    # Processing
    prioridade = Column(Integer, default=5, index=True)
    processado = Column(Boolean, default=False, index=True)

    # Timestamps
    criado_em = Column(DateTime, default=utc_now, index=True)
    processado_em = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<SystemEvent(id={self.id}, tipo='{self.tipo}', origem='{self.modulo_origem}')>"


class GlobalContext(Base):
    """
    Global Context - Snapshot of current system state.

    Maintains a holistic view of user's current context including
    wellness, capacity, focus state, etc. Used for context-aware decisions.
    """

    __tablename__ = "global_context"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Current state
    fase_ciclo = Column(String(20), nullable=True)
    energia_atual = Column(Integer, CheckConstraint("energia_atual BETWEEN 1 AND 10"), default=7)
    carga_trabalho_percentual = Column(Float, default=50.0)
    em_sessao_foco = Column(Boolean, default=False)

    # Aggregated metrics
    tarefas_pendentes = Column(Integer, default=0)
    projetos_ativos = Column(Integer, default=0)
    notificacoes_nao_lidas = Column(Integer, default=0)

    # Temporal context
    hora_dia = Column(Integer, CheckConstraint("hora_dia BETWEEN 0 AND 23"), nullable=True)
    dia_semana = Column(Integer, CheckConstraint("dia_semana BETWEEN 0 AND 6"), nullable=True)
    periodo_produtivo = Column(String(20), nullable=True)
    # Examples: 'manha', 'tarde', 'noite'

    # Emotional state (inferred)
    nivel_stress = Column(Integer, CheckConstraint("nivel_stress BETWEEN 1 AND 10"), default=5)
    necessita_pausa = Column(Boolean, default=False)

    # Timestamps
    atualizado_em = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<GlobalContext(user_id={self.user_id}, fase='{self.fase_ciclo}', energia={self.energia_atual})>"


class CrossModuleRelation(Base):
    """
    Cross Module Relation - Links between entities from different modules.

    Tracks relationships between entities across different modules
    (e.g., project → task, notification → task, task → okr).
    """

    __tablename__ = "cross_module_relations"

    id = Column(Integer, primary_key=True, index=True)

    # Relation type
    tipo_relacao = Column(String(50), nullable=False, index=True)
    # Examples: 'project_to_task', 'notification_to_task',
    # 'task_to_okr', 'project_to_portfolio'

    # Origin entity
    modulo_origem = Column(String(50), nullable=False, index=True)
    entidade_origem_id = Column(Integer, nullable=False, index=True)

    # Destination entity
    modulo_destino = Column(String(50), nullable=False, index=True)
    entidade_destino_id = Column(Integer, nullable=False, index=True)

    # Additional metadata
    relation_metadata = Column(JSON, nullable=True)

    # Timestamps
    criado_em = Column(DateTime, default=utc_now)

    def __repr__(self):
        return f"<CrossModuleRelation(tipo='{self.tipo_relacao}', {self.modulo_origem}→{self.modulo_destino})>"


class IntegratedDecision(Base):
    """
    Integrated Decision - Cross-module decisions.

    Records decisions that involve multiple modules and require
    holistic context consideration.
    """

    __tablename__ = "integrated_decisions"

    id = Column(Integer, primary_key=True, index=True)

    # Decision context
    situacao = Column(Text, nullable=False)
    # Description of the situation requiring decision

    modulos_envolvidos = Column(JSON, nullable=False)
    # List of modules involved in the decision

    contexto_considerado = Column(JSON, nullable=False)
    # Snapshot of context at decision time

    # Decision process
    opcoes_avaliadas = Column(JSON, nullable=True)
    # List of options that were considered

    decisao_tomada = Column(Text, nullable=False)
    justificativa = Column(Text, nullable=False)

    # Execution
    executado = Column(Boolean, default=False)
    resultado = Column(Text, nullable=True)

    # Timestamps
    criado_em = Column(DateTime, default=utc_now, index=True)

    def __repr__(self):
        return f"<IntegratedDecision(id={self.id}, modulos={len(self.modulos_envolvidos)}, executado={self.executado})>"


# Additional indexes for V2
# CREATE INDEX idx_cycle_date ON menstrual_cycles(start_date);
# CREATE INDEX idx_workload_period ON workloads(period_start, period_end);
# CREATE INDEX idx_daily_log_date ON daily_logs(date);

# Additional indexes for V3.1 (Integration Layer)
# CREATE INDEX idx_events_tipo_processado ON system_events(tipo, processado);
# CREATE INDEX idx_events_prioridade ON system_events(prioridade DESC, criado_em);
# CREATE INDEX idx_cross_module_origem ON cross_module_relations(modulo_origem, entidade_origem_id);
# CREATE INDEX idx_cross_module_destino ON cross_module_relations(modulo_destino, entidade_destino_id);


# ==================== Freelance System Models ====================


class FreelanceProject(Base):
    """
    Freelance Project - Client projects and contracts.

    Represents freelance projects with client information, rates,
    deadlines, and project status tracking.
    """

    __tablename__ = "freelance_projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Project information
    client_name = Column(String(200), nullable=False)
    project_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Financial
    hourly_rate = Column(Float, nullable=False)  # Rate per hour
    estimated_hours = Column(Float, nullable=False)  # Estimated total hours
    actual_hours = Column(Float, default=0.0)  # Actual hours worked (computed from WorkLog)

    # Scheduling
    start_date = Column(Date, nullable=True)
    deadline = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)

    # Status tracking
    status = Column(
        String(20),
        CheckConstraint("status IN ('proposal', 'active', 'completed', 'cancelled')"),
        default="proposal",
        index=True,
    )

    # Project metadata
    notes = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    work_logs = relationship("WorkLog", back_populates="project", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FreelanceProject(id={self.id}, client='{self.client_name}', project='{self.project_name}', status='{self.status}')>"

    def calculate_total_value(self) -> float:
        """Calculate total project value based on actual hours worked."""
        return self.actual_hours * self.hourly_rate

    def calculate_estimated_value(self) -> float:
        """Calculate estimated project value based on estimated hours."""
        return self.estimated_hours * self.hourly_rate

    def update_actual_hours(self, db_session):
        """Update actual_hours from work logs."""
        from sqlalchemy import func

        total = (
            db_session.query(func.sum(WorkLog.hours)).filter(WorkLog.project_id == self.id).scalar()
        )
        self.actual_hours = total or 0.0


class WorkLog(Base):
    """
    Work Log - Time tracking for freelance projects.

    Records hours worked on specific projects with descriptions
    for accurate time tracking and invoicing.
    """

    __tablename__ = "work_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id = Column(
        Integer,
        ForeignKey("freelance_projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Time tracking
    work_date = Column(Date, nullable=False, index=True)
    hours = Column(Float, nullable=False)
    description = Column(Text, nullable=False)

    # Optional categorization
    task_type = Column(String(50), nullable=True)  # e.g., 'development', 'design', 'meeting'

    # Billing
    billable = Column(Boolean, default=True)
    invoiced = Column(Boolean, default=False, index=True)  # Has this been included in an invoice?
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    project = relationship("FreelanceProject", back_populates="work_logs")
    invoice = relationship("Invoice", back_populates="work_logs")

    def __repr__(self):
        return f"<WorkLog(id={self.id}, project_id={self.project_id}, date={self.work_date}, hours={self.hours})>"

    def calculate_amount(self) -> float:
        """Calculate billable amount for this work log."""
        if not self.billable or not self.project:
            return 0.0
        return self.hours * self.project.hourly_rate


class Invoice(Base):
    """
    Invoice - Financial invoices for freelance projects.

    Generates invoices for projects based on work logs,
    tracks payment status and financial records.
    """

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id = Column(Integer, ForeignKey("freelance_projects.id"), nullable=False, index=True)

    # Invoice details
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    issue_date = Column(Date, nullable=False, index=True)
    due_date = Column(Date, nullable=True)

    # Financial
    total_amount = Column(Float, nullable=False)
    total_hours = Column(Float, nullable=False)
    hourly_rate = Column(Float, nullable=False)  # Rate at time of invoicing

    # Payment tracking
    status = Column(
        String(20),
        CheckConstraint("status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')"),
        default="draft",
        index=True,
    )
    paid_date = Column(Date, nullable=True)
    payment_method = Column(String(50), nullable=True)

    # Additional info
    notes = Column(Text, nullable=True)
    payment_terms = Column(Text, nullable=True)  # e.g., "Net 30", "Due on receipt"

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    project = relationship("FreelanceProject", back_populates="invoices")
    work_logs = relationship("WorkLog", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', amount={self.total_amount}, status='{self.status}')>"

    def mark_as_paid(self, payment_date=None, payment_method=None):
        """Mark invoice as paid."""
        self.status = "paid"
        self.paid_date = payment_date or datetime.now(timezone.utc).date()
        if payment_method:
            self.payment_method = payment_method
        self.updated_at = datetime.now(timezone.utc)


# Additional indexes for Freelance System
# CREATE INDEX idx_freelance_projects_status ON freelance_projects(status);
# CREATE INDEX idx_freelance_projects_deadline ON freelance_projects(deadline);
# CREATE INDEX idx_work_logs_date ON work_logs(work_date);
# CREATE INDEX idx_work_logs_invoiced ON work_logs(invoiced);
# CREATE INDEX idx_invoices_status ON invoices(status);
# CREATE INDEX idx_invoices_issue_date ON invoices(issue_date);


# ==================== Projects Intelligence System Models ====================


class FreelancePlatform(Base):
    """
    Freelance Platform - External platforms for project collection.

    Represents external freelance platforms (Upwork, Freelancer.com, etc.)
    with API credentials and monitoring configuration.
    """

    __tablename__ = "freelance_platforms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Platform information
    name = Column(String(100), nullable=False)  # 'Upwork', 'Freelancer.com', 'Fiverr', etc.
    platform_type = Column(String(50), nullable=True)  # 'marketplace', 'network', 'direct'
    website_url = Column(String(255), nullable=True)

    # API configuration (encrypted in production)
    api_config = Column(JSON, nullable=True)  # API keys, OAuth tokens, webhooks, etc.

    # Status
    active = Column(Boolean, default=True, index=True)
    last_collection_at = Column(DateTime, nullable=True)
    last_collection_count = Column(Integer, default=0)

    # Collection settings
    collection_interval_minutes = Column(Integer, default=60)  # How often to collect
    auto_collect = Column(Boolean, default=False)

    # Statistics
    total_projects_collected = Column(Integer, default=0)
    total_projects_accepted = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    opportunities = relationship(
        "FreelanceOpportunity", back_populates="platform", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<FreelancePlatform(id={self.id}, name='{self.name}', active={self.active})>"


class FreelanceOpportunity(Base):
    """
    Freelance Opportunity - Projects collected from platforms.

    Represents project opportunities collected from external platforms
    with semantic analysis, scoring, and AI recommendations.
    """

    __tablename__ = "freelance_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform_id = Column(Integer, ForeignKey("freelance_platforms.id"), nullable=True, index=True)

    # Original data from platform
    external_id = Column(String(100), nullable=True, index=True)  # Platform's project ID
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)

    # Client information
    client_name = Column(String(200), nullable=True)
    client_rating = Column(Float, nullable=True)
    client_country = Column(String(100), nullable=True)
    client_projects_count = Column(Integer, nullable=True)

    # Technical requirements
    required_skills = Column(JSON, nullable=True)  # List of required skills/technologies
    skill_level = Column(String(20), nullable=True)  # 'junior', 'mid', 'senior', 'expert'
    category = Column(
        String(50), nullable=True
    )  # 'full_stack', 'backend', 'frontend', 'ai_ml', 'devops', etc.

    # Commercial conditions
    client_budget = Column(Float, nullable=True)
    client_currency = Column(String(10), default="USD")
    client_deadline_days = Column(Integer, nullable=True)
    contract_type = Column(String(20), nullable=True)  # 'fixed_price', 'hourly', 'milestone'

    # AI Analysis - Estimations
    estimated_complexity = Column(
        Integer, CheckConstraint("estimated_complexity BETWEEN 1 AND 10"), nullable=True
    )
    estimated_hours = Column(Float, nullable=True)
    suggested_price = Column(Float, nullable=True)
    suggested_deadline_days = Column(Integer, nullable=True)

    # AI Analysis - Scoring (0.0 to 1.0)
    viability_score = Column(Float, nullable=True)  # Financial viability
    alignment_score = Column(Float, nullable=True)  # Skill alignment with user
    strategic_score = Column(Float, nullable=True)  # Career value
    final_score = Column(Float, nullable=True, index=True)  # Weighted average

    # AI Analysis - Recommendation
    recommendation = Column(
        String(20),
        CheckConstraint("recommendation IN ('accept', 'negotiate', 'reject', 'pending')"),
        default="pending",
        index=True,
    )
    recommendation_reason = Column(Text, nullable=True)

    # Semantic Analysis
    client_intent = Column(String(50), nullable=True)  # 'serious_project', 'test', 'exploration'
    red_flags = Column(JSON, nullable=True)  # List of warning signs
    opportunities = Column(JSON, nullable=True)  # List of positive aspects
    extracted_context = Column(JSON, nullable=True)  # Full semantic analysis

    # Embeddings for similarity search
    description_embedding = Column(Vector(1536), nullable=True)  # OpenAI ada-002 embeddings

    # Status and decision
    status = Column(
        String(20),
        CheckConstraint(
            "status IN ('new', 'analyzed', 'negotiating', 'accepted', 'rejected', 'expired')"
        ),
        default="new",
        index=True,
    )
    final_decision = Column(String(20), nullable=True)  # 'accepted', 'rejected', 'no_response'
    decision_reason = Column(Text, nullable=True)

    # Timestamps
    collected_at = Column(DateTime, default=utc_now, index=True)
    analyzed_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # When opportunity expires on platform

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    platform = relationship("FreelancePlatform", back_populates="opportunities")
    negotiations = relationship(
        "Negotiation", back_populates="opportunity", cascade="all, delete-orphan"
    )
    execution = relationship("ProjectExecution", back_populates="opportunity", uselist=False)

    def __repr__(self):
        return f"<FreelanceOpportunity(id={self.id}, title='{self.title[:40]}...', score={self.final_score})>"


class ProjectExecution(Base):
    """
    Project Execution - Detailed execution tracking of accepted projects.

    Tracks the execution of accepted freelance opportunities with
    detailed metrics, learnings, and career impact assessment.
    """

    __tablename__ = "project_executions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id = Column(
        Integer, ForeignKey("freelance_opportunities.id"), nullable=True, index=True
    )
    freelance_project_id = Column(
        Integer, ForeignKey("freelance_projects.id"), nullable=True, index=True
    )

    # Planning
    start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=True)
    actual_end_date = Column(Date, nullable=True)

    # Time investment
    planned_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, default=0.0)
    hours_variance_percentage = Column(Float, nullable=True)  # Difference from estimate

    # Financial
    negotiated_value = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    received_value = Column(Float, nullable=True)
    payment_date = Column(Date, nullable=True)

    # Client evaluation
    client_satisfaction = Column(
        Integer, CheckConstraint("client_satisfaction BETWEEN 1 AND 5"), nullable=True
    )
    client_rating_received = Column(Float, nullable=True)
    client_feedback = Column(Text, nullable=True)
    client_testimonial = Column(Text, nullable=True)

    # Personal evaluation
    actual_difficulty = Column(
        Integer, CheckConstraint("actual_difficulty BETWEEN 1 AND 10"), nullable=True
    )
    learnings = Column(JSON, nullable=True)  # List of key learnings
    challenges_faced = Column(JSON, nullable=True)  # List of challenges
    personal_notes = Column(Text, nullable=True)

    # Career impact
    new_skills_acquired = Column(JSON, nullable=True)  # Skills learned during project
    technologies_used = Column(JSON, nullable=True)  # Technologies actually used
    portfolio_worthy = Column(Boolean, default=False)
    testimonial_obtained = Column(Boolean, default=False)
    referral_potential = Column(Boolean, default=False)

    # Status
    status = Column(
        String(20),
        CheckConstraint(
            "status IN ('planned', 'in_progress', 'completed', 'cancelled', 'on_hold')"
        ),
        default="planned",
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    opportunity = relationship("FreelanceOpportunity", back_populates="execution")
    freelance_project = relationship("FreelanceProject")
    portfolio_item = relationship("PortfolioItem", back_populates="execution", uselist=False)

    def __repr__(self):
        return f"<ProjectExecution(id={self.id}, status='{self.status}', value={self.negotiated_value})>"

    def calculate_hourly_rate(self) -> float:
        """Calculate actual hourly rate earned."""
        if self.actual_hours and self.actual_hours > 0:
            return (self.received_value or self.negotiated_value) / self.actual_hours
        return 0.0


class PricingParameter(Base):
    """
    Pricing Parameter - Dynamic pricing configuration.

    Stores versioned pricing parameters that evolve through learning.
    Defines base rates and multiplier factors for strategic pricing.
    """

    __tablename__ = "pricing_parameters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version = Column(Integer, nullable=False)

    # Base values
    base_hourly_rate = Column(Float, nullable=False)  # Base hourly rate
    minimum_margin = Column(Float, default=0.20)  # Minimum 20% margin
    currency = Column(String(10), default="USD")

    # Multiplier factors (stored as JSON for flexibility)
    complexity_factors = Column(JSON, nullable=True)
    # Example: {"1-2": 0.8, "3-4": 1.0, "5-6": 1.3, "7-8": 1.6, "9-10": 2.0}

    specialization_factors = Column(JSON, nullable=True)
    # Example: {"ai_ml": 1.5, "blockchain": 1.4, "full_stack": 1.2, "frontend": 1.0}

    deadline_factors = Column(JSON, nullable=True)
    # Example: {"urgent_<7days": 1.5, "short_7-14days": 1.2, "normal_15-30days": 1.0}

    client_factors = Column(JSON, nullable=True)
    # Example: {"new_no_rating": 1.1, "good_rating": 1.0, "excellent_rating": 0.95}

    # Limits
    minimum_project_value = Column(Float, default=500.0)
    minimum_deadline_days = Column(Integer, default=7)

    # Learning metadata
    auto_adjusted = Column(Boolean, default=False)
    based_on_executions_count = Column(Integer, default=0)
    adjustment_reason = Column(Text, nullable=True)

    # Status
    active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    activated_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<PricingParameter(id={self.id}, version={self.version}, base_rate={self.base_hourly_rate}, active={self.active})>"


class Negotiation(Base):
    """
    Negotiation - Project negotiation history.

    Tracks negotiation attempts with counter-proposals,
    client responses, and final outcomes.
    """

    __tablename__ = "negotiations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id = Column(
        Integer, ForeignKey("freelance_opportunities.id"), nullable=False, index=True
    )

    # Original proposal
    original_budget = Column(Float, nullable=True)
    original_deadline_days = Column(Integer, nullable=True)

    # Counter-proposal
    counter_proposal_budget = Column(Float, nullable=False)
    counter_proposal_deadline_days = Column(Integer, nullable=True)
    counter_proposal_justification = Column(Text, nullable=False)
    generated_message = Column(Text, nullable=True)  # AI-generated diplomatic message

    # Client response
    client_response = Column(Text, nullable=True)
    final_agreed_budget = Column(Float, nullable=True)
    final_agreed_deadline_days = Column(Integer, nullable=True)

    # Outcome
    outcome = Column(
        String(20),
        CheckConstraint("outcome IN ('accepted', 'rejected', 'agreed', 'no_response', 'pending')"),
        default="pending",
        index=True,
    )
    outcome_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    responded_at = Column(DateTime, nullable=True)
    finalized_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    opportunity = relationship("FreelanceOpportunity", back_populates="negotiations")

    def __repr__(self):
        return f"<Negotiation(id={self.id}, opportunity_id={self.opportunity_id}, outcome='{self.outcome}')>"


class CareerInsight(Base):
    """
    Career Insight - Strategic career analytics and insights.

    Generates periodic reports with financial, technical, and
    strategic insights about career evolution and positioning.
    """

    __tablename__ = "career_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Report period
    period_start = Column(Date, nullable=False, index=True)
    period_end = Column(Date, nullable=False, index=True)
    report_type = Column(
        String(20), nullable=False, index=True
    )  # 'weekly', 'monthly', 'quarterly', 'annual'

    # Financial metrics
    total_revenue = Column(Float, default=0.0)
    average_project_value = Column(Float, nullable=True)
    effective_hourly_rate = Column(Float, nullable=True)  # Total revenue / total hours
    currency = Column(String(10), default="USD")

    # Productivity metrics
    projects_completed = Column(Integer, default=0)
    success_rate = Column(Float, nullable=True)  # % of successfully completed projects
    total_hours_worked = Column(Float, default=0.0)
    average_hours_per_project = Column(Float, nullable=True)

    # Technical evolution
    average_complexity = Column(Float, nullable=True)
    new_technologies = Column(JSON, nullable=True)  # Technologies learned this period
    dominant_categories = Column(JSON, nullable=True)  # Most worked categories

    # Market positioning
    most_profitable_categories = Column(JSON, nullable=True)  # Categories with best rates
    preferred_clients = Column(JSON, nullable=True)  # Client profiles that work best
    identified_trends = Column(JSON, nullable=True)  # Market trends observed

    # Strategic recommendations
    recommendations = Column(JSON, nullable=True)  # List of strategic recommendations
    next_step_suggestion = Column(Text, nullable=True)  # Primary suggestion for next period

    # Skills analysis
    top_demanded_skills = Column(JSON, nullable=True)
    skill_gaps = Column(JSON, nullable=True)  # Skills to develop
    competitive_advantages = Column(JSON, nullable=True)  # Unique strengths

    # Generated by AI
    ai_generated_summary = Column(Text, nullable=True)
    ai_confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0

    # Timestamps
    generated_at = Column(DateTime, default=utc_now)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<CareerInsight(id={self.id}, period={self.period_start} to {self.period_end}, type='{self.report_type}')>"


class PortfolioItem(Base):
    """
    Portfolio Item - Automated portfolio generation.

    AI-generated portfolio items from completed projects
    with optimized descriptions and highlighting achievements.
    """

    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    execution_id = Column(Integer, ForeignKey("project_executions.id"), nullable=True, index=True)

    # Portfolio content
    title = Column(String(200), nullable=False)
    optimized_description = Column(Text, nullable=False)  # AI-enhanced description
    technologies_used = Column(JSON, nullable=True)
    challenges_overcome = Column(JSON, nullable=True)
    results_metrics = Column(JSON, nullable=True)  # Quantifiable results

    # Media
    images_urls = Column(JSON, nullable=True)
    demo_url = Column(String(500), nullable=True)
    case_study_url = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)

    # Categorization
    featured = Column(Boolean, default=False, index=True)
    category = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)

    # Visibility
    public = Column(Boolean, default=True)
    published_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")
    execution = relationship("ProjectExecution", back_populates="portfolio_item")

    def __repr__(self):
        return (
            f"<PortfolioItem(id={self.id}, title='{self.title[:40]}...', featured={self.featured})>"
        )


class LearningRecord(Base):
    """
    Learning Record - Continuous learning and model improvement.

    Records feedback and outcomes to improve AI predictions
    for pricing, classification, and recommendations.
    """

    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Learning type
    learning_type = Column(
        String(50), nullable=False, index=True
    )  # 'pricing', 'classification', 'negotiation', 'time_estimation'

    # Model input/output
    input_features = Column(JSON, nullable=False)  # Features used for prediction
    predicted_output = Column(JSON, nullable=True)  # What the model predicted
    actual_output = Column(JSON, nullable=True)  # What actually happened

    # Performance metrics
    accuracy_score = Column(Float, nullable=True)  # How accurate was the prediction
    error_margin = Column(Float, nullable=True)  # Margin of error

    # User feedback
    user_feedback = Column(Text, nullable=True)  # Manual feedback from user
    user_rating = Column(Integer, CheckConstraint("user_rating BETWEEN 1 AND 5"), nullable=True)

    # Adjustment tracking
    adjustment_applied = Column(Boolean, default=False)
    adjustment_impact = Column(Text, nullable=True)  # Description of adjustment made

    # Context
    related_opportunity_id = Column(
        Integer, ForeignKey("freelance_opportunities.id"), nullable=True
    )
    related_execution_id = Column(Integer, ForeignKey("project_executions.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now, index=True)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<LearningRecord(id={self.id}, type='{self.learning_type}', accuracy={self.accuracy_score})>"


class PersonalReflection(Base):
    """
    Personal Reflection - Qualitative insights and observations.

    Stores personal reflections, learnings, and insights that
    complement quantitative data with qualitative context.
    """

    __tablename__ = "personal_reflections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Reflection content
    date = Column(Date, nullable=False, index=True)
    category = Column(
        String(50), nullable=True, index=True
    )  # 'learning', 'challenge', 'achievement', 'insight', 'goal'
    content = Column(Text, nullable=False)

    # Sentiment analysis
    sentiment = Column(
        String(20), nullable=True
    )  # 'positive', 'neutral', 'challenging', 'frustrated'
    tags = Column(JSON, nullable=True)

    # Relations
    related_to_type = Column(String(50), nullable=True)  # 'opportunity', 'execution', 'client'
    related_to_id = Column(Integer, nullable=True)

    # Action tracking
    action_taken = Column(Text, nullable=True)  # What was done about this reflection
    action_result = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<PersonalReflection(id={self.id}, date={self.date}, category='{self.category}')>"


# Additional indexes for Projects Intelligence System
# CREATE INDEX idx_platforms_active ON freelance_platforms(active, user_id);
# CREATE INDEX idx_opportunities_score ON freelance_opportunities(final_score DESC);
# CREATE INDEX idx_opportunities_status_recommendation ON freelance_opportunities(status, recommendation);
# CREATE INDEX idx_opportunities_collected ON freelance_opportunities(collected_at DESC);
# CREATE INDEX idx_opportunities_embedding ON freelance_opportunities USING ivfflat(description_embedding vector_cosine_ops);
# CREATE INDEX idx_executions_dates ON project_executions(start_date, actual_end_date);
# CREATE INDEX idx_executions_status ON project_executions(status);
# CREATE INDEX idx_pricing_active ON pricing_parameters(active, user_id, version DESC);
# CREATE INDEX idx_negotiations_outcome ON negotiations(outcome);
# CREATE INDEX idx_insights_period ON career_insights(period_start, period_end);
# CREATE INDEX idx_portfolio_featured ON portfolio_items(featured, public);
# CREATE INDEX idx_learning_type ON learning_records(learning_type, created_at DESC);
# CREATE INDEX idx_reflections_date ON personal_reflections(date DESC);
