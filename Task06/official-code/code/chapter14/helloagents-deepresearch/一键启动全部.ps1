# DeepResearch Agent - 一键启动全部服务
# 创建日期: 2025-12-26

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DeepResearch Agent - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectDir = Split-Path $MyInvocation.MyCommand.Path

Write-Host "此脚本将启动:" -ForegroundColor Yellow
Write-Host "  1. 后端服务 (FastAPI) - http://localhost:8000" -ForegroundColor White
Write-Host "  2. 前端服务 (Vue3) - http://localhost:5174" -ForegroundColor White
Write-Host ""
Write-Host "两个服务将在独立的终端窗口中运行" -ForegroundColor Cyan
Write-Host ""

# 启动后端
Write-Host "[1/2] 启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$projectDir\启动后端.ps1"
Write-Host "✓ 后端服务已在新窗口启动" -ForegroundColor Green
Write-Host "   等待 5 秒让后端完全启动..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 启动前端
Write-Host ""
Write-Host "[2/2] 启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-File", "$projectDir\启动前端.ps1"
Write-Host "✓ 前端服务已在新窗口启动" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ 所有服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  前端界面: http://localhost:5174" -ForegroundColor White
Write-Host "  后端 API: http://localhost:8000" -ForegroundColor White
Write-Host "  API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "  - 两个服务在独立窗口运行" -ForegroundColor Gray
Write-Host "  - 关闭窗口即可停止对应服务" -ForegroundColor Gray
Write-Host "  - 或按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

pause
