"""
schemas/analysis_run.py
------------------------
Pydantic schemas for the ANALYSIS_RUNS table.
"""

import enum
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RunStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class AnalysisRunCreate(BaseModel):
    lot_id: UUID
    status: RunStatusEnum = Field(RunStatusEnum.PENDING)
    model_versions: Optional[Dict[str, str]] = Field(
        None,
        description=(
            'Dict of model_name → version string. '
            'E.g. {"secom_classifier": "20240601", "wafermap_cnn": "20240601"}'
        ),
        examples=[{"secom_classifier": "20240601", "wafermap_cnn": "20240601"}],
    )


class AnalysisRunUpdate(BaseModel):
    """Patch applied by the pipeline as the run progresses."""
    status: Optional[RunStatusEnum] = None
    completed_at: Optional[datetime] = None
    secom_prediction_id: Optional[UUID] = None
    cnn_prediction_id: Optional[UUID] = None
    processing_time_ms: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class AnalysisRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    run_timestamp: datetime
    completed_at: Optional[datetime]
    status: RunStatusEnum
    model_versions: Optional[Dict[str, Any]]
    secom_prediction_id: Optional[UUID]
    cnn_prediction_id: Optional[UUID]
    processing_time_ms: Optional[int]
    error_message: Optional[str]
    notes: Optional[str]
    created_at: datetime
