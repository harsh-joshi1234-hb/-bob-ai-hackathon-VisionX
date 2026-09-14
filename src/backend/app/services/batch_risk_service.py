import numpy as np
from sqlalchemy.orm import Session
from app.models.upcoming_batch import UpcomingBatch, RiskLevel, BatchStatus
from app.models.process_record import ProcessRecord
from app.services.model_service import model_service
from app.services.root_cause_service import root_cause_service
from app.models.root_cause_analysis import ContributionDirection
import json

class BatchRiskService:
    def analyze_batch(self, batch_id: str, db: Session):
        """
        Analyzes an upcoming batch for risk of failure based on its projected process parameters.
        Applies SECOM model inference and determines contributing signals.
        """
        batch = db.query(UpcomingBatch).filter(UpcomingBatch.batch_id == batch_id).first()
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
            
        if not batch.process_record_id:
            raise ValueError(f"Batch {batch_id} missing process_record_id")
            
        process_record = db.query(ProcessRecord).filter(ProcessRecord.id == batch.process_record_id).first()
        if not process_record:
            raise ValueError("Process record not found")
            
        # Apply the exact preprocessing expected by the SECOM model
        features = process_record.to_feature_vector()
        if None in features:
            features = [0.0 if f is None else f for f in features]
            
        # Run inference using SECOM model
        secom_res = model_service.predict_secom(features)
        
        # Risk thresholds based on upcoming_batch.py docstring
        # HIGH   → P(FAIL) >= 0.70
        # MEDIUM → P(FAIL) >= 0.40
        # LOW    → P(FAIL) <  0.40
        if secom_res.get("probability"):
            predicted_risk = secom_res["probability"].get("FAIL", 0.0)
        else:
            # If probability is unavailable, use the available model output
            predicted_risk = 1.0 if secom_res["prediction"] == "FAIL" else 0.0
            
        if predicted_risk >= 0.70:
            risk_level = RiskLevel.HIGH
            status = BatchStatus.FLAGGED
            recommended_action = "Engineering Recommendation: Hold batch. Requires immediate engineer review of out-of-control parameters."
        elif predicted_risk >= 0.40:
            risk_level = RiskLevel.MEDIUM
            status = BatchStatus.FLAGGED
            recommended_action = "Engineering Recommendation: Schedule secondary review before manufacturing."
        else:
            risk_level = RiskLevel.LOW
            status = BatchStatus.CLEARED
            recommended_action = "Engineering Recommendation: Proceed with manufacturing."
            
        # Get top signals using root_cause_service (model prediction attribution)
        contributions = root_cause_service.compute_contributions(features, limit=5)
        
        top_signals = []
        signal_names = []
        for i, c in enumerate(contributions):
            if c["direction"] == ContributionDirection.POSITIVE:
                direction_str = "increases_risk"
            elif c["direction"] == ContributionDirection.NEGATIVE:
                direction_str = "decreases_risk"
            else:
                direction_str = "neutral"
                
            top_signals.append({
                "feature": c["feature_name"],
                "contribution": round(c["contribution_value"], 4),
                "direction": direction_str,
                "rank": i + 1
            })
            if c["direction"] == ContributionDirection.POSITIVE:
                signal_names.append(c["feature_name"])
        
        reason = f"Model Prediction: {predicted_risk*100:.1f}% failure probability. "
        if signal_names:
            reason += f"Historical Correlation: Elevated risk is historically correlated with signals: {', '.join(signal_names[:3])}. Note: This correlation does not imply causal relationship."
            
        # Update batch record
        batch.predicted_risk = predicted_risk
        batch.risk_level = risk_level
        batch.status = status
        batch.flag_reason = reason
        db.commit()
        
        return {
            "batch_id": batch.batch_id,
            "risk": predicted_risk,
            "risk_level": risk_level.value,
            "top_signals": top_signals,
            "reason": reason,
            "recommended_action": recommended_action
        }

batch_risk_service = BatchRiskService()
