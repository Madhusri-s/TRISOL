#!/bin/bash

# EcoInnovators PV Detection Docker Build Script

set -e

# Configuration
IMAGE_NAME="ecoinnovators/pv-detection"
VERSION="latest"
DOCKERFILE_PATH="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Building EcoInnovators PV Detection Docker Image${NC}"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build the image
echo -e "${YELLOW}📦 Building Docker image: ${IMAGE_NAME}:${VERSION}${NC}"
docker build -t ${IMAGE_NAME}:${VERSION} ${DOCKERFILE_PATH}

# Tag with additional versions
echo -e "${YELLOW}🏷️  Tagging image with version tags${NC}"
docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:v1.0
docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:$(date +%Y%m%d)

# Show image info
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""
echo "Image Details:"
docker images ${IMAGE_NAME}

echo ""
echo -e "${GREEN}🎉 Docker image built successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Test the image: docker run --rm ${IMAGE_NAME}:${VERSION}"
echo "2. Push to DockerHub: docker push ${IMAGE_NAME}:${VERSION}"
echo "3. Run with docker-compose: docker-compose up"