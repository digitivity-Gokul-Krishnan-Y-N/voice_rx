@echo off
REM Integrated Consultation System Startup Script
REM Starts API server and opens consultation page

echo.
echo ========================================
echo   VOICE CONSULTATION SYSTEM
echo   Integrated Setup & Startup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not installed!
    echo Please install Python 3.8+ from python.org
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install -q -r api_requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo [2/4] Checking data directories...
if not exist "data\" mkdir data
if not exist "data\audio\" mkdir data\audio
echo ✓ Directories ready

echo.
echo [3/4] Starting API Server...
echo ✓ Server will run on http://localhost:5000
echo ✓ Keep this window open while using the consultation page
echo.

title Medical Consultation API Server
python api.py

if %errorlevel% neq 0 (
    echo ERROR: API Server failed to start
    pause
    exit /b 1
)

pause
