from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lot import Lot, LotStatus
from app.models.process_record import ProcessRecord
from app.models.analysis_run import AnalysisRun, RunStatus
from app.models.prediction import Prediction, ModelName
from app.models.root_cause_analysis import RootCauseAnalysis, ContributionDirection
from app.models.recommendation import Recommendation
from app.schemas.api import (
    AnalysisResponse, WaferAnalysisSchema, ProcessAnalysisSchema,
    RootCauseSchema, OverallRiskSchema, RecommendationSchema
)
from app.services.model_service import model_service
from app.services.root_cause_service import root_cause_service
from app.services.ai_explanation_service import ai_explanation_service
from datetime import datetime, timezone
import numpy as np
import os
import uuid
import json

router = APIRouter(prefix="/api/lots", tags=["lots"])

@router.get("")
def list_lots(db: Session = Depends(get_db)):
    """Returns available demo lots."""
    lots = db.query(Lot).all()
    return [{"id": str(lot.id), "lot_id": lot.lot_id, "status": lot.status.value, "wafer_image_path": lot.wafer_image_path} for lot in lots]

@router.get("/{lot_id}")
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    """Returns lot information, wafer image path, and process record information."""
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
        
    process_records = db.query(ProcessRecord).filter(ProcessRecord.lot_id == lot.id).all()
    records_data = []
    for pr in process_records:
        records_data.append({
            "id": str(pr.id),
            "source_record_id": pr.source_record_id,
            "features": pr.to_feature_vector()
        })
        
    return {
        "id": str(lot.id),
        "lot_id": lot.lot_id,
        "status": lot.status.value,
        "wafer_image_path": lot.wafer_image_path,
        "process_records": records_data
    }

