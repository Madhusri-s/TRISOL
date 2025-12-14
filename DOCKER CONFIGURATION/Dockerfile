# EcoInnovators PV Detection Pipeline Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pipeline/ ./pipeline/
COPY model/ ./model/
COPY predictions/ ./predictions/
COPY artifacts/ ./artifacts/
COPY training_logs/ ./training_logs/
COPY *.md ./
COPY *.pdf ./

# Create necessary directories
RUN mkdir -p /app/data /app/outputs /app/logs

# Set permissions
RUN chmod -R 755 /app

# Create non-root user for security
RUN useradd -m -u 1000 ecouser && \
    chown -R ecouser:ecouser /app
USER ecouser

# Expose port for potential web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pipeline.inference; print('Pipeline ready')" || exit 1

# Default command
CMD ["python", "-c", "from pipeline.inference import EcoPVPipeline; print('EcoInnovators PV Detection Pipeline Ready!')"]