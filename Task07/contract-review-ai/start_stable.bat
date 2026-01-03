@echo off
chcp 65001 >nul
title 合同评审AI系统 - 稳定版服务管理器

echo ============================================================
echo           合同评审AI系统 - 稳定版启动脚本 v2.0
echo ============================================================
echo.

cd /d "%~dp0"

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查并终止可能存在的旧进程
echo [1/3] 检查并清理旧进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo 终止端口 8000 上的进程 PID=%%a
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501 " ^| findstr "LISTENING"') do (
    echo 终止端口 8501 上的进程 PID=%%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [2/3] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
)

echo [3/3] 启动服务管理器...
echo.
echo ============================================================
echo   服务地址:
echo     后端 API: http://127.0.0.1:8000
echo     API 文档: http://127.0.0.1:8000/docs
echo     前端界面: http://localhost:8501
echo.
echo   按 Ctrl+C 停止所有服务
echo ============================================================
echo.

python run_services.py

pause
