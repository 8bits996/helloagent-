@echo off
REM 合同评审AI系统 - 启动脚本 (Windows)

echo ======================================
echo   合同评审AI系统启动脚本
echo ======================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [提示] 依赖未安装，正在安装...
    pip install -r requirements.txt
)

echo [2/4] 创建.env文件...
if not exist .env (
    copy .env.example .env
    echo [完成] 已创建.env配置文件
) else (
    echo [跳过] .env文件已存在
)

echo.
echo ======================================
echo   请在3个终端中分别运行以下命令:
echo ======================================
echo.
echo 终端1 - 启动CodeBuddy:
echo   codebuddy --serve --port 3000
echo.
echo 终端2 - 启动FastAPI:
echo   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
echo 终端3 - 启动Streamlit (开发中):
echo   streamlit run app/frontend.py
echo.
echo ======================================
echo.

echo [3/4] 测试MarkItDown集成...
python test_markitdown.py

echo.
echo [4/4] 准备完成！
echo.
echo 访问地址:
echo   - FastAPI文档: http://localhost:8000/docs
echo   - Streamlit界面: http://localhost:8501 (开发中)
echo.

pause
