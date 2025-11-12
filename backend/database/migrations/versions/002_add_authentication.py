"""add authentication system

Revision ID: 002
Revises: 001
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Create authentication tables and add user_id columns to existing tables."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('now()')),
        sa.Column('revoked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)

    # Add user_id to big_rocks table
    op.add_column('big_rocks', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_big_rocks_user_id'), 'big_rocks', ['user_id'], unique=False)
    op.create_foreign_key('fk_big_rocks_user_id', 'big_rocks', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Add user_id to tasks table
    op.add_column('tasks', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_foreign_key('fk_tasks_user_id', 'tasks', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Add user_id to menstrual_cycles table
    op.add_column('menstrual_cycles', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_menstrual_cycles_user_id'), 'menstrual_cycles', ['user_id'], unique=False)
    op.create_foreign_key('fk_menstrual_cycles_user_id', 'menstrual_cycles', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Add user_id to daily_logs table and update unique constraint
    op.add_column('daily_logs', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_daily_logs_user_id'), 'daily_logs', ['user_id'], unique=False)
    op.create_foreign_key('fk_daily_logs_user_id', 'daily_logs', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # Drop old unique constraint on date and create new one with user_id
    op.drop_constraint('daily_logs_date_key', 'daily_logs', type_='unique')
    op.create_unique_constraint('uix_user_date', 'daily_logs', ['user_id', 'date'])


def downgrade():
    """Remove authentication tables and user_id columns."""

    # Remove user_id from daily_logs and restore old constraint
    op.drop_constraint('uix_user_date', 'daily_logs', type_='unique')
    op.create_unique_constraint('daily_logs_date_key', 'daily_logs', ['date'])
    op.drop_constraint('fk_daily_logs_user_id', 'daily_logs', type_='foreignkey')
    op.drop_index(op.f('ix_daily_logs_user_id'), table_name='daily_logs')
    op.drop_column('daily_logs', 'user_id')

    # Remove user_id from menstrual_cycles
    op.drop_constraint('fk_menstrual_cycles_user_id', 'menstrual_cycles', type_='foreignkey')
    op.drop_index(op.f('ix_menstrual_cycles_user_id'), table_name='menstrual_cycles')
    op.drop_column('menstrual_cycles', 'user_id')

    # Remove user_id from tasks
    op.drop_constraint('fk_tasks_user_id', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_column('tasks', 'user_id')

    # Remove user_id from big_rocks
    op.drop_constraint('fk_big_rocks_user_id', 'big_rocks', type_='foreignkey')
    op.drop_index(op.f('ix_big_rocks_user_id'), table_name='big_rocks')
    op.drop_column('big_rocks', 'user_id')

    # Drop refresh_tokens table
    op.drop_index(op.f('ix_refresh_tokens_token'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_table('refresh_tokens')

    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
