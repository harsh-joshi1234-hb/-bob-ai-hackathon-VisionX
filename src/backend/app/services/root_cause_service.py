import numpy as np
try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.root_cause_analysis import RootCauseAnalysis, ContributionDirection
from app.services.model_service import model_service

class RootCauseService:
    def compute_contributions(self, process_features: np.ndarray, limit: int = 10):
        if model_service.secom_model is None:
            raise RuntimeError("SECOM model not loaded")

        features = np.array(process_features, dtype=np.float64)
        if features.ndim == 1:
            features = features.reshape(1, -1)

        explainer_method = "shap_kernel_zero_bg"
        shap_values = None

        if HAS_SHAP:
            try:
                # Attempt to extract a RandomForest sub-estimator to use fast TreeExplainer
                rf_estimator = None
                if hasattr(model_service.secom_model, "estimators_"):
                    for est in model_service.secom_model.estimators_:
                        if est.__class__.__name__ in ("RandomForestClassifier", "XGBClassifier"):
                            rf_estimator = est
                            break
                
                if rf_estimator is not None:
                    explainer = shap.TreeExplainer(rf_estimator)
                    shap_vals = explainer.shap_values(features)
                    
                    if isinstance(shap_vals, list):
                        shap_values = shap_vals[1][0] 
                    else:
                        if shap_vals.ndim == 2:
                            shap_values = shap_vals[0]
                        elif shap_vals.ndim == 3:
                            shap_values = shap_vals[:, :, 1][0]
                    explainer_method = f"shap_tree_{rf_estimator.__class__.__name__.lower()}"
            except Exception:
                shap_values = None

            if shap_values is None:
                try:
                    # Fallback: KernelExplainer on the VotingClassifier's predict_proba
                    background = np.zeros((1, features.shape[1]))
                    def predict_fn(x):
                        return model_service.secom_model.predict_proba(x)[:, 1]
                        
                    explainer = shap.KernelExplainer(predict_fn, background)
                    shap_vals = explainer.shap_values(features)
                    
                    if isinstance(shap_vals, list):
                        shap_values = shap_vals[1][0]
                    else:
                        shap_values = shap_vals[0] if shap_vals.ndim > 1 else shap_vals
                    
                    explainer_method = "shap_kernel_zero_bg"
                except Exception:
                    shap_values = None

        if shap_values is None:
            # Empirical sensitivity perturbation fallback
            base_risk = model_service.predict_process_risk(features[0])
            base_prob = base_risk.get("failure_probability") or 0.5
            shap_values = np.zeros(features.shape[1])
            for i in range(features.shape[1]):
                perturbed = features.copy()
                perturbed[0, i] = 0.0
                p_pert = model_service.predict_process_risk(perturbed[0]).get("failure_probability") or 0.5
                shap_values[i] = float(base_prob - p_pert)
            explainer_method = "empirical_sensitivity_delta"

        abs_contribs = np.abs(shap_values)
        top_indices = np.argsort(abs_contribs)[-limit:][::-1]
        
        results = []
        for idx in top_indices:
            val = float(shap_values[idx])
            if val > 0:
                direction = ContributionDirection.POSITIVE
            elif val < 0:
                direction = ContributionDirection.NEGATIVE
            else:
                direction = ContributionDirection.NEUTRAL
                
            results.append({
                "feature_index": int(idx),
                "feature_name": f"Feature_{int(idx):03d}",
                "contribution_value": val,
                "direction": direction,
                "method": explainer_method
            })
            
        return results

    def analyze_root_causes(self, lot_id: UUID, process_features: np.ndarray, run_id: UUID, db: Session, limit: int = 10) -> List[RootCauseAnalysis]:
        """
        Uses SHAP to determine the top contributing features for the SECOM classifier prediction.
        Supports fallback methods if the primary TreeExplainer fails.
        """
        contributions = self.compute_contributions(process_features, limit)
        
        # Remove old RCA entries for this run if any
        if run_id and db:
            db.query(RootCauseAnalysis).filter(
                RootCauseAnalysis.analysis_run_id == run_id
            ).delete()

        root_causes = []
        rank = 1
        for contrib in contributions:
            rca = RootCauseAnalysis(
                lot_id=lot_id,
                analysis_run_id=run_id,
                feature_name=contrib["feature_name"],
                feature_index=contrib["feature_index"],
                contribution_value=contrib["contribution_value"],
                rank=rank,
                direction=contrib["direction"],
                method=contrib["method"]
            )
            if db:
                db.add(rca)
            root_causes.append(rca)
            rank += 1
            
        if db:
            db.commit()
        return root_causes

root_cause_service = RootCauseService()
