@echo off
title Quant Terminal v4

echo ====================================
echo   QUANT TERMINAL v4
echo ====================================
echo.

:: Kill any existing uvicorn on port 8080
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080 "') do (
    if NOT "%%a"=="0" (
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo [1/2] Installing/updating dependencies...
pip install -r requirements.txt -q

echo [2/2] Starting server...
echo.
echo Open: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.
start http://localhost:8080
uvicorn backend.app:app --host 0.0.0.0 --port 8080 --reload