@router.post("/{lot_id}/analyze", response_model=AnalysisResponse)
def analyze_lot(lot_id: str, db: Session = Depends(get_db)):
    """
    Main orchestration endpoint to analyze a lot using both models.
    
    Note: Demo lot IDs (e.g. LOT-001) are application-level integration identifiers 
    used to demonstrate multimodal analysis across independent public datasets 
    (WM-811K and SECOM). They do not represent real physical lots.
    """
    # Step 1: Load lot
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
        
    # Create Analysis Run
    run = AnalysisRun(lot_id=lot.id, status=RunStatus.RUNNING)
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        # Step 2: Load wafer image/input
        wafer_input = None
        if lot.wafer_image_path and os.path.exists(lot.wafer_image_path):
            if lot.wafer_image_path.endswith('.npy'):
                wafer_input = np.load(lot.wafer_image_path)
            else:
                import cv2
                img = cv2.imread(lot.wafer_image_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    wafer_input = img
        
        # Fallback to mock data for demo if image is missing/unreadable
        if wafer_input is None:
            wafer_input = np.random.randint(0, 3, size=(64, 64))

        # Step 3: Load process record
        process_record = db.query(ProcessRecord).filter(ProcessRecord.lot_id == lot.id).first()
        if not process_record:
            raise HTTPException(status_code=400, detail="No process record found for this lot. SECOM model requires 24 features.")
        
        features = process_record.to_feature_vector()
        if None in features:
            # Impute missing values with 0 for demo purposes
            features = [0.0 if f is None else f for f in features]

        # Step 4: Run Wafer model
        wafer_res = model_service.predict_wafer(wafer_input)
        
        # Step 5: Run SECOM model
        secom_res = model_service.predict_secom(features)

        # Step 6: Generate model outputs dynamically
        wafer_pred = wafer_res["prediction"]
        wafer_conf = wafer_res["probability"].get(wafer_pred, 0.0)
        
        secom_pred = secom_res["prediction"]
        secom_prob = secom_res["probability"].get("FAIL", 0.0) if secom_res.get("probability") else (1.0 if secom_pred == "FAIL" else 0.0)

        # Save Predictions to DB
        pred_wafer = Prediction(
            lot_id=lot.id,
            model_name=ModelName.WAFERMAP_CNN,
            predicted_class=wafer_pred,
            confidence=wafer_conf
        )
        pred_secom = Prediction(
            lot_id=lot.id,
            process_record_id=process_record.id,
            model_name=ModelName.SECOM_CLASSIFIER,
            predicted_class=secom_pred,
            confidence=secom_prob
        )
        db.add_all([pred_wafer, pred_secom])

        # Step 7: Run root-cause analysis
        root_causes = []
        try:
            rca_entries = root_cause_service.analyze_root_causes(
                lot_id=lot.id,
                process_features=features,
                run_id=run.id,
                db=db,
                limit=5
            )
            for rc in rca_entries:
                root_causes.append(RootCauseSchema(
                    feature_name=rc.feature_name,
                    importance=rc.contribution_value,
                    direction=rc.direction.value
                ))
        except Exception as e:
            # Fallback if RCA fails
            print(f"RCA Failed: {str(e)}")
            pass

        # Step 8: Generate overall risk assessment
        risk_level = "LOW"
        risk_score = (secom_prob * 0.6) + (wafer_conf * 0.4 if wafer_pred != 'none' else 0)
        
        if secom_pred == "FAIL" or (wafer_pred != 'none' and wafer_conf > 0.8):
            risk_level = "HIGH"
        elif secom_prob > 0.3 or wafer_pred != 'none':
            risk_level = "MEDIUM"
            
        # Recommendations
        recommendations = []
        if risk_level == "HIGH":
            rec = Recommendation(
                lot_id=lot.id,
                analysis_run_id=run.id,
                recommended_action="Hold lot for immediate manual inspection.",
                justification_summary="High failure probability predicted by SECOM model or severe defect pattern detected."
            )
            db.add(rec)
            recommendations.append(RecommendationSchema(action=rec.recommended_action, reason=rec.justification_summary))
        elif risk_level == "MEDIUM":
            rec = Recommendation(
                lot_id=lot.id,
                analysis_run_id=run.id,
                recommended_action="Schedule for secondary review.",
                justification_summary="Elevated risk factors detected."
            )
            db.add(rec)
            recommendations.append(RecommendationSchema(action=rec.recommended_action, reason=rec.justification_summary))

        # Update Lot status
        lot.status = LotStatus.COMPLETE
        
        # Update Run status
        run.status = RunStatus.SUCCESS
        run.completed_at = datetime.now(timezone.utc)
        
        db.commit()

        # Step 9: Optionally call LLM for explanation
        try:
            explanation = ai_explanation_service.generate_explanation(
                lot_id=lot.lot_id,
                wafer_prediction=wafer_pred,
                wafer_confidence=wafer_conf,
                process_prediction=secom_pred,
                process_probability=secom_prob,
                shap_rankings=[{"feature": rc.feature_name, "contribution": rc.importance} for rc in root_causes],
                historical_comparison=None,
                upcoming_batch_risk=None
            )
        except Exception as e:
            explanation = {"status": "unavailable", "message": f"Explanation service failed: {str(e)}"}
            
        # Step 10: Return structured response
        return AnalysisResponse(
            lot_id=lot.lot_id,
            wafer_analysis=WaferAnalysisSchema(prediction=wafer_pred, confidence=wafer_conf),
            process_analysis=ProcessAnalysisSchema(prediction=secom_pred, probability=secom_prob),
            root_causes=root_causes,
            overall_risk=OverallRiskSchema(level=risk_level, score=risk_score),
            recommendations=recommendations,
            ai_explanation=explanation,
            analysis_timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        db.rollback()
        run.status = RunStatus.FAILED
        run.error_message = str(e)
        lot.status = LotStatus.FAILED
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/{lot_id}/root-causes")
def get_root_causes(lot_id: str, db: Session = Depends(get_db)):
    """Returns the top contributing features for the lot's analysis."""
    lot = db.query(Lot).filter(Lot.lot_id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
        
    rca_entries = db.query(RootCauseAnalysis).filter(
        RootCauseAnalysis.lot_id == lot.id
    ).order_by(RootCauseAnalysis.rank).all()
    
    result = []
    for rca in rca_entries:
        if rca.direction == ContributionDirection.POSITIVE:
            direction_str = "increases_risk"
        elif rca.direction == ContributionDirection.NEGATIVE:
            direction_str = "decreases_risk"
        else:
            direction_str = "neutral"
            
        result.append({
            "feature": rca.feature_name,
            "contribution": round(rca.contribution_value, 4),
            "direction": direction_str,
            "rank": rca.rank
        })
        
    return {"root_causes": result}

