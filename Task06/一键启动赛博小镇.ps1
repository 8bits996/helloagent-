# 赛博小镇 - 一键启动脚本
# 创建日期: 2025-12-27
# 功能: 自动启动后端服务和 Godot 编辑器

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "    赛博小镇 - 一键启动" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 配置路径
$backendPath = "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter15\Helloagents-AI-Town\backend"
$godotPath = "C:\Godot\Godot_v4.3-stable_win64.exe"
$projectPath = "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter15\Helloagents-AI-Town\helloagents-ai-town\project.godot"

# 检查 Godot 是否已安装
Write-Host "[检查] Godot 安装状态..." -ForegroundColor Yellow
if (-Not (Test-Path $godotPath)) {
    Write-Host "[错误] Godot 未安装!" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先运行下载脚本:" -ForegroundColor Yellow
    Write-Host "  C:\Godot\下载Godot.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "或手动下载:" -ForegroundColor Yellow
    Write-Host "  https://godotengine.org/download/windows/" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}
Write-Host "[✓] Godot 已安装" -ForegroundColor Green
Write-Host ""

# 检查后端环境
Write-Host "[检查] 后端环境..." -ForegroundColor Yellow
if (-Not (Test-Path "$backendPath\venv")) {
    Write-Host "[错误] 后端虚拟环境不存在!" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先配置后端环境:" -ForegroundColor Yellow
    Write-Host "  cd $backendPath" -ForegroundColor Cyan
    Write-Host "  python -m venv venv" -ForegroundColor Cyan
    Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}
Write-Host "[✓] 后端环境已配置" -ForegroundColor Green
Write-Host ""

# 检查 .env 文件
Write-Host "[检查] .env 配置..." -ForegroundColor Yellow
if (-Not (Test-Path "$backendPath\.env")) {
    Write-Host "[警告] .env 文件不存在，将使用默认配置" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[✓] .env 配置已存在" -ForegroundColor Green
    Write-Host ""
}

# 启动后端服务
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "[1/2] 启动后端服务" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端将在新窗口中启动..." -ForegroundColor Yellow
Write-Host "请不要关闭后端窗口!" -ForegroundColor Red
Write-Host ""

# 创建后端启动脚本
$backendScript = @"
Set-Location '$backendPath'
& '.\venv\Scripts\Activate.ps1'
Write-Host '后端服务启动中...' -ForegroundColor Green
python main.py
"@

# 保存临时脚本
$tempScript = "$env:TEMP\start-backend.ps1"
$backendScript | Out-File -FilePath $tempScript -Encoding UTF8

# 在新窗口启动后端
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $tempScript

Write-Host "[✓] 后端服务已在新窗口启动" -ForegroundColor Green
Write-Host ""
Write-Host "等待后端服务初始化 (10秒)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 测试后端连接
Write-Host "测试后端连接..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -UseBasicParsing
    Write-Host "[✓] 后端服务运行正常" -ForegroundColor Green
} catch {
    Write-Host "[警告] 后端连接测试失败，但继续启动 Godot" -ForegroundColor Yellow
    Write-Host "如果游戏无法对话，请检查后端窗口的错误信息" -ForegroundColor Yellow
}
Write-Host ""

# 启动 Godot
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "[2/2] 启动 Godot 编辑器" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Godot 编辑器启动中..." -ForegroundColor Yellow
Write-Host ""

Start-Process $godotPath -ArgumentList "--path", (Split-Path $projectPath)

Write-Host "[✓] Godot 编辑器已启动" -ForegroundColor Green
Write-Host ""

# 完成提示
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "    启动完成！" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 在 Godot 编辑器中，点击右上角的 [运行] 按钮 (或按 F5)" -ForegroundColor Cyan
Write-Host "  2. 如果是首次运行，选择 scenes/main.tscn 作为主场景" -ForegroundColor Cyan
Write-Host "  3. 享受游戏！" -ForegroundColor Cyan
Write-Host ""
Write-Host "游戏控制:" -ForegroundColor Yellow
Write-Host "  WASD  - 移动玩家" -ForegroundColor Cyan
Write-Host "  E     - 与 NPC 交互" -ForegroundColor Cyan
Write-Host "  Enter - 发送消息" -ForegroundColor Cyan
Write-Host "  ESC   - 关闭对话框" -ForegroundColor Cyan
Write-Host ""
Write-Host "重要提示:" -ForegroundColor Red
Write-Host "  - 不要关闭后端服务窗口" -ForegroundColor Red
Write-Host "  - 如果对话失败，检查后端窗口的错误信息" -ForegroundColor Red
Write-Host ""
Write-Host "API 文档: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

Read-Host "按任意键退出本窗口（不影响后端和 Godot 运行）"
