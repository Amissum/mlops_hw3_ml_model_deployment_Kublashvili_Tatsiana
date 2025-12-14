FROM python:3.11-slim

# Non-interactive mode for apt
ENV DEBIAN_FRONTEND=noninteractive

# Working directory inside container
WORKDIR /app

# Install system dependencies (if needed for numpy/sklearn etc.)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# First copy only dependencies to cache pip install layer
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Now copy the entire application
COPY . .

# Generate gRPC code infrastructure from .proto files
RUN python -m grpc_tools.protoc \
    --proto_path=./protos \
    --python_out=. \
    --grpc_python_out=. \
    model.proto \
    health.proto

# gRPC server port
EXPOSE 50051

# By default start the server
CMD ["python", "-m", "server.server"]