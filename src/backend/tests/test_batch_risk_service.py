import pytest
import numpy as np
import uuid
from unittest.mock import MagicMock
from app.services.batch_risk_service import batch_risk_service
from app.services.model_service import model_service
from app.services.root_cause_service import root_cause_service
from app.models.upcoming_batch import RiskLevel, BatchStatus
from app.models.root_cause_analysis import ContributionDirection

@pytest.fixture
def mock_db_session():
    db = MagicMock()
    return db

@pytest.fixture
def mock_secom_model():
    model = MagicMock()
    model.predict_proba.return_value = np.array([[0.3, 0.85]]) # 85% P(FAIL) => HIGH risk
    model.prediction = "FAIL"
    return model

def test_analyze_batch_high_risk(mock_db_session, mock_secom_model, monkeypatch):
    """
    Test BatchRiskService logic for a high-risk batch
    """
    model_service.secom_model = mock_secom_model
    
    # Mock DB queries
    batch_id = "B-1043"
    mock_batch = MagicMock()
    mock_batch.batch_id = batch_id
    mock_batch.process_record_id = uuid.uuid4()
    
    mock_process_record = MagicMock()
    mock_process_record.to_feature_vector.return_value = np.random.rand(24).tolist()
    
    # Setup the mock DB session query return values
    def mock_query(model):
        query_mock = MagicMock()
        if model.__name__ == 'UpcomingBatch':
            query_mock.filter.return_value.first.return_value = mock_batch
        elif model.__name__ == 'ProcessRecord':
            query_mock.filter.return_value.first.return_value = mock_process_record
        return query_mock
        
    mock_db_session.query.side_effect = mock_query
    
    # Mock root_cause_service.compute_contributions
    mock_contributions = [
        {"feature_name": "Feature_012", "contribution_value": 0.45, "direction": ContributionDirection.POSITIVE, "method": "shap_kernel_zero_bg", "feature_index": 12},
        {"feature_name": "Feature_004", "contribution_value": 0.22, "direction": ContributionDirection.POSITIVE, "method": "shap_kernel_zero_bg", "feature_index": 4},
    ]
    monkeypatch.setattr(root_cause_service, 'compute_contributions', lambda f, limit: mock_contributions)
    
    result = batch_risk_service.analyze_batch(batch_id, mock_db_session)
    
    # Verify the output matches dashboard-ready requirements
    assert result["batch_id"] == "B-1043"
    assert result["risk"] == 0.85
    assert result["risk_level"] == RiskLevel.HIGH.value
    assert len(result["top_signals"]) == 2
    assert result["top_signals"][0]["feature"] == "Feature_012"
    assert "Engineering Recommendation: Hold batch" in result["recommended_action"]
    
    # Verify separation of model prediction and historical correlation
    assert "Model Prediction: 85.0% failure probability." in result["reason"]
    assert "Historical Correlation:" in result["reason"]
    assert "Feature_012, Feature_004" in result["reason"]
    
    # Verify DB commit was called
    mock_db_session.commit.assert_called_once()
    
    # Verify batch attributes were updated
    assert mock_batch.predicted_risk == 0.85
    assert mock_batch.risk_level == RiskLevel.HIGH
    assert mock_batch.status == BatchStatus.FLAGGED
