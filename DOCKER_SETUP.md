# Docker Setup Guide for Voice RX

## Overview
This project includes Docker configuration for containerizing the Voice RX Medical Prescription Extraction System with both Python backend and React frontend.

## Files Created

### 1. **Dockerfile**
Multi-stage Docker build that:
- Builds React frontend using Node.js
- Sets up Python backend with audio processing libraries
- Combines both services in a single container
- Includes health checks and proper environment configuration

### 2. **docker-compose.yml**
Orchestrates containers for easier deployment:
- Main service (`voice-rx`) with both backend and frontend
- Optional development service (`frontend-dev`) for frontend development
- Volume mounts for code updates and data persistence
- Environment configuration and health checks

### 3. **.dockerignore**
Optimizes Docker build context by excluding:
- Git files and cache
- Python caches (`__pycache__`, `*.pyc`)
- Node modules (rebuilt in container)
- Build artifacts and logs
- IDE configuration files

### 4. **Dockerfile.dev** (Frontend)
Development Dockerfile for standalone React frontend development

## Usage

### Option 1: Using Docker Compose (Recommended)

#### Build the image
```bash
docker-compose build
```

#### Run the application
```bash
docker-compose up
```

#### Stop the application
```bash
docker-compose down
```

#### View logs
```bash
docker-compose logs -f
```

#### Run in background
```bash
docker-compose up -d
```

### Option 2: Using Docker Directly

#### Build the image
```bash
docker build -t voice-rx:latest .
```

#### Run the container
```bash
docker run -p 3000:3000 -p 5000:5000 -v $(pwd)/data:/app/data voice-rx:latest
```

#### Run with volume mounts for development
```bash
docker run -p 3000:3000 -p 5000:5000 \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  voice-rx:latest
```

### Option 3: Frontend Development Only

```bash
docker-compose --profile dev up frontend-dev
```

## Port Mappings

- **3000**: React Frontend
- **5000**: Python Flask Backend
- **8000**: Alternative Backend Port
- **3001**: Frontend Dev Server (when using dev profile)

## Environment Variables

Configure these in `docker-compose.yml` or when running containers:

```bash
PYTHONUNBUFFERED=1           # Unbuffered Python output
PYTHONDONTWRITEBYTECODE=1    # Don't create .pyc files
FLASK_ENV=production         # Flask environment
REACT_APP_API_URL=           # Frontend API endpoint
```

## Volume Mounts

- `./src` → `/app/src` - Python source code
- `./config` → `/app/config` - Configuration files
- `./logs` → `/app/logs` - Application logs
- `./data` → `/app/data` - Data files

## System Requirements

### Prerequisites
- Docker >= 20.10
- Docker Compose >= 1.29 (for compose approach)
- 4GB RAM minimum
- 2GB disk space for images

### Audio Processing Support
The Docker image includes:
- FFmpeg for audio processing
- LibSndFile for WAV handling
- BLAS/LAPACK for numerical computing

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs voice-rx

# Check image build
docker build -t voice-rx:latest . --verbose
```

### Port already in use
```bash
# Change ports in docker-compose.yml or use different port:
docker run -p 8080:3000 -p 8001:5000 voice-rx:latest
```

### Missing dependencies
```bash
# Rebuild without cache
docker-compose build --no-cache
```

### Slow builds
- Use `.dockerignore` to exclude unnecessary files
- Consider using BuildKit: `DOCKER_BUILDKIT=1 docker build .`

## Production Deployment

For production deployments:

1. **Use specific versions** in Dockerfile
2. **Add security scanning**: `docker scan voice-rx:latest`
3. **Use secrets management** for sensitive data
4. **Enable container logging**: Configure Docker daemon
5. **Use health checks** (already configured)
6. **Resource limits**: Add to docker-compose.yml:

```yaml
services:
  voice-rx:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Performance Optimization

### Multi-stage build benefits:
- Smaller final image size
- Faster deployment
- Better security (build dependencies not included)

### Current image size estimates:
- React build artifacts: ~50-100MB
- Python dependencies: ~300-500MB
- Total: ~400-600MB

### To reduce image size further:
1. Use `python:3.11-slim` (already using)
2. Clean pip cache (already configured)
3. Remove test files from production image
4. Use Alpine variants where possible

## Next Steps

1. Update `requirements.txt` if adding new Python packages
2. Update `package.json` if adding frontend dependencies
3. Configure environment variables for your setup
4. Set up CI/CD pipeline integration
5. Consider using Kubernetes for orchestration

---

For more information, visit:
- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Documentation](https://docs.docker.com/compose)
- [Project README](./README.md)
