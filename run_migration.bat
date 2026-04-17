@echo off
chcp 65001 > nul
echo ============================================
echo 为知笔记到 Obsidian 迁移工具
echo ============================================
echo.

REM 检查 Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装 Python，请先安装 Python 3.9+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖
python -c "import bs4, lxml, html2text" > nul 2>&1
if errorlevel 1 (
    echo [提示] 检测到缺少依赖，正在安装...
    pip install beautifulsoup4 lxml html2text
    echo.
)

REM 获取用户输入
set /p WIZ_PATH="请输入为知笔记数据目录（如 D:\为知笔记4.14\My Knowledge）："
set /p OUTPUT_PATH="请输入 Obsidian 输出目录（如 D:\Obsidian_Vault）："

echo.
echo [提示] 开始迁移...
echo 源目录：%WIZ_PATH%
echo 目标目录：%OUTPUT_PATH%
echo.

REM 运行迁移
python wiz2obsidian.py --wiz "%WIZ_PATH%" --output "%OUTPUT_PATH%"

if errorlevel 1 (
    echo.
    echo [错误] 迁移失败，请查看 migration.log
    pause
    exit /b 1
)

echo.
echo ============================================
echo 迁移完成！
echo ============================================
echo.
echo 验证迁移结果...
echo.

REM 运行验证
python validate_migration.py --wiz "%WIZ_PATH%" --obsidian "%OUTPUT_PATH%"

echo.
echo 完成！请查看 migration_report.json 获取详细报告
echo.
pause
