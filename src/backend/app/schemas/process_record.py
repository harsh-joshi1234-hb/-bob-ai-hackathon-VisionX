"""
schemas/process_record.py
--------------------------
Pydantic schemas for the PROCESS_RECORDS table.

The 24 feature fields (feature_00 … feature_23) are all Optional[float].
This mirrors the nullable columns in the ORM model — a partial record can
be submitted and stored; the inference layer validates completeness before
calling the SECOM model.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, model_validator


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class ProcessRecordCreate(BaseModel):
    """Fields required to store a new process/sensor record."""
    lot_id: UUID
    source_record_id: Optional[str] = Field(
        None,
        max_length=256,
        description="Upstream system row/record identifier (ERP, SECOM row index, etc.)",
    )

    # 24 SECOM model features — all optional so partial records are accepted.
    feature_00: Optional[float] = Field(None, description="SECOM model feature index 0")
    feature_01: Optional[float] = Field(None, description="SECOM model feature index 1")
    feature_02: Optional[float] = Field(None, description="SECOM model feature index 2")
    feature_03: Optional[float] = Field(None, description="SECOM model feature index 3")
    feature_04: Optional[float] = Field(None, description="SECOM model feature index 4")
    feature_05: Optional[float] = Field(None, description="SECOM model feature index 5")
    feature_06: Optional[float] = Field(None, description="SECOM model feature index 6")
    feature_07: Optional[float] = Field(None, description="SECOM model feature index 7")
    feature_08: Optional[float] = Field(None, description="SECOM model feature index 8")
    feature_09: Optional[float] = Field(None, description="SECOM model feature index 9")
    feature_10: Optional[float] = Field(None, description="SECOM model feature index 10")
    feature_11: Optional[float] = Field(None, description="SECOM model feature index 11")
    feature_12: Optional[float] = Field(None, description="SECOM model feature index 12")
    feature_13: Optional[float] = Field(None, description="SECOM model feature index 13")
    feature_14: Optional[float] = Field(None, description="SECOM model feature index 14")
    feature_15: Optional[float] = Field(None, description="SECOM model feature index 15")
    feature_16: Optional[float] = Field(None, description="SECOM model feature index 16")
    feature_17: Optional[float] = Field(None, description="SECOM model feature index 17")
    feature_18: Optional[float] = Field(None, description="SECOM model feature index 18")
    feature_19: Optional[float] = Field(None, description="SECOM model feature index 19")
    feature_20: Optional[float] = Field(None, description="SECOM model feature index 20")
    feature_21: Optional[float] = Field(None, description="SECOM model feature index 21")
    feature_22: Optional[float] = Field(None, description="SECOM model feature index 22")
    feature_23: Optional[float] = Field(None, description="SECOM model feature index 23")

    @model_validator(mode="after")
    def check_feature_completeness(self) -> "ProcessRecordCreate":
        """
        Warn (via a custom attribute) if any features are missing.
        Does NOT raise — storage of partial records is allowed.
        The inference endpoint must reject records with NULL features.
        """
        missing = [
            f"feature_{i:02d}"
            for i in range(24)
            if getattr(self, f"feature_{i:02d}") is None
        ]
        self._missing_features: List[str] = missing
        return self

    def to_feature_list(self) -> List[Optional[float]]:
        """Return values as an ordered list [f0 … f23] for model input."""
        return [getattr(self, f"feature_{i:02d}") for i in range(24)]


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class ProcessRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    source_record_id: Optional[str]

    feature_00: Optional[float]
    feature_01: Optional[float]
    feature_02: Optional[float]
    feature_03: Optional[float]
    feature_04: Optional[float]
    feature_05: Optional[float]
    feature_06: Optional[float]
    feature_07: Optional[float]
    feature_08: Optional[float]
    feature_09: Optional[float]
    feature_10: Optional[float]
    feature_11: Optional[float]
    feature_12: Optional[float]
    feature_13: Optional[float]
    feature_14: Optional[float]
    feature_15: Optional[float]
    feature_16: Optional[float]
    feature_17: Optional[float]
    feature_18: Optional[float]
    feature_19: Optional[float]
    feature_20: Optional[float]
    feature_21: Optional[float]
    feature_22: Optional[float]
    feature_23: Optional[float]

    created_at: datetime
