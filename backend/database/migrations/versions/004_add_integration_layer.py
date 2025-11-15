"""add integration layer (Event Bus, Context Manager, Cross-Module Relations)

Revision ID: 004
Revises: 003
Create Date: 2025-01-15 20:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    """Add integration layer tables for V3.1."""

    # Create user_settings table
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("theme", sa.String(length=20), server_default="auto"),
        sa.Column("density", sa.String(length=20), server_default="comfortable"),
        sa.Column("timezone", sa.String(length=50), server_default="America/Sao_Paulo"),
        sa.Column("language", sa.String(length=10), server_default="pt-BR"),
        sa.Column("notifications_enabled", sa.Boolean(), server_default="true"),
        sa.Column("email_notifications", sa.Boolean(), server_default="false"),
        sa.Column("push_notifications", sa.Boolean(), server_default="true"),
        sa.Column("work_hours_per_day", sa.Integer(), server_default="8"),
        sa.Column("work_days_per_week", sa.Integer(), server_default="5"),
        sa.Column("planning_horizon_days", sa.Integer(), server_default="7"),
        sa.Column("cycle_tracking_enabled", sa.Boolean(), server_default="true"),
        sa.Column("cycle_length_days", sa.Integer(), server_default="28"),
        sa.Column("integrations", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_settings_id"), "user_settings", ["id"], unique=False)
    op.create_index(op.f("ix_user_settings_user_id"), "user_settings", ["user_id"], unique=True)

    # Create system_events table (Event Bus)
    op.create_table(
        "system_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=100), nullable=False),
        sa.Column("modulo_origem", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("prioridade", sa.Integer(), server_default="5"),
        sa.Column("processado", sa.Boolean(), server_default="false"),
        sa.Column("criado_em", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("processado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_system_events_id"), "system_events", ["id"], unique=False)
    op.create_index(op.f("ix_system_events_tipo"), "system_events", ["tipo"], unique=False)
    op.create_index(
        op.f("ix_system_events_modulo_origem"), "system_events", ["modulo_origem"], unique=False
    )
    op.create_index(
        op.f("ix_system_events_prioridade"), "system_events", ["prioridade"], unique=False
    )
    op.create_index(
        op.f("ix_system_events_processado"), "system_events", ["processado"], unique=False
    )
    op.create_index(
        op.f("ix_system_events_criado_em"), "system_events", ["criado_em"], unique=False
    )
    # Composite indexes
    op.create_index(
        "ix_events_tipo_processado", "system_events", ["tipo", "processado"], unique=False
    )
    op.create_index(
        "ix_events_prioridade_desc",
        "system_events",
        [sa.text("prioridade DESC"), "criado_em"],
        unique=False,
    )

    # Create global_context table (Context Manager)
    op.create_table(
        "global_context",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("fase_ciclo", sa.String(length=20), nullable=True),
        sa.Column(
            "energia_atual",
            sa.Integer(),
            sa.CheckConstraint("energia_atual BETWEEN 1 AND 10"),
            server_default="7",
        ),
        sa.Column("carga_trabalho_percentual", sa.Float(), server_default="50.0"),
        sa.Column("em_sessao_foco", sa.Boolean(), server_default="false"),
        sa.Column("tarefas_pendentes", sa.Integer(), server_default="0"),
        sa.Column("projetos_ativos", sa.Integer(), server_default="0"),
        sa.Column("notificacoes_nao_lidas", sa.Integer(), server_default="0"),
        sa.Column(
            "hora_dia", sa.Integer(), sa.CheckConstraint("hora_dia BETWEEN 0 AND 23"), nullable=True
        ),
        sa.Column(
            "dia_semana",
            sa.Integer(),
            sa.CheckConstraint("dia_semana BETWEEN 0 AND 6"),
            nullable=True,
        ),
        sa.Column("periodo_produtivo", sa.String(length=20), nullable=True),
        sa.Column(
            "nivel_stress",
            sa.Integer(),
            sa.CheckConstraint("nivel_stress BETWEEN 1 AND 10"),
            server_default="5",
        ),
        sa.Column("necessita_pausa", sa.Boolean(), server_default="false"),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_global_context_id"), "global_context", ["id"], unique=False)
    op.create_index(op.f("ix_global_context_user_id"), "global_context", ["user_id"], unique=False)

    # Create cross_module_relations table
    op.create_table(
        "cross_module_relations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tipo_relacao", sa.String(length=50), nullable=False),
        sa.Column("modulo_origem", sa.String(length=50), nullable=False),
        sa.Column("entidade_origem_id", sa.Integer(), nullable=False),
        sa.Column("modulo_destino", sa.String(length=50), nullable=False),
        sa.Column("entidade_destino_id", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cross_module_relations_id"), "cross_module_relations", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_cross_module_relations_tipo_relacao"),
        "cross_module_relations",
        ["tipo_relacao"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cross_module_relations_modulo_origem"),
        "cross_module_relations",
        ["modulo_origem"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cross_module_relations_entidade_origem_id"),
        "cross_module_relations",
        ["entidade_origem_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cross_module_relations_modulo_destino"),
        "cross_module_relations",
        ["modulo_destino"],
        unique=False,
    )
    op.create_index(
        op.f("ix_cross_module_relations_entidade_destino_id"),
        "cross_module_relations",
        ["entidade_destino_id"],
        unique=False,
    )
    # Composite indexes
    op.create_index(
        "ix_cross_module_origem",
        "cross_module_relations",
        ["modulo_origem", "entidade_origem_id"],
        unique=False,
    )
    op.create_index(
        "ix_cross_module_destino",
        "cross_module_relations",
        ["modulo_destino", "entidade_destino_id"],
        unique=False,
    )

    # Create integrated_decisions table
    op.create_table(
        "integrated_decisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("situacao", sa.Text(), nullable=False),
        sa.Column("modulos_envolvidos", sa.JSON(), nullable=False),
        sa.Column("contexto_considerado", sa.JSON(), nullable=False),
        sa.Column("opcoes_avaliadas", sa.JSON(), nullable=True),
        sa.Column("decisao_tomada", sa.Text(), nullable=False),
        sa.Column("justificativa", sa.Text(), nullable=False),
        sa.Column("executado", sa.Boolean(), server_default="false"),
        sa.Column("resultado", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_integrated_decisions_id"), "integrated_decisions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_integrated_decisions_criado_em"),
        "integrated_decisions",
        ["criado_em"],
        unique=False,
    )


def downgrade():
    """Remove integration layer tables."""

    # Drop user_settings table
    op.drop_index(op.f("ix_user_settings_user_id"), table_name="user_settings")
    op.drop_index(op.f("ix_user_settings_id"), table_name="user_settings")
    op.drop_table("user_settings")

    # Drop integrated_decisions table
    op.drop_index(op.f("ix_integrated_decisions_criado_em"), table_name="integrated_decisions")
    op.drop_index(op.f("ix_integrated_decisions_id"), table_name="integrated_decisions")
    op.drop_table("integrated_decisions")

    # Drop cross_module_relations table
    op.drop_index("ix_cross_module_destino", table_name="cross_module_relations")
    op.drop_index("ix_cross_module_origem", table_name="cross_module_relations")
    op.drop_index(
        op.f("ix_cross_module_relations_entidade_destino_id"), table_name="cross_module_relations"
    )
    op.drop_index(
        op.f("ix_cross_module_relations_modulo_destino"), table_name="cross_module_relations"
    )
    op.drop_index(
        op.f("ix_cross_module_relations_entidade_origem_id"), table_name="cross_module_relations"
    )
    op.drop_index(
        op.f("ix_cross_module_relations_modulo_origem"), table_name="cross_module_relations"
    )
    op.drop_index(
        op.f("ix_cross_module_relations_tipo_relacao"), table_name="cross_module_relations"
    )
    op.drop_index(op.f("ix_cross_module_relations_id"), table_name="cross_module_relations")
    op.drop_table("cross_module_relations")

    # Drop global_context table
    op.drop_index(op.f("ix_global_context_user_id"), table_name="global_context")
    op.drop_index(op.f("ix_global_context_id"), table_name="global_context")
    op.drop_table("global_context")

    # Drop system_events table
    op.drop_index("ix_events_prioridade_desc", table_name="system_events")
    op.drop_index("ix_events_tipo_processado", table_name="system_events")
    op.drop_index(op.f("ix_system_events_criado_em"), table_name="system_events")
    op.drop_index(op.f("ix_system_events_processado"), table_name="system_events")
    op.drop_index(op.f("ix_system_events_prioridade"), table_name="system_events")
    op.drop_index(op.f("ix_system_events_modulo_origem"), table_name="system_events")
    op.drop_index(op.f("ix_system_events_tipo"), table_name="system_events")
    op.drop_index(op.f("ix_system_events_id"), table_name="system_events")
    op.drop_table("system_events")
