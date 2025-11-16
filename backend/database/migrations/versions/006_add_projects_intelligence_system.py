"""add projects intelligence system (AI-powered freelance platform monitoring and analysis)

Revision ID: 006
Revises: 005
Create Date: 2025-01-16 19:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    """Add projects intelligence system tables with AI analysis capabilities."""

    # Enable pgvector extension for embeddings
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create freelance_platforms table
    op.create_table(
        "freelance_platforms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("platform_type", sa.String(length=50), nullable=True),
        sa.Column("website_url", sa.String(length=255), nullable=True),
        sa.Column("api_config", sa.JSON(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("last_collection_at", sa.DateTime(), nullable=True),
        sa.Column("last_collection_count", sa.Integer(), server_default="0"),
        sa.Column("collection_interval_minutes", sa.Integer(), server_default="60"),
        sa.Column("auto_collect", sa.Boolean(), server_default="false"),
        sa.Column("total_projects_collected", sa.Integer(), server_default="0"),
        sa.Column("total_projects_accepted", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_freelance_platforms_id"), "freelance_platforms", ["id"], unique=False)
    op.create_index(op.f("ix_freelance_platforms_user_id"), "freelance_platforms", ["user_id"], unique=False)
    op.create_index(op.f("ix_freelance_platforms_active"), "freelance_platforms", ["active"], unique=False)
    op.create_index("ix_platforms_active_user", "freelance_platforms", ["active", "user_id"], unique=False)

    # Create freelance_opportunities table
    op.create_table(
        "freelance_opportunities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("platform_id", sa.Integer(), nullable=True),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("client_name", sa.String(length=200), nullable=True),
        sa.Column("client_rating", sa.Float(), nullable=True),
        sa.Column("client_country", sa.String(length=100), nullable=True),
        sa.Column("client_projects_count", sa.Integer(), nullable=True),
        sa.Column("required_skills", sa.JSON(), nullable=True),
        sa.Column("skill_level", sa.String(length=20), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("client_budget", sa.Float(), nullable=True),
        sa.Column("client_currency", sa.String(length=10), server_default="USD"),
        sa.Column("client_deadline_days", sa.Integer(), nullable=True),
        sa.Column("contract_type", sa.String(length=20), nullable=True),
        sa.Column(
            "estimated_complexity",
            sa.Integer(),
            sa.CheckConstraint("estimated_complexity BETWEEN 1 AND 10"),
            nullable=True,
        ),
        sa.Column("estimated_hours", sa.Float(), nullable=True),
        sa.Column("suggested_price", sa.Float(), nullable=True),
        sa.Column("suggested_deadline_days", sa.Integer(), nullable=True),
        sa.Column("viability_score", sa.Float(), nullable=True),
        sa.Column("alignment_score", sa.Float(), nullable=True),
        sa.Column("strategic_score", sa.Float(), nullable=True),
        sa.Column("final_score", sa.Float(), nullable=True),
        sa.Column(
            "recommendation",
            sa.String(length=20),
            sa.CheckConstraint("recommendation IN ('accept', 'negotiate', 'reject', 'pending')"),
            server_default="pending",
        ),
        sa.Column("recommendation_reason", sa.Text(), nullable=True),
        sa.Column("client_intent", sa.String(length=50), nullable=True),
        sa.Column("red_flags", sa.JSON(), nullable=True),
        sa.Column("opportunities", sa.JSON(), nullable=True),
        sa.Column("extracted_context", sa.JSON(), nullable=True),
        sa.Column("description_embedding", Vector(1536), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('new', 'analyzed', 'negotiating', 'accepted', 'rejected', 'expired')"),
            server_default="new",
        ),
        sa.Column("final_decision", sa.String(length=20), nullable=True),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("collected_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["platform_id"], ["freelance_platforms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_freelance_opportunities_id"), "freelance_opportunities", ["id"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_user_id"), "freelance_opportunities", ["user_id"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_platform_id"), "freelance_opportunities", ["platform_id"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_external_id"), "freelance_opportunities", ["external_id"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_final_score"), "freelance_opportunities", ["final_score"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_recommendation"), "freelance_opportunities", ["recommendation"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_status"), "freelance_opportunities", ["status"], unique=False)
    op.create_index(op.f("ix_freelance_opportunities_collected_at"), "freelance_opportunities", ["collected_at"], unique=False)
    op.create_index("ix_opportunities_score_desc", "freelance_opportunities", [sa.text("final_score DESC")], unique=False)
    op.create_index("ix_opportunities_status_recommendation", "freelance_opportunities", ["status", "recommendation"], unique=False)
    op.create_index("ix_opportunities_collected_desc", "freelance_opportunities", [sa.text("collected_at DESC")], unique=False)
    # Vector index for similarity search (created after data is populated)
    # op.execute("CREATE INDEX ix_opportunities_embedding ON freelance_opportunities USING ivfflat (description_embedding vector_cosine_ops)")

    # Create project_executions table
    op.create_table(
        "project_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("opportunity_id", sa.Integer(), nullable=True),
        sa.Column("freelance_project_id", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("planned_end_date", sa.Date(), nullable=True),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
        sa.Column("planned_hours", sa.Float(), nullable=True),
        sa.Column("actual_hours", sa.Float(), server_default="0.0"),
        sa.Column("hours_variance_percentage", sa.Float(), nullable=True),
        sa.Column("negotiated_value", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default="USD"),
        sa.Column("received_value", sa.Float(), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column(
            "client_satisfaction",
            sa.Integer(),
            sa.CheckConstraint("client_satisfaction BETWEEN 1 AND 5"),
            nullable=True,
        ),
        sa.Column("client_rating_received", sa.Float(), nullable=True),
        sa.Column("client_feedback", sa.Text(), nullable=True),
        sa.Column("client_testimonial", sa.Text(), nullable=True),
        sa.Column(
            "actual_difficulty",
            sa.Integer(),
            sa.CheckConstraint("actual_difficulty BETWEEN 1 AND 10"),
            nullable=True,
        ),
        sa.Column("learnings", sa.JSON(), nullable=True),
        sa.Column("challenges_faced", sa.JSON(), nullable=True),
        sa.Column("personal_notes", sa.Text(), nullable=True),
        sa.Column("new_skills_acquired", sa.JSON(), nullable=True),
        sa.Column("technologies_used", sa.JSON(), nullable=True),
        sa.Column("portfolio_worthy", sa.Boolean(), server_default="false"),
        sa.Column("testimonial_obtained", sa.Boolean(), server_default="false"),
        sa.Column("referral_potential", sa.Boolean(), server_default="false"),
        sa.Column(
            "status",
            sa.String(length=20),
            sa.CheckConstraint("status IN ('planned', 'in_progress', 'completed', 'cancelled', 'on_hold')"),
            server_default="planned",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["freelance_opportunities.id"]),
        sa.ForeignKeyConstraint(["freelance_project_id"], ["freelance_projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_executions_id"), "project_executions", ["id"], unique=False)
    op.create_index(op.f("ix_project_executions_user_id"), "project_executions", ["user_id"], unique=False)
    op.create_index(op.f("ix_project_executions_opportunity_id"), "project_executions", ["opportunity_id"], unique=False)
    op.create_index(op.f("ix_project_executions_freelance_project_id"), "project_executions", ["freelance_project_id"], unique=False)
    op.create_index(op.f("ix_project_executions_status"), "project_executions", ["status"], unique=False)
    op.create_index("ix_executions_dates", "project_executions", ["start_date", "actual_end_date"], unique=False)

    # Create pricing_parameters table
    op.create_table(
        "pricing_parameters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("base_hourly_rate", sa.Float(), nullable=False),
        sa.Column("minimum_margin", sa.Float(), server_default="0.20"),
        sa.Column("currency", sa.String(length=10), server_default="USD"),
        sa.Column("complexity_factors", sa.JSON(), nullable=True),
        sa.Column("specialization_factors", sa.JSON(), nullable=True),
        sa.Column("deadline_factors", sa.JSON(), nullable=True),
        sa.Column("client_factors", sa.JSON(), nullable=True),
        sa.Column("minimum_project_value", sa.Float(), server_default="500.0"),
        sa.Column("minimum_deadline_days", sa.Integer(), server_default="7"),
        sa.Column("auto_adjusted", sa.Boolean(), server_default="false"),
        sa.Column("based_on_executions_count", sa.Integer(), server_default="0"),
        sa.Column("adjustment_reason", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("activated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pricing_parameters_id"), "pricing_parameters", ["id"], unique=False)
    op.create_index(op.f("ix_pricing_parameters_user_id"), "pricing_parameters", ["user_id"], unique=False)
    op.create_index(op.f("ix_pricing_parameters_active"), "pricing_parameters", ["active"], unique=False)
    op.create_index("ix_pricing_active_user_version", "pricing_parameters", ["active", "user_id", sa.text("version DESC")], unique=False)

    # Create negotiations table
    op.create_table(
        "negotiations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("opportunity_id", sa.Integer(), nullable=False),
        sa.Column("original_budget", sa.Float(), nullable=True),
        sa.Column("original_deadline_days", sa.Integer(), nullable=True),
        sa.Column("counter_proposal_budget", sa.Float(), nullable=False),
        sa.Column("counter_proposal_deadline_days", sa.Integer(), nullable=True),
        sa.Column("counter_proposal_justification", sa.Text(), nullable=False),
        sa.Column("generated_message", sa.Text(), nullable=True),
        sa.Column("client_response", sa.Text(), nullable=True),
        sa.Column("final_agreed_budget", sa.Float(), nullable=True),
        sa.Column("final_agreed_deadline_days", sa.Integer(), nullable=True),
        sa.Column(
            "outcome",
            sa.String(length=20),
            sa.CheckConstraint("outcome IN ('accepted', 'rejected', 'agreed', 'no_response', 'pending')"),
            server_default="pending",
        ),
        sa.Column("outcome_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("finalized_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["opportunity_id"], ["freelance_opportunities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_negotiations_id"), "negotiations", ["id"], unique=False)
    op.create_index(op.f("ix_negotiations_user_id"), "negotiations", ["user_id"], unique=False)
    op.create_index(op.f("ix_negotiations_opportunity_id"), "negotiations", ["opportunity_id"], unique=False)
    op.create_index(op.f("ix_negotiations_outcome"), "negotiations", ["outcome"], unique=False)

    # Create career_insights table
    op.create_table(
        "career_insights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("report_type", sa.String(length=20), nullable=False),
        sa.Column("total_revenue", sa.Float(), server_default="0.0"),
        sa.Column("average_project_value", sa.Float(), nullable=True),
        sa.Column("effective_hourly_rate", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), server_default="USD"),
        sa.Column("projects_completed", sa.Integer(), server_default="0"),
        sa.Column("success_rate", sa.Float(), nullable=True),
        sa.Column("total_hours_worked", sa.Float(), server_default="0.0"),
        sa.Column("average_hours_per_project", sa.Float(), nullable=True),
        sa.Column("average_complexity", sa.Float(), nullable=True),
        sa.Column("new_technologies", sa.JSON(), nullable=True),
        sa.Column("dominant_categories", sa.JSON(), nullable=True),
        sa.Column("most_profitable_categories", sa.JSON(), nullable=True),
        sa.Column("preferred_clients", sa.JSON(), nullable=True),
        sa.Column("identified_trends", sa.JSON(), nullable=True),
        sa.Column("recommendations", sa.JSON(), nullable=True),
        sa.Column("next_step_suggestion", sa.Text(), nullable=True),
        sa.Column("top_demanded_skills", sa.JSON(), nullable=True),
        sa.Column("skill_gaps", sa.JSON(), nullable=True),
        sa.Column("competitive_advantages", sa.JSON(), nullable=True),
        sa.Column("ai_generated_summary", sa.Text(), nullable=True),
        sa.Column("ai_confidence_score", sa.Float(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_career_insights_id"), "career_insights", ["id"], unique=False)
    op.create_index(op.f("ix_career_insights_user_id"), "career_insights", ["user_id"], unique=False)
    op.create_index(op.f("ix_career_insights_period_start"), "career_insights", ["period_start"], unique=False)
    op.create_index(op.f("ix_career_insights_period_end"), "career_insights", ["period_end"], unique=False)
    op.create_index(op.f("ix_career_insights_report_type"), "career_insights", ["report_type"], unique=False)
    op.create_index("ix_insights_period", "career_insights", ["period_start", "period_end"], unique=False)

    # Create portfolio_items table
    op.create_table(
        "portfolio_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("optimized_description", sa.Text(), nullable=False),
        sa.Column("technologies_used", sa.JSON(), nullable=True),
        sa.Column("challenges_overcome", sa.JSON(), nullable=True),
        sa.Column("results_metrics", sa.JSON(), nullable=True),
        sa.Column("images_urls", sa.JSON(), nullable=True),
        sa.Column("demo_url", sa.String(length=500), nullable=True),
        sa.Column("case_study_url", sa.String(length=500), nullable=True),
        sa.Column("repository_url", sa.String(length=500), nullable=True),
        sa.Column("featured", sa.Boolean(), server_default="false"),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("public", sa.Boolean(), server_default="true"),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["execution_id"], ["project_executions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_items_id"), "portfolio_items", ["id"], unique=False)
    op.create_index(op.f("ix_portfolio_items_user_id"), "portfolio_items", ["user_id"], unique=False)
    op.create_index(op.f("ix_portfolio_items_execution_id"), "portfolio_items", ["execution_id"], unique=False)
    op.create_index(op.f("ix_portfolio_items_featured"), "portfolio_items", ["featured"], unique=False)
    op.create_index("ix_portfolio_featured_public", "portfolio_items", ["featured", "public"], unique=False)

    # Create learning_records table
    op.create_table(
        "learning_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("learning_type", sa.String(length=50), nullable=False),
        sa.Column("input_features", sa.JSON(), nullable=False),
        sa.Column("predicted_output", sa.JSON(), nullable=True),
        sa.Column("actual_output", sa.JSON(), nullable=True),
        sa.Column("accuracy_score", sa.Float(), nullable=True),
        sa.Column("error_margin", sa.Float(), nullable=True),
        sa.Column("user_feedback", sa.Text(), nullable=True),
        sa.Column(
            "user_rating",
            sa.Integer(),
            sa.CheckConstraint("user_rating BETWEEN 1 AND 5"),
            nullable=True,
        ),
        sa.Column("adjustment_applied", sa.Boolean(), server_default="false"),
        sa.Column("adjustment_impact", sa.Text(), nullable=True),
        sa.Column("related_opportunity_id", sa.Integer(), nullable=True),
        sa.Column("related_execution_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["related_opportunity_id"], ["freelance_opportunities.id"]),
        sa.ForeignKeyConstraint(["related_execution_id"], ["project_executions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_learning_records_id"), "learning_records", ["id"], unique=False)
    op.create_index(op.f("ix_learning_records_user_id"), "learning_records", ["user_id"], unique=False)
    op.create_index(op.f("ix_learning_records_learning_type"), "learning_records", ["learning_type"], unique=False)
    op.create_index(op.f("ix_learning_records_created_at"), "learning_records", ["created_at"], unique=False)
    op.create_index("ix_learning_type_date", "learning_records", ["learning_type", sa.text("created_at DESC")], unique=False)

    # Create personal_reflections table
    op.create_table(
        "personal_reflections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("related_to_type", sa.String(length=50), nullable=True),
        sa.Column("related_to_id", sa.Integer(), nullable=True),
        sa.Column("action_taken", sa.Text(), nullable=True),
        sa.Column("action_result", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_personal_reflections_id"), "personal_reflections", ["id"], unique=False)
    op.create_index(op.f("ix_personal_reflections_user_id"), "personal_reflections", ["user_id"], unique=False)
    op.create_index(op.f("ix_personal_reflections_date"), "personal_reflections", ["date"], unique=False)
    op.create_index(op.f("ix_personal_reflections_category"), "personal_reflections", ["category"], unique=False)
    op.create_index("ix_reflections_date_desc", "personal_reflections", [sa.text("date DESC")], unique=False)


def downgrade():
    """Remove projects intelligence system tables."""

    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table("personal_reflections")
    op.drop_table("learning_records")
    op.drop_table("portfolio_items")
    op.drop_table("career_insights")
    op.drop_table("negotiations")
    op.drop_table("pricing_parameters")
    op.drop_table("project_executions")
    op.drop_table("freelance_opportunities")
    op.drop_table("freelance_platforms")

    # Optionally drop pgvector extension
    # op.execute("DROP EXTENSION IF EXISTS vector")
