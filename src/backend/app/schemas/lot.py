"""
schemas/lot.py
--------------
Pydantic schemas for the LOTS table.
"""

import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class LotStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    ARCHIVED = "ARCHIVED"


# ---------------------------------------------------------------------------
# Write schemas (API → DB)
# ---------------------------------------------------------------------------

class LotCreate(BaseModel):
    """Fields required to create a new lot."""
    lot_id: str = Field(
        ...,
        max_length=128,
        description="Human-readable fab lot identifier, e.g. 'LOT-2024-001234'",
        examples=["LOT-2024-001234"],
    )
    wafer_image_path: Optional[str] = Field(
        None,
        max_length=512,
        description="Relative path or object-storage key to the wafer-map image",
    )
    status: LotStatusEnum = Field(
        LotStatusEnum.PENDING,
        description="Initial pipeline state for this lot",
    )


class LotUpdate(BaseModel):
    """Fields that can be patched on an existing lot."""
    wafer_image_path: Optional[str] = Field(None, max_length=512)
    status: Optional[LotStatusEnum] = None


# ---------------------------------------------------------------------------
# Read schemas (DB → API response)
# ---------------------------------------------------------------------------

class LotRead(BaseModel):
    """Full lot representation returned by GET endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: str
    wafer_image_path: Optional[str]
    status: LotStatusEnum
    created_at: datetime
    updated_at: datetime
