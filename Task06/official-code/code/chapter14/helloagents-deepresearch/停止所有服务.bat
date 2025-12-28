@echo off
chcp 65001 >nul
echo ====================================
echo   DeepResearch Agent 服务停止
echo ====================================
echo.

echo 正在查找并停止服务...
echo.

REM 停止后端服务 (Python)
echo [1/2] 停止后端服务...
for /f "tokens=2" %%a in ('tasklist ^| findstr "python.exe"') do (
    tasklist /fi "pid eq %%a" /v | findstr "main.py" >nul 2>&1
    if not errorlevel 1 (
        echo 找到后端进程: %%a
        taskkill /pid %%a /f >nul 2>&1
        if not errorlevel 1 (
            echo ✅ 后端服务已停止
        )
    )
)

echo.
echo [2/2] 停止前端服务...
REM 停止前端服务 (Node)
for /f "tokens=2" %%a in ('tasklist ^| findstr "node.exe"') do (
    netstat -ano | findstr "5174" | findstr "%%a" >nul 2>&1
    if not errorlevel 1 (
        echo 找到前端进程: %%a
        taskkill /pid %%a /f >nul 2>&1
        if not errorlevel 1 (
            echo ✅ 前端服务已停止
        )
    )
)

echo.
echo ====================================
echo   ✅ 所有服务已停止
echo ====================================
echo.
pause
