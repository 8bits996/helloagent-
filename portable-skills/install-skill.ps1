# AI Assisted Coding 技能安装脚本
# 使用方法: .\install-skill.ps1

$ErrorActionPreference = "Stop"

$SkillName = "ai-assisted-coding"
$RepoUrl = "https://git.woa.com/cloud-mt/ai-assisted-coding.git"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillDir = Join-Path $ScriptDir $SkillName
$GlobalSkillDir = Join-Path $env:USERPROFILE ".codebuddy\skills\$SkillName"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI Assisted Coding 技能安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已下载技能
if (-not (Test-Path (Join-Path $SkillDir "SKILL.md"))) {
    Write-Host "[步骤 1] 下载技能..." -ForegroundColor Yellow
    
    # 尝试克隆仓库
    if (Test-Path $SkillDir) {
        Remove-Item -Recurse -Force $SkillDir
    }
    
    try {
        Write-Host "正在从 $RepoUrl 克隆..." -ForegroundColor Gray
        git clone $RepoUrl $SkillDir
        Write-Host "克隆成功!" -ForegroundColor Green
    }
    catch {
        Write-Host "Git 克隆失败，请手动下载:" -ForegroundColor Red
        Write-Host "1. 访问 $RepoUrl" -ForegroundColor Yellow
        Write-Host "2. 登录 OA 账号后下载 ZIP" -ForegroundColor Yellow
        Write-Host "3. 解压到 $SkillDir" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "按任意键继续安装（假设你已手动下载）..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}
else {
    Write-Host "[步骤 1] 技能已下载，跳过..." -ForegroundColor Green
}

# 验证技能文件
if (-not (Test-Path (Join-Path $SkillDir "SKILL.md"))) {
    Write-Host "错误: 未找到 SKILL.md 文件，请确保技能已正确下载到 $SkillDir" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[步骤 2] 选择安装位置:" -ForegroundColor Yellow
Write-Host "  1. 全局安装 (所有项目可用): $GlobalSkillDir"
Write-Host "  2. 仅当前项目安装"
Write-Host "  3. 跳过安装（仅保留在当前目录）"
Write-Host ""
$choice = Read-Host "请选择 (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "正在安装到全局技能目录..." -ForegroundColor Yellow
        
        # 创建目标目录
        if (-not (Test-Path (Split-Path $GlobalSkillDir -Parent))) {
            New-Item -ItemType Directory -Path (Split-Path $GlobalSkillDir -Parent) -Force | Out-Null
        }
        
        # 复制文件
        if (Test-Path $GlobalSkillDir) {
            Remove-Item -Recurse -Force $GlobalSkillDir
        }
        Copy-Item -Recurse -Force $SkillDir $GlobalSkillDir
        
        Write-Host "安装完成! 技能已安装到: $GlobalSkillDir" -ForegroundColor Green
    }
    "2" {
        Write-Host ""
        $ProjectDir = Read-Host "请输入项目路径 (留空使用当前目录)"
        if ([string]::IsNullOrWhiteSpace($ProjectDir)) {
            $ProjectDir = Get-Location
        }
        $ProjectSkillDir = Join-Path $ProjectDir ".codebuddy\skills\$SkillName"
        
        Write-Host "正在安装到项目目录..." -ForegroundColor Yellow
        
        # 创建目标目录
        if (-not (Test-Path (Split-Path $ProjectSkillDir -Parent))) {
            New-Item -ItemType Directory -Path (Split-Path $ProjectSkillDir -Parent) -Force | Out-Null
        }
        
        # 复制文件
        if (Test-Path $ProjectSkillDir) {
            Remove-Item -Recurse -Force $ProjectSkillDir
        }
        Copy-Item -Recurse -Force $SkillDir $ProjectSkillDir
        
        Write-Host "安装完成! 技能已安装到: $ProjectSkillDir" -ForegroundColor Green
    }
    default {
        Write-Host "跳过安装，技能保留在: $SkillDir" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后续步骤:" -ForegroundColor Yellow
Write-Host "1. 重启 CodeBuddy 或刷新技能列表" -ForegroundColor Gray
Write-Host "2. 在对话中使用 /skills 查看已安装技能" -ForegroundColor Gray
Write-Host ""
Write-Host "分享给他人:" -ForegroundColor Yellow
Write-Host "将整个 $ScriptDir 文件夹打包分享即可" -ForegroundColor Gray
