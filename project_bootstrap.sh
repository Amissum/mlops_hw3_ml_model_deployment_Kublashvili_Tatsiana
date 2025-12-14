#!/bin/bash
# Quick project installation

set -e

echo "================================================"
echo "  Installing ml_grpc_service"
echo "================================================"
echo ""

# 1. Install dependencies
echo "📦 Step 1/5: Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# 2. Generate proto files
echo "🔧 Step 2/4: Generating proto files..."

# Create __init__.py in protos before generation
touch protos/__init__.py

# Generate gRPC stubs (model + health). We don't pipe through grep so that
# set -e doesn't stop the script when there is no output.
python -m grpc_tools.protoc \
    --proto_path=./protos \
    --python_out=. \
    --grpc_python_out=. \
    model.proto \
    health.proto

echo "✅ Proto files generated"
echo ""

# 3. Create model
echo "🤖 Step 3/5: Creating ML model..."
python train_model.py
echo "✅ Model trained"
echo ""

# 4. Create model v2
echo "🤖 Step 4/5: Creating ML model v2..."
python train_model_v2.py
echo "✅ Model v2 trained"
echo ""

# 5. Create __init__.py files
echo "📝 Step 5/5: Creating __init__.py files..."
touch server/__init__.py
touch client/__init__.py
echo "✅ Files created"
echo ""

echo "================================================"
echo "  ✅ Installation complete!"
echo "================================================"
echo ""
echo "To start the server:"
echo "  python -m server.server"
echo ""
echo "For testing (in another terminal):"
echo "  python -m client.client"
echo ""