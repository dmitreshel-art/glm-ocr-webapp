# GLM-OCR PowerShell Script
# Usage: .\update.ps1 [command]

param(
    [string]$Command = "all"
)

function Update-Git {
    Write-Host "📥 Pulling latest changes..." -ForegroundColor Cyan
    git pull
}

function Build-Docker {
    Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
    docker-compose build
}

function Start-Containers {
    Write-Host "🚀 Starting containers..." -ForegroundColor Cyan
    docker-compose up -d
    Write-Host "✅ Done! Open http://localhost:8080" -ForegroundColor Green
}

function Stop-Containers {
    Write-Host "🛑 Stopping containers..." -ForegroundColor Yellow
    docker-compose down
}

function Show-Logs {
    docker-compose logs -f
}

function Show-Status {
    Write-Host "📊 Container status:" -ForegroundColor Cyan
    docker-compose ps
}

function Clean-All {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    docker-compose down -v --rmi local
    Write-Host "✅ Clean complete" -ForegroundColor Green
}

function Show-Help {
    Write-Host @"
GLM-OCR PowerShell Script

Usage: .\update.ps1 [command]

Commands:
  update    - Pull latest changes from GitHub
  build     - Build Docker images
  up        - Start containers
  down      - Stop containers
  logs      - Show container logs
  status    - Show container status
  clean     - Remove containers, images, volumes
  all       - Update, build, and start (default)

Examples:
  .\update.ps1          # Full update cycle
  .\update.ps1 build    # Build only
  .\update.ps1 logs     # View logs
"@
}

# Main
switch ($Command) {
    "update" { Update-Git }
    "build" { Build-Docker }
    "up" { Start-Containers }
    "down" { Stop-Containers }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "clean" { Clean-All }
    "help" { Show-Help }
    "all" {
        Update-Git
        Build-Docker
        Start-Containers
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help
    }
}