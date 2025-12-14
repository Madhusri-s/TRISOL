#!/bin/bash

# EcoInnovators PV Detection Docker Push Script

set -e

# Configuration
IMAGE_NAME="ecoinnovators/pv-detection"
DOCKERHUB_USERNAME="ecoinnovators"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Pushing EcoInnovators PV Detection to DockerHub${NC}"
echo "====================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if user is logged in to DockerHub
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}🔐 Please login to DockerHub first:${NC}"
    echo "docker login"
    exit 1
fi

# Check if image exists
if ! docker images ${IMAGE_NAME} | grep -q ${IMAGE_NAME}; then
    echo -e "${RED}❌ Image ${IMAGE_NAME} not found. Please build it first:${NC}"
    echo "./docker/build.sh"
    exit 1
fi

# Push all tags
echo -e "${YELLOW}📤 Pushing images to DockerHub...${NC}"

echo -e "${BLUE}Pushing ${IMAGE_NAME}:latest${NC}"
docker push ${IMAGE_NAME}:latest

echo -e "${BLUE}Pushing ${IMAGE_NAME}:v1.0${NC}"
docker push ${IMAGE_NAME}:v1.0

echo -e "${BLUE}Pushing ${IMAGE_NAME}:$(date +%Y%m%d)${NC}"
docker push ${IMAGE_NAME}:$(date +%Y%m%d)

echo ""
echo -e "${GREEN}✅ All images pushed successfully!${NC}"
echo ""
echo "DockerHub Repository: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/pv-detection"
echo ""
echo "Pull commands:"
echo "  docker pull ${IMAGE_NAME}:latest"
echo "  docker pull ${IMAGE_NAME}:v1.0"
echo "  docker pull ${IMAGE_NAME}:$(date +%Y%m%d)"