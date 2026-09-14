from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid

# Health Schemas
class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    models_loaded: bool
    timestamp: datetime

# Lots API Schemas
class WaferAnalysisSchema(BaseModel):
    prediction: str
    confidence: float

class ProcessAnalysisSchema(BaseModel):
    prediction: str
    probability: float

class RootCauseSchema(BaseModel):
    feature_name: str
    importance: float
    direction: str  # POSITIVE, NEGATIVE, NEUTRAL

class OverallRiskSchema(BaseModel):
    level: str  # HIGH, MEDIUM, LOW
    score: float

class RecommendationSchema(BaseModel):
    action: str
    reason: str

class AnalysisResponse(BaseModel):
    lot_id: str
    wafer_analysis: WaferAnalysisSchema
    process_analysis: ProcessAnalysisSchema
    root_causes: List[RootCauseSchema]
    overall_risk: OverallRiskSchema
    recommendations: List[RecommendationSchema]
    analysis_timestamp: datetime
