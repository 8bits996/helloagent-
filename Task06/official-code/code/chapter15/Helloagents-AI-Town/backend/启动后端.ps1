# 赛博小镇 - 后端服务启动脚本
# 创建日期: 2025-12-27

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "    赛博小镇 - 后端服务启动" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-Not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[错误] 虚拟环境不存在，请先运行: python -m venv venv" -ForegroundColor Red
    Write-Host ""
    Read-Host "按任意键退出"
    exit 1
}

# 检查 .env 文件
if (-Not (Test-Path ".\.env")) {
    Write-Host "[警告] .env 文件不存在" -ForegroundColor Yellow
    Write-Host "将使用默认配置或环境变量" -ForegroundColor Yellow
    Write-Host ""
}

# 激活虚拟环境
Write-Host "[1/2] 激活虚拟环境..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# 启动服务
Write-Host "[2/2] 启动 FastAPI 服务..." -ForegroundColor Green
Write-Host ""
Write-Host "提示: 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

python main.py

# 服务停止后
Write-Host ""
Write-Host "服务已停止" -ForegroundColor Yellow
Read-Host "按任意键退出"
