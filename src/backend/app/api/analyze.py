from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from datetime import datetime
import numpy as np
import pandas as pd
import cv2
import io

from app.schemas.api import (
    AnalysisResponse, WaferAnalysisSchema, ProcessAnalysisSchema,
    RootCauseSchema, OverallRiskSchema, RecommendationSchema
)
from app.services.model_service import model_service

router = APIRouter(prefix="/api/analyze", tags=["analyze"])

@router.post("/wafer")
async def analyze_wafer(file: UploadFile = File(...)):
    """Analyze a single uploaded wafer image."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
            
        wafer_res = model_service.predict_wafer(img)
        wafer_pred = wafer_res["prediction"]
        wafer_conf = wafer_res["probability"].get(wafer_pred, 0.0) if wafer_res.get("probability") else 0.0
        
        return {
            "prediction": wafer_pred,
            "confidence": wafer_conf,
            "model": wafer_res.get("model", "wafermap_cnn"),
            "timestamp": wafer_res.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def analyze_process(file: UploadFile = File(...)):
    """Analyze a single uploaded process CSV."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Check if CSV has enough numeric columns (need 24)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) < 24:
            raise HTTPException(status_code=400, detail=f"CSV missing required features. Found {len(numeric_cols)}, expected 24.")
        
        features = df[numeric_cols[:24]].iloc[0].values.tolist()
        
        secom_res = model_service.predict_secom(features)
        secom_pred = secom_res["prediction"]
        secom_prob = secom_res["probability"].get("FAIL", 0.0) if secom_res.get("probability") else (1.0 if secom_pred == "FAIL" else 0.0)
        
        return {
            "prediction": secom_pred,
            "probability": secom_prob,
            "model": secom_res.get("model", "secom_classifier"),
            "timestamp": secom_res.get("timestamp")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/new-lot", response_model=AnalysisResponse)
async def analyze_new_lot(
    lot_id: str = Form(...),
    waferFile: Optional[UploadFile] = File(None),
    processFile: Optional[UploadFile] = File(None)
):
    """Analyze a completely new lot with optionally an image and a CSV."""
    
    wafer_pred, wafer_conf = "Unknown", 0.0
    secom_pred, secom_prob = "Unknown", 0.0
    
    if waferFile:
        contents = await waferFile.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            wafer_res = model_service.predict_wafer(img)
            wafer_pred = wafer_res["prediction"]
            wafer_conf = wafer_res["probability"].get(wafer_pred, 0.0) if wafer_res.get("probability") else 0.0

    if processFile:
        contents = await processFile.read()
        df = pd.read_csv(io.BytesIO(contents))
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 24:
            features = df[numeric_cols[:24]].iloc[0].values.tolist()
            secom_res = model_service.predict_secom(features)
            secom_pred = secom_res["prediction"]
            secom_prob = secom_res["probability"].get("FAIL", 0.0) if secom_res.get("probability") else (1.0 if secom_pred == "FAIL" else 0.0)

    # Simple logic for risk score
    risk_score = 0
    if secom_pred == "FAIL":
        risk_score += 60
    if wafer_pred not in ["none", "Unknown"]:
        risk_score += 40
        
    level = "LOW"
    if risk_score > 70:
        level = "HIGH"
    elif risk_score > 30:
        level = "MEDIUM"

    return AnalysisResponse(
        lot_id=lot_id,
        wafer_analysis=WaferAnalysisSchema(prediction=wafer_pred, confidence=wafer_conf),
        process_analysis=ProcessAnalysisSchema(prediction=secom_pred, probability=secom_prob),
        root_causes=[], # Dynamic uploads don't have DB records for full RCA currently
        overall_risk=OverallRiskSchema(level=level, score=risk_score),
        recommendations=[],
        ai_explanation=None,
        analysis_timestamp=datetime.now()
    )
