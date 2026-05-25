"""Initial schema for DefectIQ AI."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="viewer"),
        sa.Column("department", sa.String(length=100)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "defects",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("ticket_id", sa.String(length=50), nullable=False),
        sa.Column("ticket_number", sa.String(length=50)),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(length=50)),
        sa.Column("priority", sa.String(length=20)),
        sa.Column("severity", sa.String(length=20)),
        sa.Column("assignment_group", sa.String(length=100)),
        sa.Column("assigned_to", sa.String(length=100)),
        sa.Column("opened_at", sa.DateTime(timezone=True)),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("target_resolution_time", sa.String(length=100)),
        sa.Column("actual_resolution_time", sa.String(length=100)),
        sa.Column("sla_breached", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sla_breach_date", sa.DateTime(timezone=True)),
        sa.Column("service_offering", sa.String(length=100)),
        sa.Column("business_domain", sa.String(length=100)),
        sa.Column("business_unit", sa.String(length=100)),
        sa.Column("impact", sa.String(length=50)),
        sa.Column("work_notes", sa.Text()),
        sa.Column("close_notes", sa.Text()),
        sa.Column("reassignment_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reopen_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_response_at", sa.DateTime(timezone=True)),
        sa.Column("last_modified", sa.DateTime(timezone=True)),
        sa.Column("workflow_state", sa.String(length=50)),
        sa.Column("root_cause_category", sa.String(length=100)),
        sa.Column("resolution_code", sa.String(length=50)),
        sa.Column("kmbase_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("related_incidents", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("data_source", sa.String(length=50)),
        sa.Column("ingestion_date", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("is_analyzed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("analysis_date", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("ticket_id", name="uq_defects_ticket_id"),
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("defect_id", sa.String(length=36), sa.ForeignKey("defects.id"), nullable=False),
        sa.Column("sla_breach_probability", sa.Float()),
        sa.Column("sla_breach_confidence", sa.Float()),
        sa.Column("sla_breach_days_estimate", sa.Integer()),
        sa.Column("sla_breach_model_version", sa.String(length=50)),
        sa.Column("estimated_resolution_hours", sa.Integer()),
        sa.Column("resolution_time_confidence", sa.Float()),
        sa.Column("resolution_time_model_version", sa.String(length=50)),
        sa.Column("recommended_assignment_group", sa.String(length=100)),
        sa.Column("recommended_consultant", sa.String(length=100)),
        sa.Column("assignment_confidence", sa.Float()),
        sa.Column("assignment_reason", sa.Text()),
        sa.Column("assignment_model_version", sa.String(length=50)),
        sa.Column("feature_importance", sa.JSON()),
        sa.Column("prediction_date", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("model_version", sa.String(length=50)),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("prediction_status", sa.String(length=50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ai_summaries",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("defect_id", sa.String(length=36), sa.ForeignKey("defects.id"), nullable=False),
        sa.Column("root_cause_summary", sa.Text()),
        sa.Column("resolution_summary", sa.Text()),
        sa.Column("action_taken_summary", sa.Text()),
        sa.Column("defect_category", sa.String(length=100)),
        sa.Column("defect_subcategory", sa.String(length=100)),
        sa.Column("category_confidence", sa.Float()),
        sa.Column("key_keywords", sa.JSON()),
        sa.Column("key_terms", sa.JSON()),
        sa.Column("suggested_tags", sa.JSON()),
        sa.Column("sentiment", sa.String(length=20)),
        sa.Column("urgency_score", sa.Float()),
        sa.Column("complexity_score", sa.Float()),
        sa.Column("generated_by", sa.String(length=50)),
        sa.Column("model_used", sa.String(length=100)),
        sa.Column("generation_timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("manual_corrections", sa.JSON()),
    )

    op.create_table(
        "chat_history",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("conversation_id", sa.String(length=100)),
        sa.Column("message_type", sa.String(length=50), nullable=False),
        sa.Column("message_content", sa.Text(), nullable=False),
        sa.Column("context_defect_ids", sa.JSON()),
        sa.Column("context_filters", sa.JSON()),
        sa.Column("response_time_ms", sa.Integer()),
        sa.Column("sources_used", sa.JSON()),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("user_rating", sa.Integer()),
        sa.Column("was_helpful", sa.Boolean()),
        sa.Column("feedback_text", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "upload_sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("total_records", sa.Integer()),
        sa.Column("processed_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("validation_errors", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "saved_filters",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("filter_name", sa.String(length=150), nullable=False),
        sa.Column("filter_description", sa.Text()),
        sa.Column("filter_definition", sa.JSON(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("actor_user_id", sa.String(length=36), sa.ForeignKey("users.id")),
        sa.Column("entity_name", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("before_state", sa.JSON()),
        sa.Column("after_state", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ml_models",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("model_type", sa.String(length=50), nullable=False),
        sa.Column("file_path", sa.String(length=255)),
        sa.Column("metrics", sa.JSON()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("trained_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("ml_models")
    op.drop_table("audit_logs")
    op.drop_table("saved_filters")
    op.drop_table("upload_sessions")
    op.drop_table("chat_history")
    op.drop_table("ai_summaries")
    op.drop_table("predictions")
    op.drop_table("defects")
    op.drop_table("users")
