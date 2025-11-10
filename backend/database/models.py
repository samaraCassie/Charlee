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
)
from sqlalchemy.orm import relationship
from database.config import Base


class BigRock(Base):
    """
    Big Rocks - Main life pillars.

    Represents the fundamental areas/pillars that structure
    life and tasks.
    """

    __tablename__ = "big_rocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20))  # For future UI (e.g., "#FF5733")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    tasks = relationship("Task", back_populates="big_rock")

    def __repr__(self):
        return f"<BigRock(id={self.id}, name='{self.name}')>"


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
    big_rock = relationship("BigRock", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description[:30]}...', status='{self.status}')>"

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

    def __repr__(self):
        return f"<MenstrualCycle(date={self.start_date}, phase='{self.phase}')>"


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

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)

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

    def __repr__(self):
        return f"<DailyLog(date={self.date})>"


# Additional indexes for V2
# CREATE INDEX idx_cycle_date ON menstrual_cycles(start_date);
# CREATE INDEX idx_workload_period ON workloads(period_start, period_end);
# CREATE INDEX idx_daily_log_date ON daily_logs(date);
