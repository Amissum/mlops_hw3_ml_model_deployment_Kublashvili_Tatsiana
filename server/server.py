from xml.parsers.expat import model
import grpc
import os
from concurrent import futures
from grpc_reflection.v1alpha import reflection
import model_pb2, model_pb2_grpc, health_pb2, health_pb2_grpc, grpc_health.v1.health as health
from validation import features_to_dict, ValidationError
from inference import ModelRunner
import logger as _logger
from prometheus_client import Counter, Histogram, start_http_server
import time


MODEL_PATH = os.getenv("MODEL_PATH", "models/model.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
PORT = int(os.getenv("PORT", "50051"))
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

PREDICTIONS_TOTAL = Counter('predictions_total', 'Total predictions', ['model_version'])
PREDICTION_DURATION = Histogram('prediction_duration_seconds', 'Prediction duration', ['model_version'])
ERRORS_TOTAL = Counter('errors_total', 'Total errors', ['model_version', 'error_type'])

logger = _logger.service_logger

class PredictionService(model_pb2_grpc.PredictionServiceServicer):
    def __init__(self):
        self.runner = ModelRunner(MODEL_PATH, version=MODEL_VERSION)
        logger.info(f"Service initialized. Model version: {self.runner.version}")
        metrics_port = int(os.getenv('METRICS_PORT', '8000'))
        start_http_server(metrics_port)
        logger.info(f"Prometheus metrics are available on port: {METRICS_PORT}")

    def Health(self, request, context):
        try:
            logger.info("Starting health check...")
            return model_pb2.HealthResponse(status="ok", model_version=self.runner.version)
        except Exception as e:
            logger.error(f"Error in Health: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return model_pb2.HealthResponse()

    def Predict(self, request, context):
        start_time = time.time()

        try:
            feats = features_to_dict(request.features)

            features = list(request.features)
            logger.info(f"Predict request received. Number of features: {len(features)}")
            PREDICTIONS_TOTAL.labels(model_version=self.runner.version).inc()
            
            if not features:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Features list cannot be empty")
                return model_pb2.PredictResponse()

            pred, conf = self.runner.predict(feats)

            PREDICTION_DURATION.labels(model_version=self.runner.version).observe(time.time() - start_time)

            return model_pb2.PredictResponse(
                prediction=pred, confidence=conf, model_version=self.runner.version
            )        

        except ValidationError as ve:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(ve))
            logger.error(f"Validation Error in Predict: {str(ve)}")
            return model_pb2.PredictResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"internal error: {e}")
            logger.error(f"Error in Predict: {str(e)}")
            return model_pb2.PredictResponse()

def serve():
    options = [
        ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
    ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS), options=options)
    model_pb2_grpc.add_PredictionServiceServicer_to_server(PredictionService(), server)
    SERVICE_NAMES = (
        model_pb2.DESCRIPTOR.services_by_name['PredictionService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port(f"[::]:{PORT}")

    health_servicer = health.HealthServicer()
    health_servicer.set('', health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set('mlservice.v1.PredictionService',
                        health_pb2.HealthCheckResponse.SERVING)

    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    server.start()
    logger.info(f"gRPC server started on :{PORT}, model={MODEL_PATH}, version={MODEL_VERSION}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
        server.stop(0)

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass
    serve()
