# ========================================
# HelloAgents 智能旅行助手 - 后端启动脚本
# ========================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  HelloAgents 智能旅行助手 - 后端  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 设置后端目录
$BackendDir = "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter13\helloagents-trip-planner\backend"

# 检查目录是否存在
if (-not (Test-Path $BackendDir)) {
    Write-Host "[错误] 后端目录不存在: $BackendDir" -ForegroundColor Red
    Write-Host "请先运行环境配置脚本！" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 进入后端目录
Set-Location $BackendDir
Write-Host "[1/4] 已进入目录: $BackendDir" -ForegroundColor Green

# 检查虚拟环境
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[错误] Python 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "正在创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 虚拟环境创建失败！" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    
    Write-Host "[成功] 虚拟环境创建完成" -ForegroundColor Green
    
    # 激活虚拟环境
    Write-Host "[2/4] 正在激活虚拟环境..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    
    # 安装依赖
    Write-Host "[3/4] 正在安装依赖包（首次运行可能需要几分钟）..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败！" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    
    Write-Host "[成功] 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[2/4] 正在激活虚拟环境..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "[成功] 虚拟环境已激活" -ForegroundColor Green
}

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "[警告] 未找到 .env 文件！" -ForegroundColor Yellow
    Write-Host "正在复制 .env.example 到 .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "[提示] 请编辑 .env 文件，填入您的 API 密钥！" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "是否现在编辑 .env 文件？(y/n)"
    if ($continue -eq "y") {
        notepad .env
        Write-Host "编辑完成后，请保存并关闭记事本" -ForegroundColor Yellow
        Read-Host "按 Enter 键继续启动后端"
    }
}

Write-Host ""
Write-Host "[3/4] 检查环境变量配置..." -ForegroundColor Yellow

# 读取 .env 文件并检查关键配置
$envContent = Get-Content .env
$hasLLMKey = $envContent | Select-String -Pattern "LLM_API_KEY=sk-" -Quiet
$hasAmapKey = $envContent | Select-String -Pattern "AMAP_API_KEY=.+" -Quiet

if (-not $hasLLMKey) {
    Write-Host "[警告] LLM_API_KEY 可能未配置！" -ForegroundColor Yellow
}

if (-not $hasAmapKey) {
    Write-Host "[警告] AMAP_API_KEY 可能未配置！" -ForegroundColor Yellow
}

if ($hasLLMKey -and $hasAmapKey) {
    Write-Host "[成功] 必要的 API 密钥已配置" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[提示] 请确保 .env 文件中配置了以下内容：" -ForegroundColor Cyan
    Write-Host "  - LLM_API_KEY=sk-your-api-key" -ForegroundColor White
    Write-Host "  - AMAP_API_KEY=your-amap-key" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "是否继续启动？(y/n)"
    if ($continue -ne "y") {
        exit 0
    }
}

Write-Host ""
Write-Host "[4/4] 正在启动 FastAPI 后端服务..." -ForegroundColor Yellow
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  后端服务启动中...  " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址:" -ForegroundColor Cyan
Write-Host "  - API 文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - 健康检查: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动 FastAPI
try {
    uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host ""
    Write-Host "[错误] 服务启动失败！" -ForegroundColor Red
    Write-Host "错误信息: $_" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}
