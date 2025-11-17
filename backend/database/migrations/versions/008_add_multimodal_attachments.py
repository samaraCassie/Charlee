"""add multimodal attachments (audio and image processing)

Revision ID: 008
Revises: 007
Create Date: 2025-11-17 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    """Add multimodal attachments table."""

    # Create attachments table
    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "file_type",
            sa.String(length=20),
            sa.CheckConstraint("file_type IN ('audio', 'image', 'document')"),
            nullable=False,
        ),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),  # Size in bytes
        sa.Column("file_url", sa.String(length=500), nullable=True),  # URL or path to stored file
        sa.Column(
            "mime_type", sa.String(length=100), nullable=True
        ),  # e.g., 'audio/mp3', 'image/png'
        # Processing metadata
        sa.Column("transcription", sa.Text(), nullable=True),  # For audio files
        sa.Column("analysis", sa.Text(), nullable=True),  # For image files
        sa.Column(
            "processing_status",
            sa.String(length=20),
            sa.CheckConstraint(
                "processing_status IN ('pending', 'processing', 'completed', 'failed')"
            ),
            server_default="completed",
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        # Additional metadata (JSON)
        sa.Column("file_metadata", sa.JSON(), nullable=True),  # Language, detected entities, etc.
        # Timestamps
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        # Foreign keys
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        # Primary key
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_attachments_id"),
        "attachments",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attachments_task_id"),
        "attachments",
        ["task_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_attachments_user_id"),
        "attachments",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_attachments_file_type",
        "attachments",
        ["file_type"],
        unique=False,
    )
    op.create_index(
        "ix_attachments_processing_status",
        "attachments",
        ["processing_status"],
        unique=False,
    )


def downgrade():
    """Remove multimodal attachments table."""

    # Drop indexes
    op.drop_index("ix_attachments_processing_status", table_name="attachments")
    op.drop_index("ix_attachments_file_type", table_name="attachments")
    op.drop_index(op.f("ix_attachments_user_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_task_id"), table_name="attachments")
    op.drop_index(op.f("ix_attachments_id"), table_name="attachments")

    # Drop table
    op.drop_table("attachments")
