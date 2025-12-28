@echo off
chcp 65001 >nul 2>&1
title DeepResearch Agent Startup
color 0A

echo.
echo ================================================
echo    DeepResearch Agent - Quick Start
echo ================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting Backend Service...
start "Backend-8000" cmd /k "cd /d "%~dp0backend" && title Backend Service (Port 8000) && color 0B && python src\main.py"

timeout /t 5 /nobreak >nul

echo [2/2] Starting Frontend Service...
start "Frontend-5174" cmd /k "cd /d "%~dp0frontend" && title Frontend Service (Port 5174) && color 0D && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo    Services Started Successfully!
echo ================================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5174
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:5174

timeout /t 2 /nobreak >nul
exit
