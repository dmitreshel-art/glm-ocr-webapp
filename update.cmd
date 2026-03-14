@echo off
REM GLM-OCR Update Script

if "%1"=="" goto all
if "%1"=="update" goto update
if "%1"=="build" goto build
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="logs" goto logs
if "%1"=="status" goto status
if "%1"=="clean" goto clean
goto unknown

:all
echo 📥 Pulling latest changes...
git pull
echo 🔨 Building Docker images...
docker-compose build
echo 🚀 Starting containers...
docker-compose up -d
echo ✅ Done! Open http://localhost:8080
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
echo 🚀 Starting containers...
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
echo Usage: update.cmd [update^|build^|up^|down^|logs^|status^|clean]

:end