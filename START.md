# GLM-OCR WebApp - Startup Scripts for Windows

## Quick Start

### Option 1: HIP GPU Acceleration (Recommended - ~10x faster)

```powershell
# Start HIP llama-server (GPU)
.\start-hip.ps1

# In another terminal, start WebApp
.\update.cmd
```

### Option 2: Docker CPU Mode (Slower but simpler)

```powershell
# Start both in Docker (CPU-only)
.\update.cmd cpu
```

---

## Detailed Commands

### HIP GPU Mode (Radeon 890M)

```powershell
# Start HIP llama-server (port 8765, GPU)
.\start-hip.ps1

# Start WebApp (port 8080, connects to HIP)
.\update.cmd
```

### Docker CPU Mode

```powershell
# Start both llama-server and WebApp in Docker
.\update.cmd cpu
```

### Stopping

```powershell
# Stop all instances
.\stop.ps1
```

---

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

---

## update.cmd Commands

| Command | Description |
|---------|-------------|
| `update.cmd` | Start WebApp (HIP mode) |
| `update.cmd cpu` | Start both in Docker (CPU mode) |
| `update.cmd down` | Stop WebApp |
| `update.cmd logs` | View logs |
| `update.cmd status` | Container status |

---

## Ports

- 8080: WebApp (always)
- 8765: llama-server (HIP or Docker, not both)