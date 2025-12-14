# Docker Deployment Guide

This guide explains how to build, run, and deploy the EcoInnovators PV Detection Pipeline using Docker.

## 🐳 Docker Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [DockerHub account](https://hub.docker.com/) (for pushing images)
- Git (for cloning the repository)

### Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd eco-pv-detection
```

2. **Set up environment variables**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
# Required: ROBOFLOW_API_KEY
```

3. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

## 🔨 Building the Docker Image

### Windows Users

#### Option 1: Batch Script (Recommended)
```cmd
cd eco-pv-detection
docker\build.bat
```

#### Option 2: PowerShell Script
```powershell
cd eco-pv-detection
.\docker\build.ps1
```

#### Option 3: Manual Build
```cmd
docker build -t ecoinnovators/pv-detection:latest .
```

### Linux/Mac Users

#### Option 1: Shell Script
```bash
cd eco-pv-detection
chmod +x docker/*.sh
./docker/build.sh
```

#### Option 2: Manual Build
```bash
docker build -t ecoinnovators/pv-detection:latest .
```

## 🚀 Running the Container

### Windows Users

#### Using Batch Script
```cmd
docker\run.bat
```

#### Using Docker Compose
```cmd
docker-compose up -d
```

#### Manual Run
```cmd
docker run -d ^
  --name eco-pv-pipeline ^
  --env-file .env ^
  -p 8080:8080 ^
  -v "%cd%\data:/app/data" ^
  -v "%cd%\outputs:/app/outputs" ^
  -v "%cd%\logs:/app/logs" ^
  ecoinnovators/pv-detection:latest
```

### Linux/Mac Users

#### Using Shell Script
```bash
./docker/run.sh
```

#### Using Docker Compose
```bash
docker-compose up -d
```

## 📤 Pushing to DockerHub

### 1. Login to DockerHub
```bash
docker login
```

### 2. Push the Image

#### Windows
```cmd
docker\push.bat
```

#### Linux/Mac
```bash
./docker/push.sh
```

#### Manual Push
```bash
docker push ecoinnovators/pv-detection:latest
docker push ecoinnovators/pv-detection:v1.0
```

## 🔧 Docker Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
ROBOFLOW_API_KEY=your_roboflow_api_key_here

# Optional
ROBOFLOW_WORKSPACE=alfred-weber-institute-of-economics
ROBOFLOW_PROJECT=custom-workflow-object-detection-tgnqc
ROBOFLOW_VERSION=8
BASE_DIR=/app/data
OUTPUT_DIR=/app/outputs
LOG_LEVEL=INFO
MODEL_ID=custom-workflow-object-detection-tgnqc/8
CONFIDENCE_THRESHOLD=0.5
```

### Volume Mounts

The container uses the following volume mounts:

- `./data:/app/data` - Dataset storage
- `./outputs:/app/outputs` - Results and predictions
- `./logs:/app/logs` - Application logs

### Ports

- `8080` - Main application port
- `8888` - Jupyter notebook (development profile)

## 🐛 Troubleshooting

### Common Issues

#### 1. Docker not running
```
❌ Docker is not running. Please start Docker Desktop and try again.
```
**Solution**: Start Docker Desktop and wait for it to fully initialize.

#### 2. Permission denied (Linux/Mac)
```
permission denied while trying to connect to the Docker daemon socket
```
**Solution**: Add your user to the docker group or use `sudo`.

#### 3. Port already in use
```
Error: bind: address already in use
```
**Solution**: Stop existing containers or use a different port.

#### 4. Environment file missing
```
⚠️ .env file not found
```
**Solution**: Copy `.env.example` to `.env` and fill in your API keys.

### Useful Commands

#### Container Management
```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Stop container
docker stop eco-pv-pipeline

# Remove container
docker rm eco-pv-pipeline

# View logs
docker logs eco-pv-pipeline

# Follow logs
docker logs -f eco-pv-pipeline

# Execute shell in container
docker exec -it eco-pv-pipeline bash
```

#### Image Management
```bash
# List images
docker images

# Remove image
docker rmi ecoinnovators/pv-detection:latest

# Pull from DockerHub
docker pull ecoinnovators/pv-detection:latest
```

#### System Cleanup
```bash
# Remove unused containers, networks, images
docker system prune

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune
```

## 🌐 DockerHub Repository

Once pushed, your image will be available at:
- **Repository**: https://hub.docker.com/r/ecoinnovators/pv-detection
- **Pull Command**: `docker pull ecoinnovators/pv-detection:latest`

### Available Tags
- `latest` - Latest stable version
- `v1.0` - Version 1.0 release
- `YYYYMMDD` - Daily builds (e.g., `20241214`)

## 🔄 Development Workflow

### 1. Development with Jupyter
```bash
# Start development environment
docker-compose --profile dev up

# Access Jupyter at http://localhost:8888
```

### 2. Testing Changes
```bash
# Rebuild after code changes
docker-compose up --build

# Run tests
docker-compose exec eco-pv-detection python -m pytest
```

### 3. Production Deployment
```bash
# Build production image
docker build -t ecoinnovators/pv-detection:latest .

# Push to registry
docker push ecoinnovators/pv-detection:latest

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Health Checks

The container includes health checks to monitor the application:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' eco-pv-pipeline

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' eco-pv-pipeline
```

## 🔒 Security Considerations

- The container runs as a non-root user (`ecouser`)
- Sensitive data should be passed via environment variables
- Use Docker secrets for production deployments
- Regularly update base images for security patches

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [DockerHub Documentation](https://docs.docker.com/docker-hub/)
- [EcoInnovators Pipeline Documentation](./README.md)