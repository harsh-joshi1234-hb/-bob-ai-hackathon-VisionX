"""
schemas/upcoming_batch.py
--------------------------
Pydantic schemas for the UPCOMING_BATCHES table.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RiskLevelEnum(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class BatchStatusEnum(str, enum.Enum):
    FLAGGED = "FLAGGED"
    CLEARED = "CLEARED"
    ON_HOLD = "ON_HOLD"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class UpcomingBatchCreate(BaseModel):
    batch_id: str = Field(
        ...,
        max_length=128,
        description="Human-readable fab batch identifier, e.g. 'BATCH-2024-005'",
        examples=["BATCH-2024-005"],
    )
    process_record_id: Optional[UUID] = Field(
        None,
        description="FK to process_records — the projected sensor values for this batch",
    )
    predicted_risk: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Estimated P(FAIL) in [0, 1]",
    )
    risk_level: RiskLevelEnum = Field(RiskLevelEnum.UNKNOWN)
    flag_reason: Optional[str] = Field(
        None,
        description="Plain-text explanation of why the batch was flagged",
    )
    status: BatchStatusEnum = Field(BatchStatusEnum.FLAGGED)
    scheduled_at: Optional[datetime] = Field(
        None,
        description="Planned manufacture / processing datetime (timezone-aware)",
    )


class UpcomingBatchUpdate(BaseModel):
    """Fields that can be patched by an engineer reviewing a flagged batch."""
    status: Optional[BatchStatusEnum] = None
    flag_reason: Optional[str] = None
    predicted_risk: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_level: Optional[RiskLevelEnum] = None
    scheduled_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class UpcomingBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    batch_id: str
    process_record_id: Optional[UUID]
    predicted_risk: Optional[float]
    risk_level: RiskLevelEnum
    flag_reason: Optional[str]
    status: BatchStatusEnum
    scheduled_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
