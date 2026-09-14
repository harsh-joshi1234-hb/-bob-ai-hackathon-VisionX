"""
schemas/prediction.py
---------------------
Pydantic schemas for the PREDICTIONS table.
"""

import enum
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ModelNameEnum(str, enum.Enum):
    SECOM_CLASSIFIER = "secom_classifier"
    WAFERMAP_CNN = "wafermap_cnn"


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class PredictionCreate(BaseModel):
    lot_id: UUID
    process_record_id: Optional[UUID] = None
    model_name: ModelNameEnum
    model_version: Optional[str] = Field(None, max_length=128)
    predicted_class: str = Field(
        ...,
        max_length=64,
        description=(
            "Human-readable label. "
            "SECOM: 'PASS' or 'FAIL'. "
            "CNN: 'Center' | 'Donut' | 'Edge-Loc' | 'Edge-Ring' | "
            "'Loc' | 'Random' | 'Scratch' | 'Near-full' | 'none'"
        ),
        examples=["FAIL", "Edge-Ring"],
    )
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description=(
            "Primary confidence score in [0,1]. "
            "For SECOM: P(FAIL). For CNN: max softmax probability."
        ),
    )
    probabilities: Optional[Dict[str, float]] = Field(
        None,
        description='Full per-class probability dict, e.g. {"PASS": 0.12, "FAIL": 0.88}',
    )
    raw_input_ref: Optional[str] = Field(None, max_length=512)


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class PredictionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    process_record_id: Optional[UUID]
    model_name: ModelNameEnum
    model_version: Optional[str]
    predicted_class: str
    confidence: Optional[float]
    probabilities: Optional[Dict[str, Any]]
    raw_input_ref: Optional[str]
    prediction_timestamp: datetime
    created_at: datetime
