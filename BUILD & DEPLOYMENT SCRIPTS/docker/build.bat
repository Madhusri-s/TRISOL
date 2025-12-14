@echo off
REM EcoInnovators PV Detection Docker Build Script for Windows

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ecoinnovators/pv-detection
set VERSION=latest
set DOCKERFILE_PATH=.

echo 🚀 Building EcoInnovators PV Detection Docker Image
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Build the image
echo 📦 Building Docker image: %IMAGE_NAME%:%VERSION%
docker build -t %IMAGE_NAME%:%VERSION% %DOCKERFILE_PATH%
if errorlevel 1 (
    echo ❌ Docker build failed!
    pause
    exit /b 1
)

REM Tag with additional versions
echo 🏷️  Tagging image with version tags
for /f "tokens=2 delims==" %%i in ('wmic OS Get localdatetime /value') do set "dt=%%i"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "datestamp=%YYYY%%MM%%DD%"

docker tag %IMAGE_NAME%:%VERSION% %IMAGE_NAME%:v1.0
docker tag %IMAGE_NAME%:%VERSION% %IMAGE_NAME%:%datestamp%

REM Show image info
echo ✅ Build completed successfully!
echo.
echo Image Details:
docker images %IMAGE_NAME%

echo.
echo 🎉 Docker image built successfully!
echo.
echo Next steps:
echo 1. Test the image: docker run --rm %IMAGE_NAME%:%VERSION%
echo 2. Push to DockerHub: docker push %IMAGE_NAME%:%VERSION%
echo 3. Run with docker-compose: docker-compose up

pause