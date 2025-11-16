"""add freelance system (Projects, Work Logs, Invoices)

Revision ID: 005
Revises: 004
Create Date: 2025-01-16 18:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    """Add freelance system tables."""

    # Create freelance_projects table
    op.create_table(
        "freelance_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("client_name", sa.String(length=200), nullable=False),
        sa.Column("project_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column("estimated_hours", sa.Float(), nullable=False),
        sa.Column("actual_hours", sa.Float(), server_default="0.0"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('proposal', 'active', 'completed', 'cancelled')"),
            server_default="proposal",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_freelance_projects_id"), "freelance_projects", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_freelance_projects_user_id"), "freelance_projects", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_freelance_projects_status"), "freelance_projects", ["status"], unique=False
    )
    op.create_index("ix_freelance_projects_deadline", "freelance_projects", ["deadline"], unique=False)

    # Create work_logs table
    op.create_table(
        "work_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=True),
        sa.Column("billable", sa.Boolean(), server_default="true"),
        sa.Column("invoiced", sa.Boolean(), server_default="false"),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["freelance_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_work_logs_id"), "work_logs", ["id"], unique=False)
    op.create_index(op.f("ix_work_logs_user_id"), "work_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_work_logs_project_id"), "work_logs", ["project_id"], unique=False)
    op.create_index(op.f("ix_work_logs_work_date"), "work_logs", ["work_date"], unique=False)
    op.create_index(op.f("ix_work_logs_invoiced"), "work_logs", ["invoiced"], unique=False)
    op.create_index(op.f("ix_work_logs_invoice_id"), "work_logs", ["invoice_id"], unique=False)

    # Create invoices table
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("total_hours", sa.Float(), nullable=False),
        sa.Column("hourly_rate", sa.Float(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')"),
            server_default="draft",
        ),
        sa.Column("paid_date", sa.Date(), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("payment_terms", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["freelance_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
    )
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
    op.create_index(op.f("ix_invoices_user_id"), "invoices", ["user_id"], unique=False)
    op.create_index(op.f("ix_invoices_project_id"), "invoices", ["project_id"], unique=False)
    op.create_index(
        op.f("ix_invoices_invoice_number"), "invoices", ["invoice_number"], unique=True
    )
    op.create_index(op.f("ix_invoices_issue_date"), "invoices", ["issue_date"], unique=False)
    op.create_index(op.f("ix_invoices_status"), "invoices", ["status"], unique=False)


def downgrade():
    """Remove freelance system tables."""

    # Drop work_logs table (must be first due to FK on invoices)
    op.drop_index(op.f("ix_work_logs_invoice_id"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_invoiced"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_work_date"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_project_id"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_user_id"), table_name="work_logs")
    op.drop_index(op.f("ix_work_logs_id"), table_name="work_logs")
    op.drop_table("work_logs")

    # Drop invoices table
    op.drop_index(op.f("ix_invoices_status"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_issue_date"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_project_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_user_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_table("invoices")

    # Drop freelance_projects table
    op.drop_index("ix_freelance_projects_deadline", table_name="freelance_projects")
    op.drop_index(op.f("ix_freelance_projects_status"), table_name="freelance_projects")
    op.drop_index(op.f("ix_freelance_projects_user_id"), table_name="freelance_projects")
    op.drop_index(op.f("ix_freelance_projects_id"), table_name="freelance_projects")
    op.drop_table("freelance_projects")
