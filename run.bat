@echo off
title AI Price Comparison System Orchestrator
echo ==========================================================
echo       AI Product Price Comparison System Launcher
echo ==========================================================
echo.

:: Check for backend virtual environment
if not exist "backend\.venv" (
    echo [ERROR] Backend virtual environment not found.
    echo Please ensure backend setup has completed.
    pause
    exit /b 1
)

:: Check for frontend node_modules
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not found.
    echo Please wait for frontend npm install to complete.
    pause
    exit /b 1
)

echo Starting Backend Service (Flask REST API on Port 5000)...
start "Price Compare Backend" cmd /c "backend\.venv\Scripts\python.exe backend\app.py"
timeout /t 3 /nobreak >nul

echo Starting Frontend Service (React + Vite)...
start "Price Compare Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ==========================================================
echo Services have been started!
echo - Flask Backend API: http://localhost:5000
echo - React Frontend Dashboard: http://localhost:5173 (standard Vite port)
echo.
echo Press any key to exit this orchestrator screen (servers will remain running).
echo ==========================================================
pause >nul
