# ============================================
# 重启 HelloAgents 智能旅行助手服务
# ============================================

Write-Host "🔄 正在重启服务..." -ForegroundColor Cyan

# 停止所有现有的服务进程
Write-Host "`n📛 停止现有服务..." -ForegroundColor Yellow

# 查找并停止 uvicorn 进程（后端）
$backendProcesses = Get-Process | Where-Object { $_.Path -like "*helloagents-trip-planner*" -and $_.ProcessName -eq "python" }
if ($backendProcesses) {
    $backendProcesses | ForEach-Object {
        Write-Host "  - 停止后端进程 (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}

# 查找并停止 vite 进程（前端）
$frontendProcesses = Get-Process | Where-Object { $_.ProcessName -like "*node*" -and $_.Path -like "*helloagents-trip-planner*" }
if ($frontendProcesses) {
    $frontendProcesses | ForEach-Object {
        Write-Host "  - 停止前端进程 (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 2

# 项目路径
$projectRoot = "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter13\helloagents-trip-planner"
$backendPath = Join-Path $projectRoot "backend"
$frontendPath = Join-Path $projectRoot "frontend"

Write-Host "`n🚀 启动后端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '后端服务启动中...' -ForegroundColor Cyan; .\venv\Scripts\python.exe -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "⏳ 等待后端启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n🚀 启动前端服务..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '前端服务启动中...' -ForegroundColor Cyan; npm run dev"

Write-Host "⏳ 等待前端启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "`n🌐 打开浏览器..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host "`n✅ 服务重启完成！" -ForegroundColor Green
Write-Host "`n📊 服务状态:" -ForegroundColor Cyan
Write-Host "  - 后端: http://localhost:8000" -ForegroundColor White
Write-Host "  - 前端: http://localhost:5173" -ForegroundColor White
Write-Host "  - API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "`n💡 提示: 查看新打开的两个PowerShell窗口来监控服务日志" -ForegroundColor Yellow
