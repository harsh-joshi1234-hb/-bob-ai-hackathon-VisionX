# src/backend/app/models package
# Import all models here so that Alembic's env.py can discover every table
# by doing: from app.models import *

from app.models.lot import Lot
from app.models.process_record import ProcessRecord
from app.models.prediction import Prediction
from app.models.root_cause_analysis import RootCauseAnalysis
from app.models.recommendation import Recommendation
from app.models.upcoming_batch import UpcomingBatch
from app.models.analysis_run import AnalysisRun
from app.models.demo_lot_mapping import DemoLotMapping

__all__ = [
    "Lot",
    "ProcessRecord",
    "Prediction",
    "RootCauseAnalysis",
    "Recommendation",
    "UpcomingBatch",
    "AnalysisRun",
]
