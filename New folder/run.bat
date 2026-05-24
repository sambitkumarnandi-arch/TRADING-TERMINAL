@echo off
title QUANT TERMINAL v4
cd /d "%~dp0"

echo ============================================
echo   QUANT TERMINAL v4 - Bloomberg-Style
echo   Initializing...
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found!
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [1/3] Installing Python dependencies...
echo.

:: Install git if not available for tvdatafeed dependency
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git not found. Installing via winget...
    winget install Git.Git --accept-source-agreements --accept-package-agreements >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Could not auto-install Git.
        echo The tvdatafeed library requires Git. Please install it manually from:
        echo https://git-scm.com/download/win
    )
)

pip install --upgrade --no-cache-dir ^
    git+https://github.com/rongardF/tvdatafeed.git ^
    fastapi uvicorn pandas numpy openpyxl pytz ^
    requests beautifulsoup4 lxml feedparser ^
    python-dateutil -q

if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)

echo [2/3] Starting server...
echo.
echo ============================================
echo   QUANT TERMINAL v4 IS RUNNING!
echo.
echo   Open this URL in your browser:
echo   -^>  http://localhost:8000
echo.
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

cd /d "%~dp0backend"
python -m uvicorn app:app --host 0.0.0.0 --port 8000

pause
