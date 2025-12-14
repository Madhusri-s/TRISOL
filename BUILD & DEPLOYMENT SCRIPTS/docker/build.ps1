# EcoInnovators PV Detection Docker Build Script (PowerShell)

param(
    [string]$ImageName = "ecoinnovators/pv-detection",
    [string]$Version = "latest",
    [string]$DockerfilePath = "."
)

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

Write-Host "${Green}🚀 Building EcoInnovators PV Detection Docker Image${Reset}"
Write-Host "=================================================="

# Check if Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "${Red}❌ Docker is not running. Please start Docker Desktop and try again.${Reset}"
    Read-Host "Press Enter to exit"
    exit 1
}

# Build the image
Write-Host "${Yellow}📦 Building Docker image: ${ImageName}:${Version}${Reset}"
try {
    docker build -t "${ImageName}:${Version}" $DockerfilePath
    if ($LASTEXITCODE -ne 0) { throw "Docker build failed" }
} catch {
    Write-Host "${Red}❌ Docker build failed!${Reset}"
    Read-Host "Press Enter to exit"
    exit 1
}

# Tag with additional versions
Write-Host "${Yellow}🏷️  Tagging image with version tags${Reset}"
$DateStamp = Get-Date -Format "yyyyMMdd"
docker tag "${ImageName}:${Version}" "${ImageName}:v1.0"
docker tag "${ImageName}:${Version}" "${ImageName}:${DateStamp}"

# Show image info
Write-Host "${Green}✅ Build completed successfully!${Reset}"
Write-Host ""
Write-Host "Image Details:"
docker images $ImageName

Write-Host ""
Write-Host "${Green}🎉 Docker image built successfully!${Reset}"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Test the image: docker run --rm ${ImageName}:${Version}"
Write-Host "2. Push to DockerHub: docker push ${ImageName}:${Version}"
Write-Host "3. Run with docker-compose: docker-compose up"

Read-Host "Press Enter to exit"