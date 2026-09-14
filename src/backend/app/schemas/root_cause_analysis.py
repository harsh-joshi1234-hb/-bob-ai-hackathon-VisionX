"""
schemas/root_cause_analysis.py
-------------------------------
Pydantic schemas for the ROOT_CAUSE_ANALYSIS table.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ContributionDirectionEnum(str, enum.Enum):
    POSITIVE = "POSITIVE"   # increases P(FAIL)
    NEGATIVE = "NEGATIVE"   # decreases P(FAIL)
    NEUTRAL = "NEUTRAL"


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class RootCauseAnalysisCreate(BaseModel):
    lot_id: UUID
    analysis_run_id: Optional[UUID] = None
    feature_name: str = Field(
        ...,
        max_length=128,
        description="Sensor / feature name, e.g. 'feature_08' or a semantic name",
        examples=["feature_08"],
    )
    feature_index: Optional[int] = Field(
        None,
        ge=0,
        le=23,
        description="0-based index in the 24-feature model input vector",
    )
    contribution_value: float = Field(
        ...,
        description="Signed contribution magnitude, e.g. SHAP value",
    )
    rank: int = Field(
        ...,
        ge=1,
        description="1-based importance rank among all features for this lot",
    )
    direction: ContributionDirectionEnum = Field(
        ContributionDirectionEnum.NEUTRAL,
    )
    method: Optional[str] = Field(
        "shap",
        max_length=64,
        description="Explanation method: shap | permutation_importance | manual",
    )


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class RootCauseAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    analysis_run_id: Optional[UUID]
    feature_name: str
    feature_index: Optional[int]
    contribution_value: float
    rank: int
    direction: ContributionDirectionEnum
    method: Optional[str]
    created_at: datetime
