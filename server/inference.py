import joblib
import pandas as pd
from pathlib import Path
import os
import server.logger as _logger

logger = _logger.service_logger

class ModelRunner:
    def __init__(self, model_path: str, version: str = "v1.0.0"):
        self.model = None
        self.version = version
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info(f"Model successfully loaded from {model_path}")
            else:
                logger.warning(f"Model not found at {model_path}. Using fallback.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

    def predict(self, features: dict[str, float]) -> tuple[str, float]:
        try:
            df = pd.DataFrame([features])
            y = self.model.predict(df)[0]

            if hasattr(self.model, 'predict_proba'):
                proba = float(max(self.model.predict_proba(df)[0]))
            else:
                proba = 0.95
            logger.info(f"Prediction: {y}, Confidence: {proba:.4f}")
        except Exception:
            proba = 1.0
            y = "fallback_prediction"
            logger.info(f"Using fallback. Prediction: {y}, Confidence: {proba:.4f}")

        return str(y), proba