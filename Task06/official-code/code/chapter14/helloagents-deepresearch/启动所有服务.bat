@echo off
chcp 65001 >nul
echo ====================================
echo   DeepResearch Agent 一键启动
echo ====================================
echo.

cd /d "%~dp0"

echo [1/3] 检查环境...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)
echo ✅ Python 已安装

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)
echo ✅ Node.js 已安装

echo.
echo [2/3] 启动后端服务...
echo 后端地址: http://localhost:8000
echo.

REM 在新窗口中启动后端
start "DeepResearch Backend" cmd /k "cd /d "%~dp0backend" && echo 正在启动后端服务... && python src\main.py"

REM 等待后端启动
timeout /t 5 /nobreak >nul

echo.
echo [3/3] 启动前端服务...
echo 前端地址: http://localhost:5174
echo.

REM 在新窗口中启动前端
start "DeepResearch Frontend" cmd /k "cd /d "%~dp0frontend" && echo 正在启动前端服务... && npm run dev"

REM 等待前端启动
timeout /t 3 /nobreak >nul

echo.
echo ====================================
echo   🎉 服务启动完成！
echo ====================================
echo.
echo 📌 服务信息:
echo    - 后端: http://localhost:8000
echo    - 前端: http://localhost:5174
echo    - API文档: http://localhost:8000/docs
echo.
echo 💡 提示:
echo    - 前端界面将在新窗口中打开
echo    - 关闭命令窗口即可停止服务
echo    - 按任意键打开前端页面...
echo.
pause >nul

REM 打开浏览器
start http://localhost:5174

echo 浏览器已打开，按任意键退出...
pause >nul
