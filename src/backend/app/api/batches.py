from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.upcoming_batch import UpcomingBatch
from app.services.batch_risk_service import batch_risk_service
from app.schemas.upcoming_batch import UpcomingBatchRead

router = APIRouter(prefix="/api/batches", tags=["batches"])

@router.get("/upcoming", response_model=List[UpcomingBatchRead])
def get_upcoming_batches(db: Session = Depends(get_db)):
    """Returns a list of all upcoming batches."""
    batches = db.query(UpcomingBatch).order_by(UpcomingBatch.scheduled_at).all()
    return batches

@router.get("/{batch_id}", response_model=UpcomingBatchRead)
def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Returns details of a specific upcoming batch."""
    batch = db.query(UpcomingBatch).filter(UpcomingBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    return batch

@router.post("/{batch_id}/analyze")
def analyze_upcoming_batch(batch_id: str, db: Session = Depends(get_db)):
    """
    Analyzes an upcoming batch for risk and returns a dashboard-ready response.
    """
    try:
        result = batch_risk_service.analyze_batch(batch_id, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
