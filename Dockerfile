# Build llama.cpp from source
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y \
    curl wget git build-essential cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
RUN git clone --depth 1 https://github.com/ggml-org/llama.cpp.git \
    && cd llama.cpp \
    && cmake -B build -DGGML_CUDA=OFF \
    && cmake --build build --config Release -j$(nproc)

# Download model
RUN mkdir -p /models \
    && wget -q -O /models/glm-ocr-q8_0.gguf \
    "https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/GLM-OCR-Q8_0.gguf" \
    && wget -q -O /models/mmproj.gguf \
    "https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/mmproj-GLM-OCR-Q8_0.gguf"

# Runtime - use same base to preserve shared libraries
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy llama-server and its libraries from builder
COPY --from=builder /build/llama.cpp/build/bin/llama-server /usr/local/bin/
COPY --from=builder /build/llama.cpp/build/bin/libmtmd.so.0 /usr/local/lib/
COPY --from=builder /models /models

# Update library path
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY static/ ./static/

ENV MODEL_PATH=/models/glm-ocr-q8_0.gguf
ENV MMPROJ_PATH=/models/mmproj.gguf
ENV LLAMA_SERVER_PORT=8765

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "backend.server"]