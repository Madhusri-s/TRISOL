@echo off
REM EcoInnovators PV Detection Docker Run Script for Windows

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ecoinnovators/pv-detection:latest
set CONTAINER_NAME=eco-pv-pipeline
set HOST_PORT=8080

echo 🚀 Running EcoInnovators PV Detection Pipeline
echo ==============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Stop existing container if running
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if not errorlevel 1 (
    echo 🛑 Stopping existing container: %CONTAINER_NAME%
    docker stop %CONTAINER_NAME%
)

REM Remove existing container if exists
docker ps -aq -f name=%CONTAINER_NAME% >nul 2>&1
if not errorlevel 1 (
    echo 🗑️  Removing existing container: %CONTAINER_NAME%
    docker rm %CONTAINER_NAME%
)

REM Create directories for volumes
if not exist "data" mkdir data
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from .env.example
    copy .env.example .env >nul
    echo ❗ Please edit .env file with your API keys before running again.
    pause
    exit /b 1
)

REM Run the container
echo 🐳 Starting container: %CONTAINER_NAME%
docker run -d ^
    --name %CONTAINER_NAME% ^
    --env-file .env ^
    -p %HOST_PORT%:8080 ^
    -v "%cd%\data:/app/data" ^
    -v "%cd%\outputs:/app/outputs" ^
    -v "%cd%\logs:/app/logs" ^
    --restart unless-stopped ^
    %IMAGE_NAME%

if errorlevel 1 (
    echo ❌ Failed to start container
    pause
    exit /b 1
)

REM Wait for container to start
echo ⏳ Waiting for container to start...
timeout /t 5 /nobreak >nul

REM Check container status
docker ps -q -f name=%CONTAINER_NAME% >nul 2>&1
if not errorlevel 1 (
    echo ✅ Container started successfully!
    echo.
    echo Container Details:
    docker ps -f name=%CONTAINER_NAME%
    echo.
    echo Logs:
    echo   docker logs %CONTAINER_NAME%
    echo   docker logs -f %CONTAINER_NAME%  # Follow logs
    echo.
    echo Access:
    echo   Container: http://localhost:%HOST_PORT%
    echo   Shell: docker exec -it %CONTAINER_NAME% bash
) else (
    echo ❌ Container failed to start. Check logs:
    docker logs %CONTAINER_NAME%
    pause
    exit /b 1
)

pause