# GLM-OCR WebApp - Startup Scripts for Windows

## Option 1: HIP GPU Acceleration (Recommended - ~10x faster)

```powershell
# Start HIP llama-server on Windows (GPU)
.\start-hip.ps1

# In another terminal, start WebApp
docker-compose up -d
```

## Option 2: Docker CPU Mode (Slower but simpler)

```powershell
# Start both llama-server and WebApp in Docker
.\start-cpu.ps1
```

## Architecture

```
Option 1 (HIP GPU):
┌─────────────────────────────────────────────┐
│  Windows Host                                │
│  ├── HIP llama-server.exe :8765 (GPU)       │
│  └── Docker Desktop                          │
│      └── WebApp :8080                         │
│          → http://host.docker.internal:8765  │
└─────────────────────────────────────────────┘

Option 2 (Docker CPU):
┌─────────────────────────────────────────────┐
│  Docker Desktop                              │
│  ├── llama-server :8765 (CPU)               │
│  └── WebApp :8080                            │
│      → http://llama-server:8080              │
└─────────────────────────────────────────────┘
```

## Stopping

```powershell
# Stop all instances
.\stop.ps1
```

## Ports

- 8080: WebApp (always)
- 8765: llama-server (HIP or Docker, not both)