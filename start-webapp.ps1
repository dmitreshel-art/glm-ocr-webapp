# Start WebApp only (connects to existing llama-server)
# Use this after starting HIP or Docker llama-server

Write-Host "Starting WebApp..." -ForegroundColor Cyan

# Check if llama-server is running
$hipRunning = Get-Process -Name "llama-server" -ErrorAction SilentlyContinue
$dockerRunning = docker ps --filter "name=glm-ocr-llama" --format "{{.Names}}" 2>$null

if (-not $hipRunning -and -not $dockerRunning) {
    Write-Host "Warning: No llama-server detected!" -ForegroundColor Yellow
    Write-Host "Start one first:" -ForegroundColor Yellow
    Write-Host "  HIP GPU:  .\start-hip.ps1" -ForegroundColor Yellow
    Write-Host "  Docker:   .\start-cpu.ps1" -ForegroundColor Yellow
}

docker-compose up -d

Write-Host "WebApp started on http://localhost:8080" -ForegroundColor Green