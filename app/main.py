import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from server.inference import ModelRunner
from server.validation import features_to_dict, ValidationError


MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")


class Feature(BaseModel):
    name: str
    value: float


class PredictRequest(BaseModel):
    features: List[Feature]


class HealthResponse(BaseModel):
    status: str
    model_version: str


class PredictResponse(BaseModel):
    prediction: str
    confidence: float
    model_version: str


api = FastAPI(title="ML Service", version=MODEL_VERSION)
runner = ModelRunner(MODEL_PATH, version=MODEL_VERSION)


@api.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_version=runner.version)


@api.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    sleep_ms = int(os.getenv("SLEEP_MS", "0"))
    if sleep_ms > 0:
        time.sleep(sleep_ms / 1000.0)

    try:
        # Reuse existing validation: works with any objects having .name and .value
        feats = features_to_dict(request.features)
        pred, conf = runner.predict(feats)
        return PredictResponse(
            prediction=pred,
            confidence=conf,
            model_version=runner.version,
        )
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"internal error: {e}")
