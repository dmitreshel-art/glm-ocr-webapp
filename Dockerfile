FROM ghcr.io/ggml-org/llama.cpp:server AS llamacpp

FROM python:3.11-slim

# Copy llama-server from official image (binary is in PATH)
COPY --from=llamacpp /usr/local/bin/llama-server /usr/local/bin/llama-server

# Python backend
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY static/ ./static/

# Model will be auto-downloaded on first run
ENV HF_REPO=ggml-org/GLM-OCR-GGUF:Q8_0

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "backend.server"]