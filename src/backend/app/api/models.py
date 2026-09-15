from fastapi import APIRouter

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("")
def list_models():
    """Returns metadata about the currently loaded machine learning models."""
    return [
        {
            "name": "secom_classifier_model.pkl",
            "type": "VotingClassifier (Sklearn)",
            "purpose": "Process risk classification. Predicts PASS/FAIL based on 24 process sensor features.",
            "supported_methods": ["predict", "predict_proba"],
            "expected_input": "24-element numeric array",
            "classes": ["PASS", "FAIL"],
            "probability_support": True,
            "preprocessing": "StandardScaler + Feature Selection applied internally if pipeline."
        },
        {
            "name": "wafermap_dl_model.pth",
            "type": "PyTorch CNN (Custom)",
            "purpose": "Wafer map defect pattern recognition. Classifies 2D maps into 9 defect categories.",
            "supported_methods": ["forward"],
            "expected_input": "2D array (values 0,1,2)",
            "classes": ['Center', 'Donut', 'Edge-Loc', 'Edge-Ring', 'Loc', 'Random', 'Scratch', 'Near-full', 'none'],
            "probability_support": True,
            "preprocessing": "Resized to 64x64, INTER_NEAREST, scaled by 1/2.0."
        }
    ]
