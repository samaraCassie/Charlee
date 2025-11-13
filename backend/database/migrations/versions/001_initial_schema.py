"""initial_schema_with_english_models

Revision ID: 001_initial
Revises:
Create Date: 2025-11-10 23:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create big_rocks table
    op.create_table(
        "big_rocks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True, default=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_big_rocks_id"), "big_rocks", ["id"], unique=False)

    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("big_rock_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("calculated_priority", sa.Integer(), nullable=True, default=5),
        sa.Column("priority_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("type IN ('fixed_appointment', 'task', 'continuous')"),
        sa.CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')"),
        sa.ForeignKeyConstraint(
            ["big_rock_id"],
            ["big_rocks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)

    # Create performance indexes
    op.create_index("idx_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("idx_tasks_deadline", "tasks", ["deadline"], unique=False)
    op.create_index("idx_tasks_big_rock", "tasks", ["big_rock_id"], unique=False)
    op.create_index("idx_tasks_status_deadline", "tasks", ["status", "deadline"], unique=False)

    # Create V2 tables
    op.create_table(
        "menstrual_cycles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("phase", sa.String(length=20), nullable=False),
        sa.Column("symptoms", sa.Text(), nullable=True),
        sa.Column("energy_level", sa.Integer(), nullable=True),
        sa.Column("focus_level", sa.Integer(), nullable=True),
        sa.Column("creativity_level", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("phase IN ('menstrual', 'follicular', 'ovulation', 'luteal')"),
        sa.CheckConstraint("energy_level BETWEEN 1 AND 10"),
        sa.CheckConstraint("focus_level BETWEEN 1 AND 10"),
        sa.CheckConstraint("creativity_level BETWEEN 1 AND 10"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cycle_date", "menstrual_cycles", ["start_date"], unique=False)

    op.create_table(
        "cycle_patterns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(length=20), nullable=False),
        sa.Column("identified_pattern", sa.Text(), nullable=False),
        sa.Column("average_productivity", sa.Float(), nullable=True, default=1.0),
        sa.Column("average_focus", sa.Float(), nullable=True, default=1.0),
        sa.Column("average_energy", sa.Float(), nullable=True, default=1.0),
        sa.Column("confidence_score", sa.Float(), nullable=True, default=0.0),
        sa.Column("suggestions", sa.Text(), nullable=True),
        sa.Column("samples_used", sa.Integer(), nullable=True, default=0),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("big_rock_id", sa.Integer(), nullable=True),
        sa.Column("estimated_hours", sa.Float(), nullable=True, default=0.0),
        sa.Column("available_hours", sa.Float(), nullable=True, default=0.0),
        sa.Column("load_percentage", sa.Float(), nullable=True, default=0.0),
        sa.Column("at_risk", sa.Boolean(), nullable=True, default=False),
        sa.Column("risk_reason", sa.Text(), nullable=True),
        sa.Column("calculated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["big_rock_id"],
            ["big_rocks.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_workload_period", "workloads", ["period_start", "period_end"], unique=False
    )

    op.create_table(
        "daily_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("wake_time", sa.String(length=5), nullable=True),
        sa.Column("sleep_time", sa.String(length=5), nullable=True),
        sa.Column("sleep_hours", sa.Float(), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), nullable=True),
        sa.Column("morning_energy", sa.Integer(), nullable=True),
        sa.Column("afternoon_energy", sa.Integer(), nullable=True),
        sa.Column("evening_energy", sa.Integer(), nullable=True),
        sa.Column("deep_work_hours", sa.Float(), nullable=True, default=0.0),
        sa.Column("completed_tasks", sa.Integer(), nullable=True, default=0),
        sa.Column("cycle_phase", sa.String(length=20), nullable=True),
        sa.Column("special_events", sa.Text(), nullable=True),
        sa.Column("free_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("sleep_quality BETWEEN 1 AND 10"),
        sa.CheckConstraint("morning_energy BETWEEN 1 AND 10"),
        sa.CheckConstraint("afternoon_energy BETWEEN 1 AND 10"),
        sa.CheckConstraint("evening_energy BETWEEN 1 AND 10"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date"),
    )
    op.create_index("idx_daily_log_date", "daily_logs", ["date"], unique=False)


def downgrade() -> None:
    # Drop V2 tables
    op.drop_index("idx_daily_log_date", table_name="daily_logs")
    op.drop_table("daily_logs")

    op.drop_index("idx_workload_period", table_name="workloads")
    op.drop_table("workloads")

    op.drop_table("cycle_patterns")

    op.drop_index("idx_cycle_date", table_name="menstrual_cycles")
    op.drop_table("menstrual_cycles")

    # Drop tasks table and indexes
    op.drop_index("idx_tasks_status_deadline", table_name="tasks")
    op.drop_index("idx_tasks_big_rock", table_name="tasks")
    op.drop_index("idx_tasks_deadline", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")

    # Drop big_rocks table
    op.drop_index(op.f("ix_big_rocks_id"), table_name="big_rocks")
    op.drop_table("big_rocks")
