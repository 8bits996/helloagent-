# ========================================
# HelloAgents 智能旅行助手 - 前端启动脚本
# ========================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  HelloAgents 智能旅行助手 - 前端  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 设置前端目录
$FrontendDir = "C:\Users\frankechen\CFP-Study\Task06\official-code\code\chapter13\helloagents-trip-planner\frontend"

# 检查目录是否存在
if (-not (Test-Path $FrontendDir)) {
    Write-Host "[错误] 前端目录不存在: $FrontendDir" -ForegroundColor Red
    Write-Host "请先运行环境配置脚本！" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 进入前端目录
Set-Location $FrontendDir
Write-Host "[1/4] 已进入目录: $FrontendDir" -ForegroundColor Green

# 检查 Node.js
Write-Host "[2/4] 检查 Node.js 环境..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if (-not $nodeVersion) {
    Write-Host "[错误] 未安装 Node.js！" -ForegroundColor Red
    Write-Host "请访问 https://nodejs.org/ 下载并安装 Node.js" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}
Write-Host "[成功] Node.js 版本: $nodeVersion" -ForegroundColor Green

# 检查 node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host "[提示] 依赖包未安装，正在安装..." -ForegroundColor Yellow
    Write-Host "[3/4] 正在安装 npm 依赖（首次运行可能需要几分钟）..." -ForegroundColor Yellow
    
    # 检查 npm 镜像源
    $registry = npm config get registry
    if ($registry -notlike "*npmmirror*" -and $registry -notlike "*taobao*") {
        Write-Host "[提示] 检测到使用官方 npm 源，可能较慢" -ForegroundColor Yellow
        $changeMirror = Read-Host "是否切换到国内镜像源？(y/n)"
        if ($changeMirror -eq "y") {
            npm config set registry https://registry.npmmirror.com
            Write-Host "[成功] 已切换到国内镜像源" -ForegroundColor Green
        }
    }
    
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 依赖安装失败！" -ForegroundColor Red
        Write-Host "请尝试以下命令手动安装：" -ForegroundColor Yellow
        Write-Host "  npm cache clean --force" -ForegroundColor White
        Write-Host "  npm install" -ForegroundColor White
        Read-Host "按 Enter 键退出"
        exit 1
    }
    
    Write-Host "[成功] 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "[3/4] npm 依赖包已安装" -ForegroundColor Green
}

# 检查 .env 文件
Write-Host "[4/4] 检查环境变量配置..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "[警告] 未找到 .env 文件！" -ForegroundColor Yellow
    Write-Host "正在创建 .env 文件..." -ForegroundColor Yellow
    
    # 创建默认配置
    @"
# 高德地图 Web 端 JavaScript API Key
VITE_AMAP_WEB_KEY=your-amap-javascript-api-key-here

# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
    
    Write-Host "[提示] 请编辑 .env 文件，填入您的高德地图 JavaScript API Key！" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "是否现在编辑 .env 文件？(y/n)"
    if ($continue -eq "y") {
        notepad .env
        Write-Host "编辑完成后，请保存并关闭记事本" -ForegroundColor Yellow
        Read-Host "按 Enter 键继续启动前端"
    }
}

# 读取 .env 文件并检查关键配置
$envContent = Get-Content .env -ErrorAction SilentlyContinue
$hasAmapKey = $envContent | Select-String -Pattern "VITE_AMAP_WEB_KEY=.+(?<!here)" -Quiet

if (-not $hasAmapKey) {
    Write-Host "[警告] VITE_AMAP_WEB_KEY 可能未配置！" -ForegroundColor Yellow
    Write-Host "[提示] 地图功能需要配置高德地图 JavaScript API Key" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "是否继续启动？(y/n)"
    if ($continue -ne "y") {
        exit 0
    }
} else {
    Write-Host "[成功] 高德地图 API Key 已配置" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  前端服务启动中...  " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "[重要] 请确保后端服务已启动！" -ForegroundColor Yellow
Write-Host "  后端地址: http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "前端访问地址:" -ForegroundColor Cyan
Write-Host "  - 本地: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host ""

# 启动 Vite 开发服务器
try {
    npm run dev
} catch {
    Write-Host ""
    Write-Host "[错误] 服务启动失败！" -ForegroundColor Red
    Write-Host "错误信息: $_" -ForegroundColor Red
    Read-Host "按 Enter 键退出"
    exit 1
}
