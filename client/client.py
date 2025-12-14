import os
from pyexpat import features
import sys
import grpc
import logger as _logger
import time
import model_pb2, model_pb2_grpc

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from protos import model_pb2, model_pb2_grpc

logger = _logger.service_logger

def create_channel_with_retry(server_address, max_retries=15, retry_delay=2):
    """Create gRPC channel with retry logic to handle server startup time."""
    logger.info(f"Attempting to connect to {server_address}")
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connection attempt {attempt}/{max_retries}...")
            channel = grpc.insecure_channel(server_address)
            
            # Wait for channel to be ready (with timeout)
            grpc.channel_ready_future(channel).result(timeout=5)
            
            logger.info(f"✓ Successfully connected to {server_address}")
            return channel
            
        except grpc.FutureTimeoutError:
            logger.warning(f"Connection timeout on attempt {attempt}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect after {max_retries} attempts")
                raise Exception(f"Could not connect to gRPC server at {server_address}")
                
        except Exception as e:
            logger.warning(f"Connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect after {max_retries} attempts")
                raise


def run_health_check(stub):
    """Service health check"""
    try:
        logger.info("Sending Health request...")
        request = model_pb2.HealthRequest()
        response = stub.Health(request)
        
        print("\n=== Health Check ===")
        print(f"Status: {response.status}")
        print(f"Model Version: {response.model_version}")
        print("=" * 40)
        
        return response
    except grpc.RpcError as e:
        logger.error(f"Health check failed: {e.code()} - {e.details()}")
        raise


def run_prediction(stub, features: list):
    """Get prediction"""
    try:
        # Expected features input:
        # [
        #     {"name": "sepal_length", "value": 10.1},
        #     {"name": "sepal_width",  "value": 3.5},
        #     {"name": "petal_length", "value": 4.4},
        #     {"name": "petal_width",  "value": 1.2}
        # ]
        features_names = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
        features_dicts = []
        for name, value in zip(features_names, features):
            feature_dict = model_pb2.Feature(name=name, value=value)
            features_dicts.append(feature_dict)
        
        logger.info(f"Sending Predict request with features: {features}")
        request = model_pb2.PredictRequest(features=features_dicts)
        response = stub.Predict(request)
        
        print("\n=== Prediction ===")
        print(f"Prediction: {response.prediction}")
        print(f"Confidence: {response.confidence:.4f}")
        print(f"Model Version: {response.model_version}")
        print("=" * 40)
        
        return response
    except grpc.RpcError as e:
        logger.error(f"Prediction failed: {e.code()} - {e.details()}")
        raise


def main():
    """Main client function"""
    server_address = os.getenv('GRPC_SERVER', 'localhost:50051')
    
    logger.info(f"Starting gRPC client for server: {server_address}")
    
    # Create channel with retry logic
    try:
        channel = create_channel_with_retry(server_address)
    except Exception as e:
        logger.error(f"Could not establish connection: {e}")
        sys.exit(1)
    
    try:
        stub = model_pb2_grpc.PredictionServiceStub(channel)
        
        # Health check
        try:
            run_health_check(stub)
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return
        
        # Example predictions
        test_cases = [
            [5.1, 3.5, 1.4, 0.2],  # Example 1
            [6.7, 3.0, 5.2, 2.3],  # Example 2
            [1.0, 2.0, 3.0, 4.0],  # Example 3
        ]
        
        for i, features in enumerate(test_cases, 1):
            print(f"\nTest {i}:")
            try:
                run_prediction(stub, features)
            except Exception as e:
                logger.error(f"Prediction error: {e}")
        
        # Interactive mode
        print("\n" + "=" * 40)
        print("Would you like to make a custom prediction? (y/n)")
        choice = input().strip().lower()
        
        if choice == 'y' or choice == 'yes' or choice == 'Y' or choice == 'YES' or choice == '':
            print("Enter features separated by commas (e.g.: 1.0,2.0,3.0,4.0) representing 'sepal_length, sepal_width, petal_length, petal_width' parameters:")
            try:
                features_input = input().strip()
                features = [float(x.strip()) for x in features_input.split(',')]
                run_prediction(stub, features)
            except ValueError:
                logger.error("Invalid input format")
            except Exception as e:
                logger.error(f"Error: {e}")
    
    finally:
        # Close channel
        channel.close()
        logger.info("Connection closed")


if __name__ == '__main__':
    main()