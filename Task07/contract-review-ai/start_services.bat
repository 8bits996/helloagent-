@echo off
echo ========================================
echo 合同智能评审系统 - 启动服务
echo ========================================

cd /d %~dp0

echo.
echo [1/2] 启动 FastAPI 后端 (端口 8000)...
start "FastAPI Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo.
echo [2/2] 启动 Streamlit 前端 (端口 8501)...
timeout /t 3 /nobreak > nul
start "Streamlit Frontend" cmd /k "python -m streamlit run app/frontend.py --server.port 8501"

echo.
echo ========================================
echo 服务启动完成！
echo.
echo FastAPI 后端: http://localhost:8000
echo API 文档:     http://localhost:8000/docs
echo Streamlit:    http://localhost:8501
echo ========================================
echo.
echo 请在浏览器中打开 http://localhost:8501
echo.
pause
