from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.schemas.api import HealthResponse
from app.services.model_service import model_service
from datetime import datetime, timezone

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """
    Check system health including DB connectivity and ML models status.
    """
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass

    models_loaded = (model_service.secom_model is not None) and (model_service.wafermap_model is not None)
    
    status = "OK" if (db_connected and models_loaded) else "DEGRADED"

    return HealthResponse(
        status=status,
        db_connected=db_connected,
        models_loaded=models_loaded,
        timestamp=datetime.now(timezone.utc)
    )
