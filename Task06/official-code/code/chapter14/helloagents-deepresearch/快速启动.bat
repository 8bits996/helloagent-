@echo off
chcp 65001 >nul
title DeepResearch Agent 快速启动
color 0A

echo.
echo     ╔═══════════════════════════════════════╗
echo     ║   DeepResearch Agent 快速启动工具    ║
echo     ╚═══════════════════════════════════════╝
echo.
echo     📚 自动化深度研究智能体
echo     🚀 版本: v1.0
echo.

cd /d "%~dp0"

REM 启动后端
echo [1/2] 🔧 启动后端服务...
start "🔧 DeepResearch Backend" /min cmd /k "title DeepResearch Backend && color 0B && cd /d "%~dp0backend" && echo. && echo ════════════════════════════════════════ && echo    DeepResearch Backend 后端服务 && echo ════════════════════════════════════════ && echo. && echo 📍 地址: http://localhost:8000 && echo 📄 API文档: http://localhost:8000/docs && echo. && echo 正在启动... && echo. && python src\main.py"

echo    ✅ 后端服务启动命令已发送
timeout /t 6 /nobreak >nul

REM 启动前端
echo.
echo [2/2] 🎨 启动前端服务...
start "🎨 DeepResearch Frontend" /min cmd /k "title DeepResearch Frontend && color 0D && cd /d "%~dp0frontend" && echo. && echo ════════════════════════════════════════ && echo    DeepResearch Frontend 前端界面 && echo ════════════════════════════════════════ && echo. && echo 📍 地址: http://localhost:5174 && echo. && echo 正在启动... && echo. && npm run dev"

echo    ✅ 前端服务启动命令已发送
timeout /t 4 /nobreak >nul

echo.
echo     ╔═══════════════════════════════════════╗
echo     ║         🎉 服务启动完成！            ║
echo     ╚═══════════════════════════════════════╝
echo.
echo     📌 服务信息:
echo        • 前端界面: http://localhost:5174
echo        • 后端API:  http://localhost:8000
echo        • API文档:  http://localhost:8000/docs
echo.
echo     💡 使用提示:
echo        • 最小化的窗口即为服务进程
echo        • 关闭窗口即可停止对应服务
echo        • 按任意键打开前端页面
echo.

pause >nul
start http://localhost:5174

timeout /t 2 /nobreak >nul
exit
