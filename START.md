# GLM-OCR WebApp - Startup Scripts for Windows

## Option 1: HIP GPU Acceleration (Recommended)

Run HIP llama-server on Windows with GPU acceleration:

```powershell
# Start HIP llama-server (GPU)
.\start-hip.ps1
```

This starts llama-server.exe on port 8765 using your AMD Radeon GPU.

## Option 2: Docker CPU Mode

Run llama-server in Docker container (CPU-only):

```powershell
# Start Docker llama-server (CPU)
docker-compose --profile cpu up -d
```

## WebApp

The WebApp automatically connects to the available llama-server:
- Priority: LLAMA_SERVER_URL env var
- Fallback: http://host.docker.internal:8765 (HIP on Windows)
- Alternative: http://llama-server:8080 (Docker container)

## Ports

- 8080: WebApp (always)
- 8765: llama-server (HIP or Docker, not both)