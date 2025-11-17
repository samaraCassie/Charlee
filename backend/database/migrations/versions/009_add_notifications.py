"""add notification system (notifications and preferences)

Revision ID: 009
Revises: 008
Create Date: 2025-11-17 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade():
    """Add notification system tables."""

    # Create notifications table
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.String(length=50),
            sa.CheckConstraint(
                "type IN ('task_due_soon', 'capacity_overload', 'cycle_phase_change', 'freelance_invoice_ready', 'system', 'achievement')"
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        # Foreign keys
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for notifications
    op.create_index(
        op.f("ix_notifications_id"),
        "notifications",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_type"),
        "notifications",
        ["type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_read"),
        "notifications",
        ["read"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
    )
    # Composite indexes for common queries
    op.create_index(
        "ix_notifications_user_read",
        "notifications",
        ["user_id", "read"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_user_created",
        "notifications",
        ["user_id", sa.text("created_at DESC")],
        unique=False,
    )
    op.create_index(
        "ix_notifications_type_created",
        "notifications",
        ["type", sa.text("created_at DESC")],
        unique=False,
    )

    # Create notification_preferences table
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "notification_type",
            sa.String(length=50),
            sa.CheckConstraint(
                "notification_type IN ('task_due_soon', 'capacity_overload', 'cycle_phase_change', 'freelance_invoice_ready', 'system', 'achievement', 'all')"
            ),
            nullable=False,
        ),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("push_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        # Foreign keys
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
        # Unique constraint
        sa.UniqueConstraint("user_id", "notification_type", name="uix_user_notification_type"),
    )

    # Create indexes for notification_preferences
    op.create_index(
        op.f("ix_notification_preferences_id"),
        "notification_preferences",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_preferences_user_id"),
        "notification_preferences",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_notification_preferences_user_type",
        "notification_preferences",
        ["user_id", "notification_type"],
        unique=False,
    )


def downgrade():
    """Remove notification system tables."""

    # Drop notification_preferences indexes
    op.drop_index("ix_notification_preferences_user_type", table_name="notification_preferences")
    op.drop_index(op.f("ix_notification_preferences_user_id"), table_name="notification_preferences")
    op.drop_index(op.f("ix_notification_preferences_id"), table_name="notification_preferences")

    # Drop notification_preferences table
    op.drop_table("notification_preferences")

    # Drop notifications indexes
    op.drop_index("ix_notifications_type_created", table_name="notifications")
    op.drop_index("ix_notifications_user_created", table_name="notifications")
    op.drop_index("ix_notifications_user_read", table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_read"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")

    # Drop notifications table
    op.drop_table("notifications")
