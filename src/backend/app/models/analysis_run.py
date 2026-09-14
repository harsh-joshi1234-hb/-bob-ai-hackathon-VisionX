"""
models/analysis_run.py
-----------------------
ANALYSIS_RUNS table.

One row per full end-to-end analysis execution for a lot.  An analysis
run ties together all model inferences, root-cause entries, and
recommendations produced in a single pipeline invocation.

This table is created BEFORE root_cause_analysis and recommendations
in the FK dependency order, so it is defined here.  RootCauseAnalysis
and Recommendation back-reference it via FK.

Run statuses
------------
    PENDING     → queued, not yet started
    RUNNING     → actively processing
    SUCCESS     → completed without errors
    PARTIAL     → completed with non-fatal warnings (some features missing)
    FAILED      → terminated with an unrecoverable error
"""

import uuid
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RunStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class AnalysisRun(Base):
    """
    Columns
    -------
    id                  UUID primary key.
    lot_id              FK → lots.id.
    run_timestamp       When the run was initiated (set by the application).
    completed_at        When the run finished (NULL while running).
    status              Pipeline state: PENDING | RUNNING | SUCCESS | PARTIAL | FAILED.
    model_versions      JSONB dict of model names → version strings used.
                        E.g. {"secom_classifier": "20240601", "wafermap_cnn": "20240601"}
    secom_prediction_id FK → predictions.id — SECOM result for this run (nullable).
    cnn_prediction_id   FK → predictions.id — CNN result for this run (nullable).
    processing_time_ms  Total wall-clock time in milliseconds.
    error_message       Captured traceback / error text on FAILED runs.
    notes               Optional free-text field for engineer annotations.
    created_at          Row insertion timestamp.
    """

    __tablename__ = "analysis_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    lot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    run_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Datetime the analysis run was initiated",
    )
    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Datetime the run finished (NULL while still running)",
    )

    status = Column(
        SAEnum(RunStatus, name="run_status_enum", create_type=True),
        nullable=False,
        default=RunStatus.PENDING,
        server_default=RunStatus.PENDING.value,
    )

    model_versions = Column(
        JSONB,
        nullable=True,
        comment=(
            'Dict of model_name → version, e.g. '
            '{"secom_classifier": "20240601", "wafermap_cnn": "20240601"}'
        ),
    )

    # Self-referencing FKs to Prediction rows produced by this run.
    # Use_alter=True breaks the circular FK cycle that would otherwise
    # prevent table creation.
    secom_prediction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="SET NULL", use_alter=True,
                   name="fk_analysis_runs_secom_prediction"),
        nullable=True,
    )
    cnn_prediction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("predictions.id", ondelete="SET NULL", use_alter=True,
                   name="fk_analysis_runs_cnn_prediction"),
        nullable=True,
    )

    processing_time_ms = Column(
        Integer,
        nullable=True,
        comment="Total wall-clock processing time in milliseconds",
    )
    error_message = Column(
        Text,
        nullable=True,
        comment="Captured error / traceback text on FAILED runs",
    )
    notes = Column(
        Text,
        nullable=True,
        comment="Free-text field for engineer annotations",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lot = relationship("Lot", back_populates="analysis_runs")
    root_cause_entries = relationship(
        "RootCauseAnalysis",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    recommendations = relationship(
        "Recommendation",
        back_populates="analysis_run",
        cascade="all, delete-orphan",
    )
    secom_prediction = relationship(
        "Prediction",
        foreign_keys=[secom_prediction_id],
        primaryjoin="AnalysisRun.secom_prediction_id == Prediction.id",
    )
    cnn_prediction = relationship(
        "Prediction",
        foreign_keys=[cnn_prediction_id],
        primaryjoin="AnalysisRun.cnn_prediction_id == Prediction.id",
    )

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_analysis_runs_lot_id", "lot_id"),
        Index("ix_analysis_runs_status", "status"),
        Index("ix_analysis_runs_run_timestamp", "run_timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<AnalysisRun id={self.id} lot_id={self.lot_id} "
            f"status={self.status} ts={self.run_timestamp}>"
        )
