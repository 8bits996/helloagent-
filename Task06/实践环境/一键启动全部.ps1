# ========================================
# HelloAgents 智能旅行助手 - 一键启动脚本
# ========================================

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   HelloAgents 智能旅行助手   " -ForegroundColor Cyan
Write-Host "     一键启动完整服务     " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 检查脚本是否存在
$BackendScript = Join-Path $ScriptDir "启动后端.ps1"
$FrontendScript = Join-Path $ScriptDir "启动前端.ps1"

if (-not (Test-Path $BackendScript) -or -not (Test-Path $FrontendScript)) {
    Write-Host "[错误] 启动脚本不完整！" -ForegroundColor Red
    Write-Host "请确保以下文件存在：" -ForegroundColor Yellow
    Write-Host "  - 启动后端.ps1" -ForegroundColor White
    Write-Host "  - 启动前端.ps1" -ForegroundColor White
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host "[提示] 此脚本将在两个新窗口中分别启动后端和前端服务" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务信息：" -ForegroundColor Yellow
Write-Host "  - 后端: http://localhost:8000" -ForegroundColor White
Write-Host "  - 前端: http://localhost:5173" -ForegroundColor White
Write-Host "  - API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

# 询问是否继续
$continue = Read-Host "是否继续？(y/n)"
if ($continue -ne "y") {
    Write-Host "已取消启动" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[1/2] 正在启动后端服务..." -ForegroundColor Green

# 启动后端（新窗口）
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$BackendScript`""

# 等待3秒，让后端有时间启动
Write-Host "[提示] 等待后端服务初始化（3秒）..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "[2/2] 正在启动前端服务..." -ForegroundColor Green

# 启动前端（新窗口）
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$FrontendScript`""

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "       服务启动完成！        " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "已在两个新窗口中启动服务：" -ForegroundColor Cyan
Write-Host "  1. 后端服务 (端口 8000)" -ForegroundColor White
Write-Host "  2. 前端服务 (端口 5173)" -ForegroundColor White
Write-Host ""
Write-Host "快速访问：" -ForegroundColor Yellow
Write-Host "  - 旅行助手首页: http://localhost:5173" -ForegroundColor White
Write-Host "  - API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "提示：" -ForegroundColor Cyan
Write-Host "  - 在各自的窗口中按 Ctrl+C 可以停止对应服务" -ForegroundColor White
Write-Host "  - 关闭窗口也会停止服务" -ForegroundColor White
Write-Host ""

# 等待用户操作
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "服务运行中，请勿关闭此窗口" -ForegroundColor Yellow
Write-Host ""
Write-Host "按任意键打开浏览器访问前端页面..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 打开浏览器
Write-Host ""
Write-Host "[提示] 正在打开浏览器..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "已打开浏览器，开始使用吧！" -ForegroundColor Green
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "          使用提示          " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 在首页填写旅行信息" -ForegroundColor White
Write-Host "2. 点击'生成旅行计划'按钮" -ForegroundColor White
Write-Host "3. 等待 AI 生成个性化行程" -ForegroundColor White
Write-Host "4. 查看详细的景点、路线和天气信息" -ForegroundColor White
Write-Host ""
Write-Host "遇到问题？" -ForegroundColor Yellow
Write-Host "  - 查看后端窗口的日志信息" -ForegroundColor White
Write-Host "  - 访问 API 文档查看接口状态" -ForegroundColor White
Write-Host "  - 查看环境配置指南排查问题" -ForegroundColor White
Write-Host ""
Write-Host "按 Enter 键关闭此窗口（不影响服务运行）" -ForegroundColor Cyan
Read-Host ""
