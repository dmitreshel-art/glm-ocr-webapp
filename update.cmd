@echo off
REM GLM-OCR Update Script
REM 
REM Modes:
REM   1. HIP GPU (recommended): Run start-hip.ps1 first, then this script
REM   2. Docker CPU: This script starts both llama-server and webapp

if "%1"=="" goto all
if "%1"=="update" goto update
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
if "%1"=="cpu" goto cpu
goto unknown

:all
echo 📥 Pulling latest changes...
git pull
echo 🔨 Building Docker images...
docker-compose build
echo.
echo ℹ️  This starts WebApp only (connects to HIP on port 8765)
echo    For Docker CPU mode, run: update.cmd cpu
echo.
echo 🚀 Starting WebApp...
docker-compose up -d
echo ✅ Done! Open http://localhost:8080
echo 💡 If using HIP, make sure llama-server.exe is running on port 8765
goto end

:cpu
echo 📥 Pulling latest changes...
git pull
echo 🔨 Building Docker images...
docker-compose --profile cpu build
echo.
echo 🚀 Starting llama-server (CPU) and WebApp...
docker-compose --profile cpu up -d
echo ✅ Done! Open http://localhost:8080
echo ⚠️  CPU mode is slower than HIP GPU
goto end

:update
echo 📥 Pulling latest changes...
git pull
goto end

:build
echo 🔨 Building Docker images...
docker-compose build
goto end

:up
echo 🚀 Starting WebApp...
docker-compose up -d
echo ✅ Done! Open http://localhost:8080
goto end

:down
echo 🛑 Stopping containers...
docker-compose down
goto end

:logs
docker-compose logs -f
goto end

:status
echo 📊 Container status:
docker-compose ps
goto end

:clean
echo 🧹 Cleaning up...
docker-compose down -v --rmi local
echo ✅ Clean complete
goto end

:unknown
echo Unknown command: %1
echo Usage: update.cmd [update^|build^|up^|down^|logs^|status^|clean^|cpu]
echo.
echo Modes:
echo   (default) - WebApp only (connects to HIP on port 8765)
echo   cpu       - Docker CPU mode (slower, no HIP needed)