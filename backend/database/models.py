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
    work_logs = relationship(
        "WorkLog", back_populates="project", cascade="all, delete-orphan"
    )
    invoices = relationship(
        "Invoice", back_populates="project", cascade="all, delete-orphan"
    )

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
            db_session.query(func.sum(WorkLog.hours))
            .filter(WorkLog.project_id == self.id)
            .scalar()
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
    project_id = Column(
        Integer, ForeignKey("freelance_projects.id"), nullable=False, index=True
    )

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
