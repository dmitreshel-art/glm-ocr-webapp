# GLM-OCR WebApp - Startup Scripts for Windows

## Quick Start

### Option 1: HIP GPU Acceleration (Recommended - ~10x faster)

```powershell
# Start HIP llama-server (GPU ~2-5 sec/page)
.\start-hip.ps1

# In another terminal, start WebApp
.\update.cmd
```

### Option 2: CPU on Windows Host (Slower, no Docker)

```powershell
# Start llama-server on Windows (CPU-only, ~50 sec/page)
.\start-cpu-local.ps1

# In another terminal, start WebApp
.\update.cmd
```

### Option 3: Docker CPU Mode (Slowest, simplest)

```powershell
# Start both in Docker (CPU-only)
.\update.cmd cpu
```

---

## Startup Scripts

| Script | Mode | Speed | Location |
|--------|------|-------|----------|
| `start-hip.ps1` | GPU | ~2-5 sec/page | Windows host |
| `start-cpu-local.ps1` | CPU | ~50 sec/page | Windows host |
| `update.cmd cpu` | CPU | ~50 sec/page | Docker |

---

## update.cmd Commands

| Command | Description |
|---------|-------------|
| `update.cmd` | Start WebApp (HIP/CPU host mode) |
| `update.cmd cpu` | Start both in Docker (CPU mode) |
| `update.cmd down` | Stop WebApp |
| `update.cmd logs` | View logs |
| `update.cmd status` | Container status |

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

Option 2 (CPU on Windows):
┌─────────────────────────────────────────────┐
│  Windows Host                                │
│  ├── llama-server.exe :8765 (CPU)           │
│  └── Docker Desktop                          │
│      └── WebApp :8080                         │
│          → http://host.docker.internal:8765  │
└─────────────────────────────────────────────┘

Option 3 (Docker CPU):
┌─────────────────────────────────────────────┐
│  Docker Desktop                              │
│  ├── llama-server :8765 (CPU)               │
│  └── WebApp :8080                            │
│      → http://llama-server:8080              │
└─────────────────────────────────────────────┘
```

---

## Ports

- 8080: WebApp (always)
- 8765: llama-server (HIP, CPU local, or Docker - choose one)