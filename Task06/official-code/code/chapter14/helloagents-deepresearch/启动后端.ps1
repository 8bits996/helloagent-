# DeepResearch Agent - 后端启动脚本
# 创建日期: 2025-12-26

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DeepResearch Agent - 后端服务启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到后端目录
$backendDir = Split-Path $MyInvocation.MyCommand.Path
Set-Location $backendDir\backend

Write-Host "[1/3] 检查环境配置..." -ForegroundColor Yellow

# 检查 .env 文件
if (-Not (Test-Path ".env")) {
    Write-Host "❌ 错误: .env 文件不存在！" -ForegroundColor Red
    Write-Host "请复制 .env.example 并配置 API 密钥" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✓ 环境配置文件存在" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] 启动 FastAPI 服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "后端服务运行信息:" -ForegroundColor Cyan
Write-Host "  - API 地址: http://localhost:8000" -ForegroundColor White
Write-Host "  - API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - 搜索引擎: DuckDuckGo (免费)" -ForegroundColor White
Write-Host "  - LLM 模型: Qwen/Qwen2.5-7B-Instruct" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 启动服务
python src\main.py
