@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo AI Assisted Coding 技能安装脚本
echo ========================================
echo.

set SKILL_NAME=ai-assisted-coding
set REPO_URL=https://git.woa.com/cloud-mt/ai-assisted-coding.git
set SCRIPT_DIR=%~dp0
set SKILL_DIR=%SCRIPT_DIR%%SKILL_NAME%
set GLOBAL_SKILL_DIR=%USERPROFILE%\.codebuddy\skills\%SKILL_NAME%

:: 检查是否已下载技能（通过检查是否有真实的 SKILL.md 内容）
findstr /c:"此为占位文件" "%SKILL_DIR%\SKILL.md" >nul 2>&1
if %errorlevel%==0 (
    echo [步骤 1] 正在下载技能...
    echo.
    
    :: 删除占位文件
    rmdir /s /q "%SKILL_DIR%" 2>nul
    
    :: 尝试克隆
    echo 正在从 %REPO_URL% 克隆...
    git clone %REPO_URL% "%SKILL_DIR%"
    
    if %errorlevel% neq 0 (
        echo.
        echo Git 克隆失败，请手动下载:
        echo 1. 访问 %REPO_URL%
        echo 2. 登录 OA 账号后下载 ZIP
        echo 3. 解压到 %SKILL_DIR%
        echo.
        mkdir "%SKILL_DIR%" 2>nul
        pause
        goto :check_skill
    )
    echo 克隆成功!
) else (
    echo [步骤 1] 技能已下载，跳过...
)

:check_skill
echo.

:: 验证技能文件
if not exist "%SKILL_DIR%\SKILL.md" (
    echo 错误: 未找到 SKILL.md 文件
    echo 请确保技能已正确下载到 %SKILL_DIR%
    pause
    exit /b 1
)

echo [步骤 2] 选择安装位置:
echo   1. 全局安装 (所有项目可用): %GLOBAL_SKILL_DIR%
echo   2. 仅当前项目安装
echo   3. 跳过安装 (仅保留在当前目录)
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 正在安装到全局技能目录...
    
    :: 创建目标目录
    if not exist "%USERPROFILE%\.codebuddy\skills" mkdir "%USERPROFILE%\.codebuddy\skills"
    
    :: 删除旧版本
    if exist "%GLOBAL_SKILL_DIR%" rmdir /s /q "%GLOBAL_SKILL_DIR%"
    
    :: 复制文件
    xcopy /E /I /Y "%SKILL_DIR%" "%GLOBAL_SKILL_DIR%"
    
    echo.
    echo 安装完成! 技能已安装到: %GLOBAL_SKILL_DIR%
) else if "%choice%"=="2" (
    echo.
    set /p project_dir="请输入项目路径 (留空使用当前目录): "
    if "!project_dir!"=="" set project_dir=%CD%
    
    set PROJECT_SKILL_DIR=!project_dir!\.codebuddy\skills\%SKILL_NAME%
    
    echo 正在安装到项目目录...
    
    :: 创建目标目录
    if not exist "!project_dir!\.codebuddy\skills" mkdir "!project_dir!\.codebuddy\skills"
    
    :: 删除旧版本
    if exist "!PROJECT_SKILL_DIR!" rmdir /s /q "!PROJECT_SKILL_DIR!"
    
    :: 复制文件
    xcopy /E /I /Y "%SKILL_DIR%" "!PROJECT_SKILL_DIR!"
    
    echo.
    echo 安装完成! 技能已安装到: !PROJECT_SKILL_DIR!
) else (
    echo 跳过安装，技能保留在: %SKILL_DIR%
)

echo.
echo ========================================
echo 安装完成!
echo ========================================
echo.
echo 后续步骤:
echo 1. 重启 CodeBuddy 或刷新技能列表
echo 2. 在对话中使用 /skills 查看已安装技能
echo.
echo 分享给他人:
echo 将整个 %SCRIPT_DIR% 文件夹打包分享即可
echo.
pause
