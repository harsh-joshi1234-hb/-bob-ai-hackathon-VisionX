from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.analysis_run import AnalysisRun
from app.models.lot import Lot
from app.models.prediction import Prediction

router = APIRouter(prefix="/api/analyses", tags=["analyses"])

@router.get("")
def list_analyses(db: Session = Depends(get_db)):
    """Returns a history of all analyses performed."""
    # Query AnalysisRun joined with Lot
    runs = db.query(AnalysisRun, Lot).join(Lot, AnalysisRun.lot_id == Lot.id).order_by(AnalysisRun.created_at.desc()).all()
    
    results = []
    for run, lot in runs:
        # Get overall prediction (using SECOM for risk, or just summarize)
        predictions = db.query(Prediction).filter(Prediction.lot_id == lot.id).all()
        
        wafer_pred = "Unknown"
        secom_pred = "Unknown"
        risk = "NORMAL"
        
        for p in predictions:
            if p.model_name == "wafermap_cnn":
                wafer_pred = p.predicted_class
            elif p.model_name == "secom_classifier":
                secom_pred = p.predicted_class
                if secom_pred == "FAIL":
                    risk = "CRITICAL"
                elif risk != "CRITICAL" and p.confidence and p.confidence > 0.4:
                    risk = "WATCH"
        
        results.append({
            "id": str(run.id),
            "lot_id": lot.lot_id,
            "type": "Demo Lot Analysis",
            "prediction": f"Process: {secom_pred} | Wafer: {wafer_pred}",
            "risk": risk,
            "timestamp": run.created_at.isoformat(),
            "status": run.status.value
        })
        
    return results
