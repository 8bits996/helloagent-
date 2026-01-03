@echo off
echo ========================================
echo Contract Review AI System - Start All Services
echo ========================================

cd /d "%~dp0"

echo.
echo [1/3] Starting CodeBuddy AI Engine (Port 3000)...
start "CodeBuddy Engine" cmd /k "codebuddy --serve --port 3000"

echo.
echo [2/3] Starting FastAPI Backend (Port 8000)...
timeout /t 5 /nobreak > nul
start "FastAPI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [3/3] Starting Streamlit Frontend (Port 8501)...
timeout /t 5 /nobreak > nul
start "Streamlit Frontend" cmd /k "python -m streamlit run app/frontend.py"

echo.
echo ========================================
echo All services started!
echo.
echo Please wait a moment for the browser to open.
echo Frontend URL: http://localhost:8501
echo ========================================
echo.
pause
