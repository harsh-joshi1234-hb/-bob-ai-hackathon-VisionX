"""
models/root_cause_analysis.py
------------------------------
ROOT_CAUSE_ANALYSIS table.

One row per feature contribution entry for a given lot.

For the SECOM classifier the contributions are computed externally
(e.g. SHAP values, permutation importance, or simple coefficient
inspection) and stored here.  For the Wafer Map CNN contributions
are not currently computed, but the same table can hold CNN saliency
or Grad-CAM region importance scores if added later.

``direction`` indicates whether the feature pushed the prediction
toward FAIL (positive) or toward PASS (negative).  ``contribution_value``
is the raw signed contribution magnitude (e.g. SHAP value).
``rank`` is the ordinal position among all features for this lot/run,
with 1 = most important.
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ContributionDirection(str, enum.Enum):
    """Whether the feature pushed the prediction toward failure or pass."""
    POSITIVE = "POSITIVE"    # increases P(FAIL)
    NEGATIVE = "NEGATIVE"    # decreases P(FAIL) / increases P(PASS)
    NEUTRAL = "NEUTRAL"      # negligible effect


class RootCauseAnalysis(Base):
    """
    Columns
    -------
    id                 UUID primary key.
    lot_id             FK → lots.id.
    analysis_run_id    FK → analysis_runs.id (nullable — allows standalone
                       RCA rows not tied to a full run record).
    feature_name       Name of the sensor/feature (e.g. "feature_08",
                       or a semantic name once recovered).
    feature_index      Integer position in the 24-feature vector (0–23).
    contribution_value Signed contribution magnitude (e.g. SHAP value).
    rank               Ordinal rank among all features for this lot (1 = most
                       important).
    direction          POSITIVE | NEGATIVE | NEUTRAL.
    method             Name of the explanation method used (e.g. "shap",
                       "permutation_importance", "manual").
    created_at         Row insertion timestamp.
    """

    __tablename__ = "root_cause_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    lot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_run_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    feature_name = Column(
        String(128),
        nullable=False,
        comment="Sensor / feature name, e.g. 'feature_08' or semantic name",
    )
    feature_index = Column(
        Integer,
        nullable=True,
        comment="Position in the 24-feature model input vector (0-based)",
    )
    contribution_value = Column(
        Float,
        nullable=False,
        comment="Signed contribution magnitude, e.g. SHAP value",
    )
    rank = Column(
        Integer,
        nullable=False,
        comment="1-based rank among all features for this lot (1 = most important)",
    )
    direction = Column(
        SAEnum(ContributionDirection, name="contribution_direction_enum", create_type=True),
        nullable=False,
        default=ContributionDirection.NEUTRAL,
    )
    method = Column(
        String(64),
        nullable=True,
        server_default="shap",
        comment="Explanation method: shap | permutation_importance | manual | etc.",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lot = relationship("Lot", back_populates="root_cause_analyses")
    analysis_run = relationship("AnalysisRun", back_populates="root_cause_entries")

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_rca_lot_id", "lot_id"),
        Index("ix_rca_rank", "rank"),
        Index("ix_rca_feature_name", "feature_name"),
        Index("ix_rca_analysis_run_id", "analysis_run_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<RootCauseAnalysis id={self.id} lot_id={self.lot_id} "
            f"feature={self.feature_name!r} rank={self.rank} "
            f"contribution={self.contribution_value:.4f}>"
        )
