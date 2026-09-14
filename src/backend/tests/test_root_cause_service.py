import pytest
import numpy as np
import uuid
from unittest.mock import MagicMock
from app.services.root_cause_service import root_cause_service
from app.services.model_service import model_service
from app.models.root_cause_analysis import ContributionDirection

@pytest.fixture
def mock_db_session():
    db = MagicMock()
    # mock query().filter().delete()
    db.query.return_value.filter.return_value.delete.return_value = 0
    return db

@pytest.fixture
def mock_secom_model():
    model = MagicMock()
    # Mock predict_proba for 1 sample and 2 classes
    model.predict_proba.return_value = np.array([[0.3, 0.7]])
    
    # We will simulate a VotingClassifier WITHOUT RandomForest to force KernelExplainer fallback
    model.estimators_ = [MagicMock(__class__=MagicMock(__name__="SVC"))]
    return model

def test_analyze_root_causes_kernel_fallback(mock_db_session, mock_secom_model):
    """
    Test RootCauseService using the KernelExplainer fallback (when TreeExplainer is not applicable).
    """
    model_service.secom_model = mock_secom_model
    lot_id = uuid.uuid4()
    run_id = uuid.uuid4()
    
    # 24 features
    features = np.random.rand(24)
    
    # Mocking shap KernelExplainer inside root_cause_service is tricky without monkeypatch,
    # but KernelExplainer itself will just call model_service.secom_model.predict_proba
    # Actually, shap.KernelExplainer will work if predict_proba returns proper values.
    # We'll just run it. It might take a moment.
    # Wait, shap is installed? If not, this might fail, but let's assume standard testing environment.
    
    # To make it fast and avoid real shap computation in tests, we could mock shap.
    # But since it's just 1 instance and a mock predict_fn that returns constant, it's very fast.
    
    results = root_cause_service.analyze_root_causes(
        lot_id=lot_id,
        process_features=features,
        run_id=run_id,
        db=mock_db_session,
        limit=5
    )
    
    assert len(results) == 5
    assert results[0].method == "shap_kernel_zero_bg"
    assert results[0].lot_id == lot_id
    assert results[0].analysis_run_id == run_id
    
    # DB commit should be called
    mock_db_session.commit.assert_called_once()
    
def test_analyze_root_causes_tree_explainer(mock_db_session):
    """
    Test RootCauseService when a RandomForestClassifier is available.
    """
    model = MagicMock()
    
    class DummyRF:
        pass
        
    DummyRF.__name__ = "RandomForestClassifier"
    rf_mock = MagicMock()
    rf_mock.__class__ = DummyRF
    
    model.estimators_ = [rf_mock]
    model_service.secom_model = model
    
    # We need to mock shap.TreeExplainer because we passed a fake model
    import shap
    
    class FakeExplainer:
        def __init__(self, model):
            pass
        def shap_values(self, X):
            # simulate 2 classes, 24 features for 1 sample
            # return shape (1, 24, 2) or list of arrays [ (1, 24), (1, 24) ]
            return [np.zeros((1, 24)), np.random.randn(1, 24)]
            
    original_tree = shap.TreeExplainer
    shap.TreeExplainer = FakeExplainer
    
    try:
        lot_id = uuid.uuid4()
        run_id = uuid.uuid4()
        features = np.random.rand(24)
        
        results = root_cause_service.analyze_root_causes(
            lot_id=lot_id,
            process_features=features,
            run_id=run_id,
            db=mock_db_session,
            limit=10
        )
        
        assert len(results) == 10
        assert results[0].method == "shap_tree_dummyrf"
    finally:
        shap.TreeExplainer = original_tree
