# Build llama.cpp from source (reliable, works everywhere)
# Alternative: Dockerfile.build for faster build using pre-built binary

FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Build llama.cpp from source
WORKDIR /build
RUN git clone --depth 1 https://github.com/ggml-org/llama.cpp.git \
    && cd llama.cpp \
    && cmake -B build -DGGML_CUDA=OFF \
    && cmake --build build --config Release -j$(nproc) \
    && cp build/bin/llama-server /usr/local/bin/

# Runtime image
FROM python:3.11-slim

# Copy llama-server from builder
COPY --from=builder /usr/local/bin/llama-server /usr/local/bin/llama-server

# Python backend
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY static/ ./static/

ENV HF_REPO=ggml-org/GLM-OCR-GGUF:Q8_0

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "backend.server"]