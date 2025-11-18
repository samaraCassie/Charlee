"""add advanced notification system with AI classification and external sources

Revision ID: 010
Revises: 009
Create Date: 2025-11-18 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade():
    """Add advanced notification system tables and extend notifications table."""

    # Ensure pgvector extension is enabled for embeddings
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ========================================
    # 1. Create notification_sources table
    # ========================================
    op.create_table(
        "notification_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "source_type",
            sa.String(length=50),
            sa.CheckConstraint(
                "source_type IN ('email', 'slack', 'linkedin', 'github', 'whatsapp', "
                "'telegram', 'discord', 'trello', 'notion')"
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("credentials", sa.JSON(), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_sync", sa.DateTime(), nullable=True),
        sa.Column("sync_frequency_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("total_collected", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_spam_filtered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_notification_sources_id"), "notification_sources", ["id"])
    op.create_index(
        op.f("ix_notification_sources_user_id"), "notification_sources", ["user_id"]
    )
    op.create_index(
        op.f("ix_notification_sources_source_type"), "notification_sources", ["source_type"]
    )
    op.create_index(
        "ix_notification_sources_user_type",
        "notification_sources",
        ["user_id", "source_type"],
        unique=False,
    )

    # ========================================
    # 2. Extend notifications table with new fields
    # ========================================
    with op.batch_alter_table("notifications") as batch_op:
        # External source tracking
        batch_op.add_column(sa.Column("source_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("external_id", sa.String(255), nullable=True))
        batch_op.add_column(sa.Column("thread_id", sa.String(255), nullable=True))

        # AI Classification fields
        batch_op.add_column(
            sa.Column(
                "categoria",
                sa.String(50),
                sa.CheckConstraint(
                    "categoria IN ('urgente', 'importante', 'informativo', 'spam')"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("prioridade", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("contexto", sa.JSON(), nullable=True))

        # Semantic Analysis
        batch_op.add_column(
            sa.Column(
                "intencao",
                sa.String(50),
                sa.CheckConstraint(
                    "intencao IN ('solicitacao', 'informacao', 'convite', 'cobranca')"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "tom_emocional",
                sa.String(50),
                sa.CheckConstraint("tom_emocional IN ('neutro', 'urgente', 'amigavel', 'formal')"),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("entidades_extraidas", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("embedding", Vector(1536), nullable=True))

        # Automated Actions
        batch_op.add_column(
            sa.Column(
                "acao_sugerida",
                sa.String(50),
                sa.CheckConstraint(
                    "acao_sugerida IN ('responder', 'arquivar', 'criar_tarefa', 'snooze')"
                ),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("acao_executada", sa.String(50), nullable=True))
        batch_op.add_column(sa.Column("rascunho_resposta", sa.Text(), nullable=True))

        # Advanced Status
        batch_op.add_column(
            sa.Column("arquivada", sa.Boolean(), nullable=False, server_default="false")
        )
        batch_op.add_column(
            sa.Column("respondida", sa.Boolean(), nullable=False, server_default="false")
        )
        batch_op.add_column(sa.Column("snooze_until", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("tarefa_criada_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("evento_criado_id", sa.String(255), nullable=True))

        # Updated timestamp
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            )
        )

        # Add foreign key constraints
        batch_op.create_foreign_key(
            "fk_notifications_source_id",
            "notification_sources",
            ["source_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_foreign_key(
            "fk_notifications_tarefa_criada_id", "tasks", ["tarefa_criada_id"], ["id"]
        )

    # Update notification type constraint to include external sources
    op.execute(
        """
        ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_type_check;
        ALTER TABLE notifications ADD CONSTRAINT notifications_type_check CHECK (
            type IN ('task_due_soon', 'capacity_overload', 'cycle_phase_change',
                     'freelance_invoice_ready', 'system', 'achievement', 'email',
                     'slack', 'linkedin', 'github', 'whatsapp', 'telegram',
                     'discord', 'trello', 'notion')
        );
        """
    )

    # Create new indexes on notifications
    op.create_index("ix_notifications_external_id", "notifications", ["external_id"])
    op.create_index("ix_notifications_thread_id", "notifications", ["thread_id"])
    op.create_index("ix_notifications_categoria", "notifications", ["categoria"])
    op.create_index("ix_notifications_prioridade", "notifications", ["prioridade"])
    op.create_index("ix_notifications_arquivada", "notifications", ["arquivada"])
    op.create_index("ix_notifications_snooze_until", "notifications", ["snooze_until"])

    # ========================================
    # 3. Create notification_rules table
    # ========================================
    op.create_table(
        "notification_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("actions", sa.JSON(), nullable=False),
        sa.Column("times_triggered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_triggered", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_notification_rules_id"), "notification_rules", ["id"])
    op.create_index(op.f("ix_notification_rules_user_id"), "notification_rules", ["user_id"])
    op.create_index(op.f("ix_notification_rules_enabled"), "notification_rules", ["enabled"])
    op.create_index(
        "ix_notification_rules_user_enabled",
        "notification_rules",
        ["user_id", "enabled", "priority"],
    )

    # ========================================
    # 4. Create notification_digests table
    # ========================================
    op.create_table(
        "notification_digests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "digest_type",
            sa.String(50),
            sa.CheckConstraint("digest_type IN ('daily', 'weekly', 'monthly')"),
            nullable=False,
        ),
        sa.Column("period_start", sa.DateTime(), nullable=False),
        sa.Column("period_end", sa.DateTime(), nullable=False),
        sa.Column("total_notifications", sa.Integer(), nullable=False),
        sa.Column("urgent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("important_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("informativo_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("spam_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("archived_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_saved_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("summary_text", sa.Text(), nullable=True),
        sa.Column("highlights", sa.JSON(), nullable=True),
        sa.Column("sent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_notification_digests_id"), "notification_digests", ["id"])
    op.create_index(
        op.f("ix_notification_digests_user_id"), "notification_digests", ["user_id"]
    )
    op.create_index(
        op.f("ix_notification_digests_period_start"), "notification_digests", ["period_start"]
    )

    # ========================================
    # 5. Create focus_sessions table
    # ========================================
    op.create_table(
        "focus_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("planned_duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "session_type",
            sa.String(50),
            sa.CheckConstraint("session_type IN ('deep_work', 'meeting', 'break', 'custom')"),
            nullable=True,
            server_default="deep_work",
        ),
        sa.Column("suppress_all", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("allow_urgent_only", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("custom_rules", sa.JSON(), nullable=True),
        sa.Column("notifications_suppressed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notifications_allowed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_focus_sessions_id"), "focus_sessions", ["id"])
    op.create_index(op.f("ix_focus_sessions_user_id"), "focus_sessions", ["user_id"])
    op.create_index(op.f("ix_focus_sessions_start_time"), "focus_sessions", ["start_time"])
    op.create_index(
        "ix_focus_sessions_user_active", "focus_sessions", ["user_id", "end_time"], unique=False
    )

    # ========================================
    # 6. Create notification_patterns table
    # ========================================
    op.create_table(
        "notification_patterns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "pattern_type",
            sa.String(50),
            sa.CheckConstraint(
                "pattern_type IN ('sender_preference', 'time_preference', "
                "'topic_preference', 'action_pattern')"
            ),
            nullable=False,
        ),
        sa.Column("pattern_key", sa.String(255), nullable=False),
        sa.Column("pattern_data", sa.JSON(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("occurrences", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_occurrence", sa.DateTime(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_notification_patterns_id"), "notification_patterns", ["id"])
    op.create_index(
        op.f("ix_notification_patterns_user_id"), "notification_patterns", ["user_id"]
    )
    op.create_index(
        op.f("ix_notification_patterns_pattern_key"), "notification_patterns", ["pattern_key"]
    )

    # ========================================
    # 7. Create response_templates table
    # ========================================
    op.create_table(
        "response_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("variables", sa.JSON(), nullable=True),
        sa.Column("times_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_used", sa.DateTime(), nullable=True),
        sa.Column("ai_generated", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_response_templates_id"), "response_templates", ["id"])
    op.create_index(op.f("ix_response_templates_user_id"), "response_templates", ["user_id"])
    op.create_index(op.f("ix_response_templates_category"), "response_templates", ["category"])


def downgrade():
    """Remove advanced notification system tables and fields."""

    # Drop response_templates
    op.drop_index(op.f("ix_response_templates_category"), table_name="response_templates")
    op.drop_index(op.f("ix_response_templates_user_id"), table_name="response_templates")
    op.drop_index(op.f("ix_response_templates_id"), table_name="response_templates")
    op.drop_table("response_templates")

    # Drop notification_patterns
    op.drop_index(op.f("ix_notification_patterns_pattern_key"), table_name="notification_patterns")
    op.drop_index(op.f("ix_notification_patterns_user_id"), table_name="notification_patterns")
    op.drop_index(op.f("ix_notification_patterns_id"), table_name="notification_patterns")
    op.drop_table("notification_patterns")

    # Drop focus_sessions
    op.drop_index("ix_focus_sessions_user_active", table_name="focus_sessions")
    op.drop_index(op.f("ix_focus_sessions_start_time"), table_name="focus_sessions")
    op.drop_index(op.f("ix_focus_sessions_user_id"), table_name="focus_sessions")
    op.drop_index(op.f("ix_focus_sessions_id"), table_name="focus_sessions")
    op.drop_table("focus_sessions")

    # Drop notification_digests
    op.drop_index(
        op.f("ix_notification_digests_period_start"), table_name="notification_digests"
    )
    op.drop_index(op.f("ix_notification_digests_user_id"), table_name="notification_digests")
    op.drop_index(op.f("ix_notification_digests_id"), table_name="notification_digests")
    op.drop_table("notification_digests")

    # Drop notification_rules
    op.drop_index("ix_notification_rules_user_enabled", table_name="notification_rules")
    op.drop_index(op.f("ix_notification_rules_enabled"), table_name="notification_rules")
    op.drop_index(op.f("ix_notification_rules_user_id"), table_name="notification_rules")
    op.drop_index(op.f("ix_notification_rules_id"), table_name="notification_rules")
    op.drop_table("notification_rules")

    # Remove new indexes from notifications
    op.drop_index("ix_notifications_snooze_until", table_name="notifications")
    op.drop_index("ix_notifications_arquivada", table_name="notifications")
    op.drop_index("ix_notifications_prioridade", table_name="notifications")
    op.drop_index("ix_notifications_categoria", table_name="notifications")
    op.drop_index("ix_notifications_thread_id", table_name="notifications")
    op.drop_index("ix_notifications_external_id", table_name="notifications")

    # Revert notification type constraint
    op.execute(
        """
        ALTER TABLE notifications DROP CONSTRAINT IF EXISTS notifications_type_check;
        ALTER TABLE notifications ADD CONSTRAINT notifications_type_check CHECK (
            type IN ('task_due_soon', 'capacity_overload', 'cycle_phase_change',
                     'freelance_invoice_ready', 'system', 'achievement')
        );
        """
    )

    # Remove new columns from notifications
    with op.batch_alter_table("notifications") as batch_op:
        batch_op.drop_constraint("fk_notifications_tarefa_criada_id", type_="foreignkey")
        batch_op.drop_constraint("fk_notifications_source_id", type_="foreignkey")

        batch_op.drop_column("updated_at")
        batch_op.drop_column("evento_criado_id")
        batch_op.drop_column("tarefa_criada_id")
        batch_op.drop_column("snooze_until")
        batch_op.drop_column("respondida")
        batch_op.drop_column("arquivada")
        batch_op.drop_column("rascunho_resposta")
        batch_op.drop_column("acao_executada")
        batch_op.drop_column("acao_sugerida")
        batch_op.drop_column("embedding")
        batch_op.drop_column("entidades_extraidas")
        batch_op.drop_column("tom_emocional")
        batch_op.drop_column("intencao")
        batch_op.drop_column("contexto")
        batch_op.drop_column("prioridade")
        batch_op.drop_column("categoria")
        batch_op.drop_column("thread_id")
        batch_op.drop_column("external_id")
        batch_op.drop_column("source_id")

    # Drop notification_sources
    op.drop_index("ix_notification_sources_user_type", table_name="notification_sources")
    op.drop_index(
        op.f("ix_notification_sources_source_type"), table_name="notification_sources"
    )
    op.drop_index(op.f("ix_notification_sources_user_id"), table_name="notification_sources")
    op.drop_index(op.f("ix_notification_sources_id"), table_name="notification_sources")
    op.drop_table("notification_sources")
