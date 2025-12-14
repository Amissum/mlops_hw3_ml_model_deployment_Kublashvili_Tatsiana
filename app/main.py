import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, start_http_server

from server.inference import ModelRunner
from server.validation import features_to_dict, ValidationError
from server import logger as _logger


MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

PREDICTIONS_TOTAL = Counter('predictions_total', 'Total predictions', ['model_version'])
PREDICTION_DURATION = Histogram('prediction_duration_seconds', 'Prediction duration', ['model_version'])
ERRORS_TOTAL = Counter('errors_total', 'Total errors', ['model_version', 'error_type'])

logger = _logger.service_logger


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

start_http_server(METRICS_PORT)
logger.info(f"HTTP service initialized. Model version: {runner.version}")
logger.info(f"Prometheus metrics are available on port: {METRICS_PORT}")


@api.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    logger.info("Starting HTTP health check...")
    try:
        return HealthResponse(status="SERVING", model_version=runner.version)
    except Exception as e:
        logger.error(f"Error in HTTP Health: {e}")
        raise HTTPException(status_code=500, detail=f"internal error: {e}")


@api.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    start_time = time.time()

    try:
        features = request.features
        logger.info(f"HTTP predict request received. Number of features: {len(features)}")

        if not features:
            ERRORS_TOTAL.labels(model_version=runner.version, error_type="empty_features").inc()
            raise HTTPException(status_code=400, detail="Features list cannot be empty")

        PREDICTIONS_TOTAL.labels(model_version=runner.version).inc()

        # Reuse existing validation: works with any objects having .name and .value
        feats = features_to_dict(features)
        pred, conf = runner.predict(feats)

        duration = time.time() - start_time
        PREDICTION_DURATION.labels(model_version=runner.version).observe(duration)

        return PredictResponse(
            prediction=pred,
            confidence=conf,
            model_version=runner.version,
        )
    except ValidationError as ve:
        ERRORS_TOTAL.labels(model_version=runner.version, error_type="validation").inc()
        logger.error(f"Validation Error in HTTP Predict: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        # already logged & counted where appropriate
        raise
    except Exception as e:
        ERRORS_TOTAL.labels(model_version=runner.version, error_type="internal").inc()
        logger.error(f"Error in HTTP Predict: {str(e)}")
        raise HTTPException(status_code=500, detail=f"internal error: {e}")
