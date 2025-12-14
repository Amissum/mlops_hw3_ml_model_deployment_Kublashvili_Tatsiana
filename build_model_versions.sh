#!/bin/bash

set -e

echo "Building ML gRPC Service versions..."

# Version 1
echo "Building v1.0.0..."
docker build -t ml-hw3-grpc-service:v1.0.0 \
  --build-arg MODEL_FILE=model.pkl \
  -f Dockerfile .

# Version 2
echo "Building v2.0.0..."
docker build -t ml-hw3-grpc-service:v2.0.0 \
  --build-arg MODEL_FILE=model_v2.pkl \
  -f Dockerfile .

echo "Both versions built successfully!"
docker images | grep ml-hw3-grpc-service