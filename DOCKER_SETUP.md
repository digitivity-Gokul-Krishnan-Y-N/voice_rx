# Docker Setup Guide for Voice RX

## Overview
This project includes Docker configuration for containerizing the Voice RX Medical Prescription Extraction System with both Python backend and React frontend, including all consultation pages and related modules.

## Project Structure in Docker

The Docker image includes:
- **React Frontend** (`digidoc_v3_consultation/`) - Main UI application
- **Python Backend** (`src/`) - Medical extraction system
- **Consultation Pages** (`consultation_pages/`) - Specialized consultation components
  - `api.py` - API endpoints for consultation
  - `Consultation.jsx` - Main consultation component
  - `ConsultationDetails/` - Detailed consultation views
  - `ConsultationFollowUp/` - Follow-up consultation handling
  - `ConsultationMedicines/` - Medicine prescription interface
  - `ConsultationTests/` - Medical test management
  - `data/` - Audio and consultation data
  - `i18n/` - Internationalization support
- **Configuration** (`config/`) - System configuration files
- **Tests** (`tests/`) - Automated test suite
- **Data** (`data/`) - Application data and persistence

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

### Option 4: Development with Consultation Page Changes

When modifying consultation pages:

```bash
# Keep container running with volume mounts for live reload
docker-compose up -d

# Watch console logs for errors
docker-compose logs -f voice-rx

# Any changes to consultation_pages/ are reflected automatically
```

Changes to the following are picked up automatically:
- `src/*.py` - Python modules
- `consultation_pages/**/*.jsx` - React components
- `consultation_pages/**/*.py` - API endpoints
- `config/` - Configuration files

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
- `./consultation_pages` → `/app/consultation_pages` - Consultation components and API
- `./logs` → `/app/logs` - Application logs
- `./data` → `/app/data` - Data files and audio

## API Endpoints

### Consultation Pages API
The `consultation_pages/api.py` provides endpoints for:
- Managing consultations
- Handling medicine prescriptions
- Managing medical tests
- Processing audio uploads
- Supporting multiple languages (i18n)

### Available Routes
When running the container, access:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:5000`
- **Consultation API**: Available through backend

### Audio File Handling
Audio uploads are stored in:
- Container: `/app/consultation_pages/data/audio/`
- Volume mount: `./consultation_pages/data/audio/`

Supported formats:
- `.webm` - WebM format
- `.mp3` - MP3 format
- `.wav` - WAV format

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

## Consultation Pages Integration

### Overview
The Consultation Pages module provides a complete consultation management system integrated with the medical prescription extraction service.

### Component Structure

```
consultation_pages/
├── api.py                           # API endpoints for consultations
├── Consultation.jsx                 # Main consultation component
├── ConsultationDetails/
│   └── ConsultationDetails.jsx      # Detailed consultation view
├── ConsultationFollowUp/
│   ├── ConsultationFollowUp.jsx     # Follow-up management
│   ├── ConsultationFollowUp_2.jsx   # Additional follow-up features
│   ├── PreviewPrescription.jsx      # Prescription preview
│   └── UploadPrescription.jsx       # Upload new prescriptions
├── ConsultationMedicines/
│   ├── AddConsultationMedicines.jsx # Add medicines
│   ├── ConsultationMedList.jsx      # Medicine list view
│   ├── EditConsultationMedicines.jsx # Edit medicines
│   └── MedicineCard.jsx             # Medicine card component
├── ConsultationTests/
│   ├── TestsCard.jsx                # Test card component
│   ├── TestsList.jsx                # Tests list view
│   ├── HomeTest/
│   │   ├── AddHomeTest.jsx          # Add home tests
│   │   └── EditHomeTest.jsx         # Edit home tests
│   └── LabTest/
│       ├── AddLabTest.jsx           # Add lab tests
│       └── EditLabTest.jsx          # Edit lab tests
├── data/
│   └── audio/                       # Audio file storage
└── i18n/                            # Internationalization files
```

### Features

1. **Consultation Management**
   - Create and manage consultations
   - Track consultation history
   - Link to prescriptions and tests

2. **Medicine Management**
   - Add/edit/delete medicines
   - Prescription generation
   - Medicine dosage tracking

3. **Test Management**
   - Home tests
   - Lab tests
   - Test result tracking

4. **Audio Processing**
   - Upload consultation audio
   - Automatic transcription
   - Speech-to-prescription conversion

5. **Multi-language Support**
   - Internationalization configuration
   - Support for multiple languages
   - Localized content delivery

### API Endpoints

The `api.py` file exposes the following endpoints (when integrated with Flask/FastAPI):

```
POST   /api/consultations              # Create consultation
GET    /api/consultations/{id}         # Get consultation details
PATCH  /api/consultations/{id}         # Update consultation
DELETE /api/consultations/{id}         # Delete consultation

GET    /api/consultations/{id}/medicines    # Get medicines
POST   /api/consultations/{id}/medicines    # Add medicine
PUT    /api/consultations/{id}/medicines/{mid}  # Update medicine

GET    /api/consultations/{id}/tests        # Get tests
POST   /api/consultations/{id}/tests        # Add test

POST   /api/consultations/{id}/audio        # Upload audio
GET    /api/consultations/{id}/audio        # Get audio files
```

### Working with Consultation Pages in Docker

#### During Development

Keep the container running and mount the consultation_pages volume:

```bash
docker-compose up -d
cd consultation_pages
# Edit JSX and Python files - changes are reflected automatically
```

#### Building with Consultation Pages

The Docker build process:
1. Builds React components including consultation pages
2. Copies all consultation_pages files to the container
3. Makes API endpoints available through Python backend
4. Serves static files through frontend

#### Data Persistence

Consultation data is stored in volumes:
- Audio files: `consultation_pages/data/audio/`
- Database: `data/` (if using database)
- User preferences: Stored in browser localStorage

### Troubleshooting Consultation Pages

#### Audio Upload Issues

```bash
# Check audio directory permissions
docker exec voice-rx ls -la /app/consultation_pages/data/audio/

# Check available disk space
docker exec voice-rx df -h
```

#### API Connection Issues

```bash
# Verify API is running
docker exec voice-rx curl -s http://localhost:5000/health

# Check API logs
docker-compose logs voice-rx | grep api
```

#### JavaScript Module Issues

```bash
# Rebuild frontend with consultation pages
docker-compose build --no-cache voice-rx

# Clear browser cache and reload
# Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
```

### Performance Optimization for Consultation Pages

1. **Lazy Loading Components**
   - Load consultation components on demand
   - Reduce initial bundle size
   - Faster page loads

2. **Audio Compression**
   - Compress audio files before upload
   - Reduce storage requirements
   - Faster transmission

3. **Database Indexing**
   - Index consultation queries
   - Faster data retrieval
   - Better API response times

4. **Caching Strategy**
   - Cache frequently accessed consultations
   - Cache medicine/test data
   - Implement Redis for session management

---

For more information, visit:
- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Documentation](https://docs.docker.com/compose)
- [Project README](./README.md)
