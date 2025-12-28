@echo off
chcp 65001 >nul 2>&1
title Apply Stable Configuration
color 0E

echo.
echo ================================================
echo    Apply Stable Configuration
echo ================================================
echo.

cd /d "%~dp0backend"

echo Backing up current configuration...
if exist .env (
    copy /Y .env .env.backup >nul
    echo Current .env backed up to .env.backup
) else (
    echo No existing .env found
)

echo.
echo Applying stable configuration...
if exist .env.stable (
    copy /Y .env.stable .env >nul
    echo Stable configuration applied successfully!
    echo.
    echo Key changes:
    echo - LLM_TIMEOUT: 300 seconds
    echo - MAX_WEB_RESEARCH_LOOPS: 1
    echo - LOG_LEVEL: INFO
    echo.
    echo Please restart services for changes to take effect:
    echo 1. Run STOP.bat
    echo 2. Run START.bat
) else (
    echo ERROR: .env.stable not found!
    echo Please ensure .env.stable exists in backend directory.
)

echo.
echo ================================================
pause
