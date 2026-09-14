"""
schemas/recommendation.py
--------------------------
Pydantic schemas for the RECOMMENDATIONS table.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ActionItem(BaseModel):
    """
    One structured action item inside the ``recommended_actions`` list.

    Example::

        {
            "action": "Inspect cooling unit on chamber C3",
            "priority": "HIGH",
            "target_parameter": "feature_08",
            "rationale": "Feature 8 contributed +2.34 SHAP points toward FAIL"
        }
    """
    action: str = Field(..., description="Plain-text description of the action to take")
    priority: Literal["HIGH", "MEDIUM", "LOW"] = Field("MEDIUM")
    target_parameter: Optional[str] = Field(
        None,
        description="The sensor / feature this action targets",
    )
    rationale: Optional[str] = Field(
        None,
        description="Why this action is recommended (links to RCA)",
    )


# ---------------------------------------------------------------------------
# Write schemas
# ---------------------------------------------------------------------------

class RecommendationCreate(BaseModel):
    lot_id: UUID
    analysis_run_id: Optional[UUID] = None
    summary: Optional[str] = Field(
        None,
        description="Plain-text executive summary of recommended actions",
    )
    recommended_actions: Optional[List[ActionItem]] = Field(
        None,
        description="Structured list of action items",
    )
    generated_by: Optional[str] = Field(
        "rule_engine",
        max_length=64,
        description="Source: rule_engine | watsonx_llm | manual",
    )


# ---------------------------------------------------------------------------
# Read schemas
# ---------------------------------------------------------------------------

class RecommendationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lot_id: UUID
    analysis_run_id: Optional[UUID]
    summary: Optional[str]
    recommended_actions: Optional[List[Dict[str, Any]]]
    generated_by: Optional[str]
    created_at: datetime
    updated_at: datetime
