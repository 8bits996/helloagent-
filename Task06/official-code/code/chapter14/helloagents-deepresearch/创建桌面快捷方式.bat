@echo off
chcp 65001 >nul
echo ====================================
echo   创建桌面快捷方式
echo ====================================
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop

echo 正在创建快捷方式...
echo.

REM 创建 VBS 脚本来生成快捷方式
echo Set WshShell = WScript.CreateObject("WScript.Shell") > "%TEMP%\CreateShortcut.vbs"
echo Set Shortcut = WshShell.CreateShortcut("%DESKTOP%\DeepResearch启动.lnk") >> "%TEMP%\CreateShortcut.vbs"
echo Shortcut.TargetPath = "%SCRIPT_DIR%快速启动.bat" >> "%TEMP%\CreateShortcut.vbs"
echo Shortcut.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\CreateShortcut.vbs"
echo Shortcut.Description = "DeepResearch Agent 快速启动" >> "%TEMP%\CreateShortcut.vbs"
echo Shortcut.Save >> "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs"
del "%TEMP%\CreateShortcut.vbs"

if exist "%DESKTOP%\DeepResearch启动.lnk" (
    echo ✅ 快捷方式创建成功！
    echo.
    echo 📍 位置: %DESKTOP%\DeepResearch启动.lnk
    echo.
    echo 💡 使用方法:
    echo    1. 双击桌面上的 "DeepResearch启动" 快捷方式
    echo    2. 等待服务启动完成
    echo    3. 浏览器自动打开，开始使用
) else (
    echo ❌ 快捷方式创建失败
)

echo.
pause
