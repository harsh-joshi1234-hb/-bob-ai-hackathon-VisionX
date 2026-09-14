import os
import pytest
import numpy as np
from app.services.model_service import model_service

# Paths to the actual models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECOM_PATH = os.path.join(BASE_DIR, "ml", "secom_classifier_model.pkl")
WAFERMAP_PATH = os.path.join(BASE_DIR, "ml", "wafermap_dl_model.pth")

@pytest.fixture(scope="module")
def loaded_service():
    """
    Loads models once for the entire test module.
    """
    model_service.load_models(SECOM_PATH, WAFERMAP_PATH)
    return model_service

def test_load_models_invalid_path():
    """
    Test that invalid model paths raise a clear error.
    """
    try:
        model_service.load_models("invalid/path.pkl", WAFERMAP_PATH)
        assert False, "Should have raised FileNotFoundError for missing SECOM model"
    except FileNotFoundError:
        pass
        
    try:
        model_service.load_models(SECOM_PATH, "invalid/path.pth")
        assert False, "Should have raised FileNotFoundError for missing WaferMap model"
    except FileNotFoundError:
        pass

def test_predict_secom_valid_input(loaded_service):
    """
    Test SECOM prediction with a valid 24-feature input using real model inference.
    """
    # Create a dummy valid input matching expected shape (24 features)
    dummy_input = np.random.rand(24).tolist()
    
    result = loaded_service.predict_secom(dummy_input)
    
    assert "model" in result
    assert result["model"] == "secom_classifier"
    assert "prediction" in result
    assert result["prediction"] in ["PASS", "FAIL"]
    assert "probability" in result
    
    if result["probability"] is not None:
        assert "PASS" in result["probability"]
        assert "FAIL" in result["probability"]
        # Probabilities should sum to approximately 1.0
        total_prob = result["probability"]["PASS"] + result["probability"]["FAIL"]
        assert 0.99 < total_prob < 1.01

def test_predict_secom_invalid_input(loaded_service):
    """
    Test SECOM prediction with invalid input shape.
    """
    # Create invalid input with 23 features instead of 24
    invalid_input = np.random.rand(23).tolist()
    
    with pytest.raises(ValueError, match="Expected 24 features"):
        loaded_service.predict_secom(invalid_input)

def test_predict_wafer_valid_input(loaded_service):
    """
    Test Wafer Map prediction with a valid 2D array input using real model inference.
    """
    # Create a dummy 2D array simulating a wafer map (e.g., 30x30 with values 0, 1, 2)
    dummy_wafer = np.random.randint(0, 3, size=(30, 30)).tolist()
    
    result = loaded_service.predict_wafer(dummy_wafer)
    
    assert "model" in result
    assert result["model"] == "wafermap_cnn"
    assert "prediction" in result
    assert result["prediction"] in loaded_service.wafermap_class_labels
    assert "probability" in result
    
    # Check probabilities dict
    for label in loaded_service.wafermap_class_labels:
        assert label in result["probability"]
        
    # Probabilities should sum to approximately 1.0
    total_prob = sum(result["probability"].values())
    assert 0.99 < total_prob < 1.01

def test_predict_wafer_invalid_input(loaded_service):
    """
    Test Wafer Map prediction with an invalid input shape.
    """
    # Create invalid 1D array
    invalid_wafer = np.random.randint(0, 3, size=(30,)).tolist()
    
    with pytest.raises(ValueError, match="Expected 2D array"):
        loaded_service.predict_wafer(invalid_wafer)
