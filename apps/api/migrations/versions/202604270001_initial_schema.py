"""initial schema

Revision ID: 202604270001
Revises:
Create Date: 2026-04-27
"""

from alembic import op
import sqlalchemy as sa

revision = "202604270001"
down_revision = None
branch_labels = None
depends_on = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "custom_models",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("visibility", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("icon_file_id", sa.String(length=36), nullable=True),
        sa.Column("icon_url", sa.Text(), nullable=True),
        sa.Column("improve_from_feedback", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_version_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "slug", name="uq_model_owner_slug"),
    )
    op.create_index("ix_custom_models_owner_id", "custom_models", ["owner_id"])

    op.create_table(
        "datasets",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("readiness_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("valid_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("issue_summary", sa.JSON(), nullable=True),
        sa.Column("dataset_metadata", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_datasets_model_id", "datasets", ["model_id"])
    op.create_index("ix_datasets_owner_id", "datasets", ["owner_id"])

    op.create_table(
        "stored_files",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=True),
        sa.Column("dataset_id", sa.String(length=36), nullable=True),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("storage_bucket", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.Text(), nullable=False),
        sa.Column("public_url", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stored_files_checksum_sha256", "stored_files", ["checksum_sha256"])
    op.create_index("ix_stored_files_dataset_id", "stored_files", ["dataset_id"])
    op.create_index("ix_stored_files_model_id", "stored_files", ["model_id"])
    op.create_index("ix_stored_files_owner_id", "stored_files", ["owner_id"])

    op.create_table(
        "data_issues",
        sa.Column("dataset_id", sa.String(length=36), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=True),
        sa.Column("field", sa.String(length=80), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_data_issues_dataset_id", "data_issues", ["dataset_id"])

    op.create_table(
        "training_jobs",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("dataset_id", sa.String(length=36), nullable=True),
        sa.Column("job_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_step", sa.String(length=160), nullable=True),
        sa.Column("rq_job_id", sa.String(length=120), nullable=True),
        sa.Column("logs", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("training_config", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"]),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_training_jobs_dataset_id", "training_jobs", ["dataset_id"])
    op.create_index("ix_training_jobs_model_id", "training_jobs", ["model_id"])
    op.create_index("ix_training_jobs_owner_id", "training_jobs", ["owner_id"])
    op.create_index("ix_training_jobs_rq_job_id", "training_jobs", ["rq_job_id"])

    op.create_table(
        "model_versions",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("training_job_id", sa.String(length=36), nullable=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("base_model", sa.String(length=160), nullable=True),
        sa.Column("artifact_file_id", sa.String(length=36), nullable=True),
        sa.Column("artifact_storage_key", sa.Text(), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["training_job_id"], ["training_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_id", "version_number", name="uq_model_version_number"),
    )
    op.create_index("ix_model_versions_model_id", "model_versions", ["model_id"])
    op.create_index("ix_model_versions_owner_id", "model_versions", ["owner_id"])

    op.create_table(
        "api_keys",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=32), nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"])
    op.create_index("ix_api_keys_model_id", "api_keys", ["model_id"])
    op.create_index("ix_api_keys_owner_id", "api_keys", ["owner_id"])

    op.create_table(
        "feedback",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("model_version_id", sa.String(length=36), nullable=True),
        sa.Column("request_id", sa.String(length=80), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=True),
        sa.Column("output_payload", sa.JSON(), nullable=True),
        sa.Column("rating", sa.String(length=30), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("approved_for_training", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_model_id", "feedback", ["model_id"])
    op.create_index("ix_feedback_owner_id", "feedback", ["owner_id"])
    op.create_index("ix_feedback_request_id", "feedback", ["request_id"])

    op.create_table(
        "usage_logs",
        sa.Column("owner_id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=36), nullable=False),
        sa.Column("model_version_id", sa.String(length=36), nullable=True),
        sa.Column("api_key_id", sa.String(length=36), nullable=True),
        sa.Column("request_id", sa.String(length=80), nullable=False),
        sa.Column("endpoint", sa.String(length=160), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("input_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_units", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["api_key_id"], ["api_keys.id"]),
        sa.ForeignKeyConstraint(["model_id"], ["custom_models.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_version_id"], ["model_versions.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usage_logs_model_id", "usage_logs", ["model_id"])
    op.create_index("ix_usage_logs_owner_id", "usage_logs", ["owner_id"])
    op.create_index("ix_usage_logs_request_id", "usage_logs", ["request_id"])


def downgrade() -> None:
    op.drop_table("usage_logs")
    op.drop_table("feedback")
    op.drop_table("api_keys")
    op.drop_table("model_versions")
    op.drop_table("training_jobs")
    op.drop_table("data_issues")
    op.drop_table("stored_files")
    op.drop_table("datasets")
    op.drop_table("custom_models")
    op.drop_table("users")
