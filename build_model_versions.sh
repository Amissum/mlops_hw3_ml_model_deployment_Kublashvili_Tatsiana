#!/bin/bash

set -e

echo "Building ML gRPC Service versions..."

# Version 1
echo "Building v1.0.0..."
docker build -t ml-hw3-grpc-service:v1.0.0 -f Dockerfile .

# Version 2
echo "Building v2.0.0..."
docker build -t ml-hw3-grpc-service:v2.0.0 -f Dockerfile .

echo "Both versions built successfully!"
docker images | grep ml-hw3-grpc-service