@echo off
REM EcoInnovators PV Detection Docker Push Script for Windows

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=ecoinnovators/pv-detection
set DOCKERHUB_USERNAME=ecoinnovators

echo 🚀 Pushing EcoInnovators PV Detection to DockerHub
echo =====================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if user is logged in to DockerHub
docker info | findstr "Username" >nul
if errorlevel 1 (
    echo 🔐 Please login to DockerHub first:
    echo docker login
    pause
    exit /b 1
)

REM Check if image exists
docker images %IMAGE_NAME% | findstr %IMAGE_NAME% >nul
if errorlevel 1 (
    echo ❌ Image %IMAGE_NAME% not found. Please build it first:
    echo docker\build.bat
    pause
    exit /b 1
)

REM Get date stamp
for /f "tokens=2 delims==" %%i in ('wmic OS Get localdatetime /value') do set "dt=%%i"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "datestamp=%YYYY%%MM%%DD%"

REM Push all tags
echo 📤 Pushing images to DockerHub...

echo Pushing %IMAGE_NAME%:latest
docker push %IMAGE_NAME%:latest

echo Pushing %IMAGE_NAME%:v1.0
docker push %IMAGE_NAME%:v1.0

echo Pushing %IMAGE_NAME%:%datestamp%
docker push %IMAGE_NAME%:%datestamp%

echo.
echo ✅ All images pushed successfully!
echo.
echo DockerHub Repository: https://hub.docker.com/r/%DOCKERHUB_USERNAME%/pv-detection
echo.
echo Pull commands:
echo   docker pull %IMAGE_NAME%:latest
echo   docker pull %IMAGE_NAME%:v1.0
echo   docker pull %IMAGE_NAME%:%datestamp%

pause