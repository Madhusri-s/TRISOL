#!/bin/bash

# EcoInnovators PV Detection Docker Run Script

set -e

# Configuration
IMAGE_NAME="ecoinnovators/pv-detection:latest"
CONTAINER_NAME="eco-pv-pipeline"
HOST_PORT="8080"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Running EcoInnovators PV Detection Pipeline${NC}"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Stop existing container if running
if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
    echo -e "${YELLOW}🛑 Stopping existing container: ${CONTAINER_NAME}${NC}"
    docker stop ${CONTAINER_NAME}
fi

# Remove existing container if exists
if docker ps -aq -f name=${CONTAINER_NAME} | grep -q .; then
    echo -e "${YELLOW}🗑️  Removing existing container: ${CONTAINER_NAME}${NC}"
    docker rm ${CONTAINER_NAME}
fi

# Create directories for volumes
mkdir -p ./data ./outputs ./logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit .env file with your API keys before running again.${NC}"
    exit 1
fi

# Run the container
echo -e "${BLUE}🐳 Starting container: ${CONTAINER_NAME}${NC}"
docker run -d \
    --name ${CONTAINER_NAME} \
    --env-file .env \
    -p ${HOST_PORT}:8080 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/outputs:/app/outputs \
    -v $(pwd)/logs:/app/logs \
    --restart unless-stopped \
    ${IMAGE_NAME}

# Wait for container to start
echo -e "${YELLOW}⏳ Waiting for container to start...${NC}"
sleep 5

# Check container status
if docker ps -q -f name=${CONTAINER_NAME} | grep -q .; then
    echo -e "${GREEN}✅ Container started successfully!${NC}"
    echo ""
    echo "Container Details:"
    docker ps -f name=${CONTAINER_NAME}
    echo ""
    echo "Logs:"
    echo "  docker logs ${CONTAINER_NAME}"
    echo "  docker logs -f ${CONTAINER_NAME}  # Follow logs"
    echo ""
    echo "Access:"
    echo "  Container: http://localhost:${HOST_PORT}"
    echo "  Shell: docker exec -it ${CONTAINER_NAME} bash"
else
    echo -e "${RED}❌ Container failed to start. Check logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi