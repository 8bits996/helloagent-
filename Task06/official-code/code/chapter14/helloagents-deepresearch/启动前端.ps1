# DeepResearch 前端服务启动脚本

Write-Host "🌐 启动 DeepResearch 前端服务" -ForegroundColor Green
Write-Host ""

# 切换目录
Set-Location "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter14\helloagents-deepresearch\frontend"

Write-Host "📂 当前目录: $PWD" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 启动前端服务..." -ForegroundColor Yellow
Write-Host "   访问地址: http://localhost:5173 或 http://localhost:5174"
Write-Host "   按 Ctrl+C 停止服务"
Write-Host ""

# 启动服务
npm run dev
