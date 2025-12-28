@echo off
chcp 65001 >nul
echo ====================================
echo   DeepResearch Agent 服务重启
echo ====================================
echo.

echo [步骤 1] 停止现有服务...
call "%~dp0停止所有服务.bat"

echo.
echo [步骤 2] 等待服务完全停止...
timeout /t 3 /nobreak >nul

echo.
echo [步骤 3] 启动服务...
call "%~dp0启动所有服务.bat"
