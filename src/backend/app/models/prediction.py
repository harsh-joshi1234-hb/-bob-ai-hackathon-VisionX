"""
models/prediction.py
--------------------
PREDICTIONS table.

One row per model inference result.  Both models (SECOM classifier and
Wafer Map CNN) write here — distinguished by ``model_name``.

SECOM classifier outputs
    predicted_class  : "PASS" or "FAIL"
    confidence       : P(FAIL)  — scalar probability from predict_proba[:,1]
    probabilities    : {"PASS": 0.12, "FAIL": 0.88}

Wafer Map CNN outputs
    predicted_class  : one of the 9 defect pattern labels
    confidence       : max softmax probability (i.e. certainty of top class)
    probabilities    : {"Center": 0.01, "Donut": 0.03, …, "none": 0.88}
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
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ModelName(str, enum.Enum):
    """Identifies which trained model produced the prediction."""
    SECOM_CLASSIFIER = "secom_classifier"          # VotingClassifier (.pkl)
    WAFERMAP_CNN = "wafermap_cnn"                  # WaferMapCNN (.pth)


class Prediction(Base):
    """
    Columns
    -------
    id                   UUID primary key.
    lot_id               FK → lots.id.
    process_record_id    FK → process_records.id (nullable — wafer-map
                         predictions may not reference a process record).
    model_name           Which model produced this result.
    model_version        Freeform version string (e.g. git SHA or date tag).
    predicted_class      Human-readable predicted label.
    confidence           Primary probability / confidence score [0.0, 1.0].
                         For SECOM: P(FAIL).  For CNN: max softmax prob.
    probabilities        Full per-class probability dict stored as JSONB.
    raw_input_ref        Optional reference (path/id) to the raw input used,
                         useful for audit trails.
    prediction_timestamp Moment the inference was performed.
    created_at           Row insertion timestamp.
    """

    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    lot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    process_record_id = Column(
        UUID(as_uuid=True),
        ForeignKey("process_records.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    model_name = Column(
        SAEnum(ModelName, name="model_name_enum", create_type=True, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    model_version = Column(
        String(128),
        nullable=True,
        comment="Freeform version tag, e.g. git SHA or YYYYMMDD",
    )

    predicted_class = Column(
        String(64),
        nullable=False,
        comment="Human-readable label: PASS/FAIL for SECOM, defect pattern for CNN",
    )
    confidence = Column(
        Float,
        nullable=True,
        comment="Primary confidence score [0,1]. P(FAIL) for SECOM; max softmax for CNN.",
    )
    probabilities = Column(
        JSONB,
        nullable=True,
        comment='Full per-class probability dict, e.g. {"PASS": 0.12, "FAIL": 0.88}',
    )
    raw_input_ref = Column(
        String(512),
        nullable=True,
        comment="Optional path/key to the raw input used for this prediction (audit)",
    )

    prediction_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when the model inference was executed",
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    lot = relationship("Lot", back_populates="predictions")
    process_record = relationship("ProcessRecord")

    # ------------------------------------------------------------------
    # Indexes
    # ------------------------------------------------------------------
    __table_args__ = (
        Index("ix_predictions_lot_id", "lot_id"),
        Index("ix_predictions_model_name", "model_name"),
        Index("ix_predictions_predicted_class", "predicted_class"),
        Index("ix_predictions_prediction_timestamp", "prediction_timestamp"),
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction id={self.id} lot_id={self.lot_id} "
            f"model={self.model_name} class={self.predicted_class!r} "
            f"conf={self.confidence}>"
        )
