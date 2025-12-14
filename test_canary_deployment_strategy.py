# test_canary.py
import grpc
import sys
sys.path.insert(0, '.')

import model_pb2, model_pb2_grpc
from collections import Counter

def test_canary_distribution(num_requests=100):
    """Тестирует распределение трафика между версиями"""
    channel = grpc.insecure_channel('localhost:50051')
    stub = model_pb2_grpc.PredictionServiceStub(channel)
    
    versions = []
    
    print(f"Sending {num_requests} requests...")
    for i in range(num_requests):
        request = model_pb2.PredictRequest(
            features=[
                model_pb2.Feature(name="sepal_length", value=5.1),
                model_pb2.Feature(name="sepal_width",  value=3.5),
                model_pb2.Feature(name="petal_length", value=1.4),
                model_pb2.Feature(name="petal_width",  value=0.2),
            ]
        )
        response = stub.Predict(request)
        versions.append(response.model_version)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_requests}")
    
    channel.close()
    
    counter = Counter(versions)
    print("\n=== Traffic Distribution ===")
    for version, count in counter.items():
        percentage = (count / num_requests) * 100
        print(f"{version}: {count} requests ({percentage:.1f}%)")
    
    return counter

if __name__ == '__main__':
    test_canary_distribution(100)