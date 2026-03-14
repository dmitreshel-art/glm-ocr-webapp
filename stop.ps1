# Stop all llama-server instances

Write-Host "Stopping HIP llama-server..." -ForegroundColor Yellow
Get-Process -Name "llama-server" -ErrorAction SilentlyContinue | Stop-Process -Force

Write-Host "Stopping Docker containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "All stopped." -ForegroundColor Green