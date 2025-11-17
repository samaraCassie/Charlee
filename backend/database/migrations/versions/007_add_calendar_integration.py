"""add calendar integration (Google Calendar, Microsoft Outlook)

Revision ID: 007
Revises: 006
Create Date: 2025-11-16 23:30:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    """Add calendar integration tables."""

    # Create calendar_connections table
    op.create_table(
        "calendar_connections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "provider",
            sa.String(length=20),
            sa.CheckConstraint("provider IN ('google', 'microsoft')"),
            nullable=False,
        ),
        sa.Column("calendar_id", sa.String(length=255), nullable=False),
        sa.Column("calendar_name", sa.String(length=255), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("sync_enabled", sa.Boolean(), server_default=sa.text("1")),
        sa.Column(
            "sync_direction",
            sa.String(length=20),
            sa.CheckConstraint("sync_direction IN ('both', 'to_calendar', 'from_calendar')"),
            server_default="both",
        ),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("sync_token", sa.String(length=500), nullable=True),
        sa.Column("webhook_id", sa.String(length=255), nullable=True),
        sa.Column("webhook_expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "provider", "calendar_id", name="uq_user_provider_calendar"),
    )
    op.create_index(
        op.f("ix_calendar_connections_id"),
        "calendar_connections",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_connections_user_id"),
        "calendar_connections",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_connections_provider"),
        "calendar_connections",
        ["provider"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_connections_sync_enabled",
        "calendar_connections",
        ["sync_enabled"],
        unique=False,
    )

    # Create calendar_events table
    op.create_table(
        "calendar_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("external_event_id", sa.String(length=255), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("all_day", sa.Boolean(), server_default="false"),
        sa.Column("location", sa.String(length=500), nullable=True),
        sa.Column("attendees", sa.Text(), nullable=True),
        sa.Column("is_recurring", sa.Boolean(), server_default="false"),
        sa.Column("recurrence_rule", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('confirmed', 'tentative', 'cancelled')"),
            server_default="confirmed",
        ),
        sa.Column(
            "source",
            sa.String(length=20),
            sa.CheckConstraint("source IN ('charlee', 'external')"),
            nullable=False,
        ),
        sa.Column("last_modified_at", sa.DateTime(), nullable=True),
        sa.Column("charlee_modified_at", sa.DateTime(), nullable=True),
        sa.Column("external_modified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["connection_id"], ["calendar_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "connection_id",
            "external_event_id",
            name="uq_connection_external_event",
        ),
    )
    op.create_index(
        op.f("ix_calendar_events_id"),
        "calendar_events",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_connection_id"),
        "calendar_events",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_user_id"),
        "calendar_events",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_events_task_id"),
        "calendar_events",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_events_start_time",
        "calendar_events",
        ["start_time"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_events_status",
        "calendar_events",
        ["status"],
        unique=False,
    )
    # Compound index for efficient queries
    op.create_index(
        "ix_calendar_events_user_start_time",
        "calendar_events",
        ["user_id", "start_time"],
        unique=False,
    )

    # Create calendar_sync_logs table
    op.create_table(
        "calendar_sync_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "sync_type",
            sa.String(length=20),
            sa.CheckConstraint("sync_type IN ('manual', 'scheduled', 'webhook')"),
            nullable=False,
        ),
        sa.Column(
            "direction",
            sa.String(length=20),
            sa.CheckConstraint("direction IN ('to_calendar', 'from_calendar', 'both')"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('started', 'success', 'failed', 'partial')"),
            nullable=False,
        ),
        sa.Column("events_created", sa.Integer(), server_default="0"),
        sa.Column("events_updated", sa.Integer(), server_default="0"),
        sa.Column("events_deleted", sa.Integer(), server_default="0"),
        sa.Column("conflicts_detected", sa.Integer(), server_default="0"),
        sa.Column("conflicts_resolved", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["connection_id"], ["calendar_connections.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_sync_logs_id"),
        "calendar_sync_logs",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_sync_logs_connection_id"),
        "calendar_sync_logs",
        ["connection_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_sync_logs_user_id"),
        "calendar_sync_logs",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_sync_logs_status",
        "calendar_sync_logs",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_sync_logs_started_at",
        "calendar_sync_logs",
        ["started_at"],
        unique=False,
    )

    # Create calendar_conflicts table
    op.create_table(
        "calendar_conflicts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "conflict_type",
            sa.String(length=50),
            sa.CheckConstraint(
                "conflict_type IN ('both_modified', 'time_conflict', 'duplicate', 'deletion_conflict')"
            ),
            nullable=False,
        ),
        sa.Column("charlee_version", sa.JSON(), nullable=True),
        sa.Column("external_version", sa.JSON(), nullable=True),
        sa.Column(
            "resolution_strategy",
            sa.String(length=50),
            sa.CheckConstraint(
                "resolution_strategy IN ('last_modified_wins', 'manual', 'charlee_wins', 'external_wins', 'merge')"
            ),
            server_default="last_modified_wins",
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('detected', 'resolved', 'manual_review')"),
            server_default="detected",
        ),
        sa.Column("resolved_version", sa.JSON(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_by", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["event_id"], ["calendar_events.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calendar_conflicts_id"),
        "calendar_conflicts",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_conflicts_event_id"),
        "calendar_conflicts",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_calendar_conflicts_user_id"),
        "calendar_conflicts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_conflicts_status",
        "calendar_conflicts",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_calendar_conflicts_conflict_type",
        "calendar_conflicts",
        ["conflict_type"],
        unique=False,
    )


def downgrade():
    """Remove calendar integration tables."""
    op.drop_index("ix_calendar_conflicts_conflict_type", table_name="calendar_conflicts")
    op.drop_index("ix_calendar_conflicts_status", table_name="calendar_conflicts")
    op.drop_index(op.f("ix_calendar_conflicts_user_id"), table_name="calendar_conflicts")
    op.drop_index(op.f("ix_calendar_conflicts_event_id"), table_name="calendar_conflicts")
    op.drop_index(op.f("ix_calendar_conflicts_id"), table_name="calendar_conflicts")
    op.drop_table("calendar_conflicts")

    op.drop_index("ix_calendar_sync_logs_started_at", table_name="calendar_sync_logs")
    op.drop_index("ix_calendar_sync_logs_status", table_name="calendar_sync_logs")
    op.drop_index(op.f("ix_calendar_sync_logs_user_id"), table_name="calendar_sync_logs")
    op.drop_index(op.f("ix_calendar_sync_logs_connection_id"), table_name="calendar_sync_logs")
    op.drop_index(op.f("ix_calendar_sync_logs_id"), table_name="calendar_sync_logs")
    op.drop_table("calendar_sync_logs")

    op.drop_index("ix_calendar_events_user_start_time", table_name="calendar_events")
    op.drop_index("ix_calendar_events_status", table_name="calendar_events")
    op.drop_index("ix_calendar_events_start_time", table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_task_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_user_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_connection_id"), table_name="calendar_events")
    op.drop_index(op.f("ix_calendar_events_id"), table_name="calendar_events")
    op.drop_table("calendar_events")

    op.drop_index("ix_calendar_connections_sync_enabled", table_name="calendar_connections")
    op.drop_index(op.f("ix_calendar_connections_provider"), table_name="calendar_connections")
    op.drop_index(op.f("ix_calendar_connections_user_id"), table_name="calendar_connections")
    op.drop_index(op.f("ix_calendar_connections_id"), table_name="calendar_connections")
    op.drop_table("calendar_connections")
