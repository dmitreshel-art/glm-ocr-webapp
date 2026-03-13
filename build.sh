#!/bin/bash
# Build script for GLM-OCR WebApp

set -e

echo "🔨 Building GLM-OCR WebApp..."

# Create build context with all files
mkdir -p build/context
cp Dockerfile build/context/
cp docker-compose.yml build/context/
cp requirements.txt build/context/
cp -r backend build/context/
cp -r static build/context/

# Build image
echo "📦 Building Docker image..."
docker build -t glm-ocr-webapp:latest build/context

# Cleanup
rm -rf build/context

echo "✅ Build complete!"
echo ""
echo "To run: docker-compose up -d"
echo "Then open: http://localhost:8080"