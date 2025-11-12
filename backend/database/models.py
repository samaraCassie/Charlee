"""SQLAlchemy database models for Charlee V1."""

from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import relationship
from database.config import Base


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
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
        return datetime.utcnow() < self.locked_until

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
    created_at = Column(DateTime, default=datetime.utcnow)
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
    event_type = Column(String(50), nullable=False, index=True)  # 'login', 'logout', 'register', etc.
    event_status = Column(String(20), nullable=False)  # 'success', 'failure', 'blocked'
    event_message = Column(Text, nullable=True)

    # Request metadata
    ip_address = Column(String(50), nullable=True, index=True)
    user_agent = Column(String(255), nullable=True)
    request_path = Column(String(255), nullable=True)

    # Additional data (JSON)
    metadata = Column(JSON, nullable=True)  # Extra contextual information

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20))  # For future UI (e.g., "#FF5733")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    big_rock = relationship("BigRock", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description[:30]}...', status='{self.status}', user_id={self.user_id})>"

    def mark_as_completed(self):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reopen(self):
        """Reopen a completed task."""
        self.status = "pending"
        self.completed_at = None
        self.updated_at = datetime.utcnow()


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
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)

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

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

    calculated_at = Column(DateTime, default=datetime.utcnow)

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
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uix_user_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
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

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="daily_logs")

    def __repr__(self):
        return f"<DailyLog(date={self.date}, user_id={self.user_id})>"


# Additional indexes for V2
# CREATE INDEX idx_cycle_date ON menstrual_cycles(start_date);
# CREATE INDEX idx_workload_period ON workloads(period_start, period_end);
# CREATE INDEX idx_daily_log_date ON daily_logs(date);
