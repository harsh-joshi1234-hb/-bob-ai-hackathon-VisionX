"""
models/recommendation.py
-------------------------
RECOMMENDATIONS table.

One row per recommendation report generated for a lot.

``summary`` holds a high-level text summary of the recommended actions.
``recommended_actions`` is a JSONB array, where each element is a dict:

    {
        "action": "Inspect cooling unit on chamber C3",
        "priority": "HIGH",
        "target_parameter": "feature_08",
        "rationale": "Feature 8 contributed +2.34 SHAP points toward FAIL"
    }

This structure lets the frontend render a structured action list without
parsing free text.
"""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Recommendation(Base):
    """
    Columns
    -------
    id                  UUID primary key.
    lot_id              FK → lots.id.
    analysis_run_id     FK → analysis_runs.id (nullable).
    summary             Plain-text executive summary of the recommendation.
    recommended_actions JSONB array of structured action items.
    generated_by        Who/what generated the recommendation: "rule_engine",
                        "watsonx_llm", "manual", etc.
    created_at          Row insertion timestamp.
    updated_at          Last modification timestamp (allows editing).
    """

    __tablename__ = "recommendations"

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

    summary = Column(
        Text,
        nullable=True,
        comment="Plain-text executive summary of what actions are recommended",
    )
    recommended_actions = Column(
        JSONB,
        nullable=True,
        comment=(
            "Structured list of action items. "
            'Each item: {"action": str, "priority": HIGH|MEDIUM|LOW, '
            '"target_parameter": str, "rationale": str}'
        ),
    )
    generated_by = Column(
        String(64),
        nullable=True,
        server_default="rule_engine",
        comment="Source of recommendation: rule_engine | watsonx_llm | manual",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lot = relationship("Lot", back_populates="recommendations")
    analysis_run = relationship("AnalysisRun", back_populates="recommendations")

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_recommendations_lot_id", "lot_id"),
        Index("ix_recommendations_analysis_run_id", "analysis_run_id"),
        Index("ix_recommendations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation id={self.id} lot_id={self.lot_id} "
            f"generated_by={self.generated_by!r}>"
        )
