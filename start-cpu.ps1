# Start llama-server in Docker (CPU-only)
# Use this when HIP/GPU is not available

Write-Host "Starting Docker llama-server (CPU)..." -ForegroundColor Yellow

# Stop HIP if running
Get-Process -Name "llama-server" -ErrorAction SilentlyContinue | Stop-Process -Force

# Run with CPU profile
docker-compose --profile cpu up -d

Write-Host "llama-server started on port 8765 (CPU mode)" -ForegroundColor Yellow
Write-Host "Note: This is slower than HIP GPU acceleration"