"""Add pgvector extension and WorkLog table

Revision ID: 009_add_pgvector_and_worklog
Revises: 008_add_multimodal_attachments
Create Date: 2024-12-24 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "009_add_pgvector_and_worklog"
down_revision: Union[str, None] = "008_add_multimodal_attachments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""

    # 1. Enable pgvector extension
    # This requires PostgreSQL superuser privileges or the extension to be available
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    except Exception as e:
        print(f"Warning: Could not create vector extension: {e}")
        print(
            "You may need to install pgvector manually: sudo apt-get install postgresql-14-pgvector"
        )

    # 2. Create WorkLog table for time tracking
    op.create_table(
        "work_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("hours_worked", sa.Float(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "logged_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["freelance_projects.id"], ondelete="SET NULL"),
    )

    # Create indices for WorkLog
    op.create_index("ix_work_logs_user_id", "work_logs", ["user_id"])
    op.create_index("ix_work_logs_task_id", "work_logs", ["task_id"])
    op.create_index("ix_work_logs_project_id", "work_logs", ["project_id"])
    op.create_index("ix_work_logs_work_date", "work_logs", ["work_date"])
    op.create_index("ix_work_logs_logged_at", "work_logs", ["logged_at"])

    # 3. Add vector column to freelance_opportunities (if it doesn't exist)
    # Check if column exists first
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col["name"] for col in inspector.get_columns("freelance_opportunities")]

    if "embedding" not in columns:
        # Add embedding column using raw SQL for pgvector type
        try:
            op.execute("ALTER TABLE freelance_opportunities ADD COLUMN embedding vector(1536)")
            print("Added embedding column to freelance_opportunities")
        except Exception as e:
            print(f"Warning: Could not add embedding column: {e}")

    # 4. Create vector index for similarity search (HNSW or IVFFlat)
    try:
        # HNSW index is faster for similarity search
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_freelance_opportunities_embedding 
            ON freelance_opportunities 
            USING hnsw (embedding vector_cosine_ops)
        """
        )
        print("Created HNSW index for embedding similarity search")
    except Exception as e:
        print(f"Warning: Could not create HNSW index: {e}")
        # Fallback to simpler index
        try:
            op.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_freelance_opportunities_embedding 
                ON freelance_opportunities 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """
            )
            print("Created IVFFlat index as fallback")
        except Exception as e2:
            print(f"Warning: Could not create any vector index: {e2}")


def downgrade() -> None:
    """Downgrade database schema."""

    # Drop WorkLog table and indices
    op.drop_index("ix_work_logs_logged_at", table_name="work_logs")
    op.drop_index("ix_work_logs_work_date", table_name="work_logs")
    op.drop_index("ix_work_logs_project_id", table_name="work_logs")
    op.drop_index("ix_work_logs_task_id", table_name="work_logs")
    op.drop_index("ix_work_logs_user_id", table_name="work_logs")
    op.drop_table("work_logs")

    # Drop vector index
    try:
        op.execute("DROP INDEX IF EXISTS idx_freelance_opportunities_embedding")
    except:
        pass

    # Remove embedding column
    try:
        op.execute("ALTER TABLE freelance_opportunities DROP COLUMN IF EXISTS embedding")
    except:
        pass

    # Note: We don't drop the vector extension as other things might depend on it
    # op.execute('DROP EXTENSION IF EXISTS vector')
