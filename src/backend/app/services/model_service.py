import os
import sys
import types
import datetime
import numpy as np
import joblib
import cv2
import torch
import torch.nn as nn
from typing import List, Dict, Union, Any

# ==========================================
# 1. Compatibility Shim for SECOM Classifier
# ==========================================
# The SECOM classifier was trained with sklearn 1.6.1 and references a Cython
# loss class that no longer exists in newer versions. This stub allows the
# model to deserialize correctly.
class _CyHalfBinomialLoss:
    def __setstate__(self, s):
        if isinstance(s, dict):
            self.__dict__.update(s)

_stub = types.ModuleType('_loss')
_stub.CyHalfBinomialLoss = _CyHalfBinomialLoss
sys.modules.setdefault('_loss', _stub)


# ==========================================
# 2. PyTorch Architecture for Wafer Map CNN
# ==========================================
class WaferMapCNN(nn.Module):
    def __init__(self, num_classes=9):
        super(WaferMapCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ==========================================
# 3. Model Service Class
# ==========================================
class ModelService:
    def __init__(self):
        self.secom_model = None
        self.wafermap_model = None
        
        self.secom_class_names = {0: 'PASS', 1: 'FAIL'}
        self.wafermap_class_labels = [
            'Center', 'Donut', 'Edge-Loc', 'Edge-Ring',
            'Loc', 'Random', 'Scratch', 'Near-full', 'none'
        ]

    def load_models(self, secom_path: str, wafermap_path: str):
        """
        Loads both models into memory. If a model fails to load, raises a clear error.
        """
        # Load SECOM model
        if not os.path.exists(secom_path):
            raise FileNotFoundError(f"SECOM model file not found at {secom_path}")
        try:
            self.secom_model = joblib.load(secom_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load SECOM model from {secom_path}. Error: {str(e)}")

        # Load Wafer Map model
        if not os.path.exists(wafermap_path):
            raise FileNotFoundError(f"Wafer Map model file not found at {wafermap_path}")
        try:
            self.wafermap_model = WaferMapCNN(num_classes=9)
            self.wafermap_model.load_state_dict(
                torch.load(wafermap_path, map_location='cpu', weights_only=True)
            )
            self.wafermap_model.eval()
        except Exception as e:
            raise RuntimeError(f"Failed to load Wafer Map model from {wafermap_path}. Error: {str(e)}")

    def predict_secom(self, process_data: Union[List[float], np.ndarray]) -> Dict[str, Any]:
        """
        Predicts whether a wafer will PASS or FAIL based on 24 pre-processed features.
        """
        if self.secom_model is None:
            raise RuntimeError("SECOM model is not loaded. Call load_models() first.")
            
        features = np.array(process_data, dtype=np.float64)
        
        if features.ndim == 1:
            features = features.reshape(1, -1)
            
        if features.shape[1] != 24:
            raise ValueError(f"Expected 24 features for SECOM model, but got {features.shape[1]}")
            
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        try:
            pred = self.secom_model.predict(features)
            predicted_label = self.secom_class_names.get(int(pred[0]), "UNKNOWN")
            
            result = {
                "model": "secom_classifier",
                "prediction": predicted_label,
                "classes": list(self.secom_class_names.values()),
                "timestamp": timestamp
            }
            
            if hasattr(self.secom_model, "predict_proba"):
                proba = self.secom_model.predict_proba(features)
                result["probability"] = {
                    "PASS": float(proba[0, 0]),
                    "FAIL": float(proba[0, 1])
                }
            else:
                result["probability"] = None
                result["probability_note"] = "Probability unavailable for this model type."
                
            return result
            
        except Exception as e:
            raise RuntimeError(f"Prediction failed during SECOM inference: {str(e)}")

    def predict_wafer(self, input_data: Union[List[List[int]], np.ndarray]) -> Dict[str, Any]:
        """
        Predicts defect pattern from a 2D wafer map (values 0, 1, 2).
        """
        if self.wafermap_model is None:
            raise RuntimeError("Wafer Map model is not loaded. Call load_models() first.")
            
        wafer_2d = np.array(input_data, dtype=np.float32)
        if wafer_2d.ndim != 2:
            raise ValueError(f"Expected 2D array for Wafer Map, but got {wafer_2d.ndim}D array.")
            
        # Preprocessing: resize to 64x64 with INTER_NEAREST, scale by / 2.0
        resized = cv2.resize(
            wafer_2d,
            (64, 64),
            interpolation=cv2.INTER_NEAREST
        )
        
        tensor = torch.tensor(resized / 2.0, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        try:
            with torch.no_grad():
                logits = self.wafermap_model(tensor)
            
            probs = torch.softmax(logits, dim=1).squeeze(0)
            idx = int(probs.argmax())
            
            prob_dict = {
                label: round(float(probs[i]), 6)
                for i, label in enumerate(self.wafermap_class_labels)
            }
            
            return {
                "model": "wafermap_cnn",
                "prediction": self.wafermap_class_labels[idx],
                "probability": prob_dict,
                "classes": self.wafermap_class_labels,
                "timestamp": timestamp
            }
            
        except Exception as e:
            raise RuntimeError(f"Prediction failed during Wafer Map inference: {str(e)}")

# Create a singleton instance
model_service = ModelService()
