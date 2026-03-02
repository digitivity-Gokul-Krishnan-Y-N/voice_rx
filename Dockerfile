# Multi-stage build for Voice RX - Medical Prescription Extraction System

# Stage 1: Build React Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend dependencies
COPY digidoc_v3_consultation/package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy frontend source
COPY digidoc_v3_consultation/public ./public
COPY digidoc_v3_consultation/src ./src

# Build the React app
RUN npm run build

# Stage 2: Python Backend with Audio Processing
FROM python:3.11-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend source
COPY src ./src
COPY config ./config
COPY consultation_pages ./consultation_pages
COPY data ./data
COPY tests ./tests

# Copy documentation and configuration files
COPY README.md ./
COPY requirements.txt ./

# Copy built React frontend from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create directory for logs and data
RUN mkdir -p /app/logs /app/data

# Expose ports
EXPOSE 3000 8000 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command (can be overridden)
CMD ["python", "src/pipeline.py"]
