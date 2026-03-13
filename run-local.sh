#!/bin/bash
# Build and run GLM-OCR WebApp locally (without Docker)

set -e

echo "🔨 Building GLM-OCR WebApp..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "📦 Starting llama-server with GLM-OCR..."
echo "Model will download from HuggingFace (~1GB)"

# Start llama-server in background (auto-downloads model)
llama-server -hf ggml-org/GLM-OCR-GGUF:Q8_0 \
    --port 8765 \
    --host 127.0.0.1 \
    --ctx-size 4096 \
    --n-gpu-layers 0 \
    &

# Wait for llama-server to be ready
echo "⏳ Waiting for model to load..."
sleep 10

for i in {1..30}; do
    if curl -s http://127.0.0.1:8765/health > /dev/null 2>&1; then
        echo "✅ llama-server is ready"
        break
    fi
    sleep 1
done

echo "🌐 Starting web server..."
python -m backend.server