"""Add role field to users table for RBAC

Revision ID: 012_add_user_role
Revises: 011_add_performance_indexes
Create Date: 2025-12-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '012_add_user_role'
down_revision: Union[str, None] = '011_add_performance_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role column to users table."""

    # Add role column with default 'user'
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.String(20),
            nullable=False,
            server_default='user'
        )
    )

    # Add check constraint for valid roles
    op.create_check_constraint(
        'ck_users_role_valid',
        'users',
        "role IN ('user', 'admin', 'moderator')"
    )

    # Update existing superusers to have admin role
    op.execute("""
        UPDATE users
        SET role = 'admin'
        WHERE is_superuser = true
    """)

    # Create index for faster role-based queries
    op.create_index(
        'idx_users_role',
        'users',
        ['role'],
        unique=False
    )

    print("✅ Added role column to users table")
    print("✅ Migrated existing superusers to admin role")
    print("✅ Created role index for performance")


def downgrade() -> None:
    """Remove role column from users table."""

    # Drop index first
    op.drop_index('idx_users_role', table_name='users')

    # Drop check constraint
    op.drop_constraint('ck_users_role_valid', 'users', type_='check')

    # Drop column
    op.drop_column('users', 'role')

    print("🗑️  Removed role column from users table")
