"""initial_schema

Create all application tables for the S1 Semiconductor AI backend.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2024-06-01 00:00:00.000000

Tables created
--------------
  lots
  process_records
  predictions
  analysis_runs
  root_cause_analysis
  recommendations
  upcoming_batches

Enums created (PostgreSQL native)
----------------------------------
  lot_status_enum
  run_status_enum
  model_name_enum
  contribution_direction_enum
  risk_level_enum
  batch_status_enum
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# ---------------------------------------------------------------------------
# Alembic metadata
# ---------------------------------------------------------------------------
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Helper: idempotent enum creation
# ---------------------------------------------------------------------------
def _create_enum(name: str, *values: str) -> None:
    """Create a PostgreSQL ENUM type only if it does not already exist."""
    op.execute(
        f"DO $$ BEGIN "
        f"CREATE TYPE {name} AS ENUM {tuple(values)}; "
        f"EXCEPTION WHEN duplicate_object THEN NULL; "
        f"END $$;"
    )


def _drop_enum(name: str) -> None:
    op.execute(f"DROP TYPE IF EXISTS {name}")


# ---------------------------------------------------------------------------
# upgrade — forward migration
# ---------------------------------------------------------------------------
def upgrade() -> None:
    # ── PostgreSQL ENUM types ──────────────────────────────────────────────
    # SQLAlchemy will create these native enums automatically during table creation.


    # ── lots ──────────────────────────────────────────────────────────────
    op.create_table(
        "lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", sa.String(128), nullable=False),
        sa.Column("wafer_image_path", sa.String(512), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "PROCESSING", "COMPLETE", "FAILED", "ARCHIVED",
                name="lot_status_enum",
                create_type=False,
            ),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lot_id"),
    )
    op.create_index("ix_lots_lot_id", "lots", ["lot_id"])
    op.create_index("ix_lots_status", "lots", ["status"])
    op.create_index("ix_lots_created_at", "lots", ["created_at"])

    # ── process_records ───────────────────────────────────────────────────
    op.create_table(
        "process_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_record_id", sa.String(256), nullable=True),
        # 24 SECOM model features
        *[
            sa.Column(f"feature_{i:02d}", sa.Float(), nullable=True)
            for i in range(24)
        ],
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lot_id"], ["lots.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_process_records_lot_id", "process_records", ["lot_id"])
    op.create_index("ix_process_records_source_record_id", "process_records", ["source_record_id"])
    op.create_index("ix_process_records_created_at", "process_records", ["created_at"])

    # ── predictions ───────────────────────────────────────────────────────
    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "model_name",
            sa.Enum(
                "secom_classifier", "wafermap_cnn",
                name="model_name_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("model_version", sa.String(128), nullable=True),
        sa.Column("predicted_class", sa.String(64), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("probabilities", postgresql.JSONB(), nullable=True),
        sa.Column("raw_input_ref", sa.String(512), nullable=True),
        sa.Column(
            "prediction_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lot_id"], ["lots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["process_record_id"], ["process_records.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_predictions_lot_id", "predictions", ["lot_id"])
    op.create_index("ix_predictions_model_name", "predictions", ["model_name"])
    op.create_index("ix_predictions_predicted_class", "predictions", ["predicted_class"])
    op.create_index("ix_predictions_prediction_timestamp", "predictions", ["prediction_timestamp"])

    # ── analysis_runs ─────────────────────────────────────────────────────
    # Created before root_cause_analysis / recommendations because they FK here.
    # secom_prediction_id / cnn_prediction_id use ALTER TABLE to break the
    # circular FK cycle with predictions.
    op.create_table(
        "analysis_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "run_timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING", "RUNNING", "SUCCESS", "PARTIAL", "FAILED",
                name="run_status_enum",
                create_type=False,
            ),
            server_default="PENDING",
            nullable=False,
        ),
        sa.Column("model_versions", postgresql.JSONB(), nullable=True),
        sa.Column("secom_prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cnn_prediction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lot_id"], ["lots.id"], ondelete="CASCADE"),
    )
    # Deferred FK constraints to predictions (circular reference resolved via ALTER TABLE)
    op.create_foreign_key(
        "fk_analysis_runs_secom_prediction",
        "analysis_runs", "predictions",
        ["secom_prediction_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_analysis_runs_cnn_prediction",
        "analysis_runs", "predictions",
        ["cnn_prediction_id"], ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_analysis_runs_lot_id", "analysis_runs", ["lot_id"])
    op.create_index("ix_analysis_runs_status", "analysis_runs", ["status"])
    op.create_index("ix_analysis_runs_run_timestamp", "analysis_runs", ["run_timestamp"])

    # ── root_cause_analysis ───────────────────────────────────────────────
    op.create_table(
        "root_cause_analysis",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("feature_name", sa.String(128), nullable=False),
        sa.Column("feature_index", sa.Integer(), nullable=True),
        sa.Column("contribution_value", sa.Float(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column(
            "direction",
            sa.Enum(
                "POSITIVE", "NEGATIVE", "NEUTRAL",
                name="contribution_direction_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("method", sa.String(64), server_default="shap", nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lot_id"], ["lots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["analysis_runs.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_rca_lot_id", "root_cause_analysis", ["lot_id"])
    op.create_index("ix_rca_rank", "root_cause_analysis", ["rank"])
    op.create_index("ix_rca_feature_name", "root_cause_analysis", ["feature_name"])
    op.create_index("ix_rca_analysis_run_id", "root_cause_analysis", ["analysis_run_id"])

    # ── recommendations ───────────────────────────────────────────────────
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("recommended_actions", postgresql.JSONB(), nullable=True),
        sa.Column(
            "generated_by",
            sa.String(64),
            server_default="rule_engine",
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["lot_id"], ["lots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["analysis_runs.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_recommendations_lot_id", "recommendations", ["lot_id"])
    op.create_index("ix_recommendations_analysis_run_id", "recommendations", ["analysis_run_id"])
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"])

    # ── upcoming_batches ──────────────────────────────────────────────────
    op.create_table(
        "upcoming_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", sa.String(128), nullable=False),
        sa.Column("process_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("predicted_risk", sa.Float(), nullable=True),
        sa.Column(
            "risk_level",
            sa.Enum(
                "HIGH", "MEDIUM", "LOW", "UNKNOWN",
                name="risk_level_enum",
                create_type=False,
            ),
            server_default="UNKNOWN",
            nullable=False,
        ),
        sa.Column("flag_reason", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "FLAGGED", "CLEARED", "ON_HOLD", "CANCELLED",
                name="batch_status_enum",
                create_type=False,
            ),
            server_default="FLAGGED",
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("batch_id"),
        sa.ForeignKeyConstraint(
            ["process_record_id"], ["process_records.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_upcoming_batches_batch_id", "upcoming_batches", ["batch_id"])
    op.create_index("ix_upcoming_batches_risk_level", "upcoming_batches", ["risk_level"])
    op.create_index("ix_upcoming_batches_status", "upcoming_batches", ["status"])
    op.create_index("ix_upcoming_batches_scheduled_at", "upcoming_batches", ["scheduled_at"])
    op.create_index("ix_upcoming_batches_process_record_id", "upcoming_batches", ["process_record_id"])


# ---------------------------------------------------------------------------
# downgrade — roll back in reverse dependency order
# ---------------------------------------------------------------------------
def downgrade() -> None:
    # Drop tables (reverse FK dependency order)
    op.drop_table("upcoming_batches")
    op.drop_table("recommendations")
    op.drop_table("root_cause_analysis")

    # Drop deferred FKs before dropping analysis_runs
    op.drop_constraint(
        "fk_analysis_runs_cnn_prediction", "analysis_runs", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_analysis_runs_secom_prediction", "analysis_runs", type_="foreignkey"
    )
    op.drop_table("analysis_runs")
    op.drop_table("predictions")
    op.drop_table("process_records")
    op.drop_table("lots")

    # Drop PostgreSQL ENUM types
    _drop_enum("batch_status_enum")
    _drop_enum("risk_level_enum")
    _drop_enum("contribution_direction_enum")
    _drop_enum("model_name_enum")
    _drop_enum("run_status_enum")
    _drop_enum("lot_status_enum")
