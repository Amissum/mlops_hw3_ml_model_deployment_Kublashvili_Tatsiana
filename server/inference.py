import joblib
import pandas as pd
from pathlib import Path

class ModelRunner:
    def __init__(self, model_path: str, version: str = "v1.0.0"):
        self.model = joblib.load(model_path)
        self.version = version

    def predict(self, features: dict[str, float]) -> tuple[str, float]:
        df = pd.DataFrame([features])
        y = self.model.predict(df)[0]
        try:
            proba = float(max(self.model.predict_proba(df)[0]))
        except Exception:
            proba = 1.0
        return str(y), proba