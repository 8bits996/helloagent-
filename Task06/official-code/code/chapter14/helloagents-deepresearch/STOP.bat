@echo off
chcp 65001 >nul 2>&1
title Stop DeepResearch Services
color 0C

echo.
echo ================================================
echo    Stopping DeepResearch Services
echo ================================================
echo.

echo [1/2] Stopping Backend (Python)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 echo Backend stopped (PID: %%a)
)

echo.
echo [2/2] Stopping Frontend (Node)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5174" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 echo Frontend stopped (PID: %%a)
)

echo.
echo ================================================
echo    All Services Stopped
echo ================================================
echo.
pause
