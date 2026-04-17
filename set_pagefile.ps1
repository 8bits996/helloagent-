# 设置页面文件大小脚本
# 需要管理员权限运行

Write-Host "正在修改页面文件设置..." -ForegroundColor Yellow

try {
    # 获取当前页面文件设置
    $pagefile = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='d:\\pagefile.sys'"
    
    if ($pagefile) {
        # 修改页面文件大小
        $pagefile.InitialSize = 16384  # 16 GB
        $pagefile.MaximumSize = 32768  # 32 GB
        Set-CimInstance -InputObject $pagefile
        
        Write-Host "✓ 页面文件设置成功！" -ForegroundColor Green
        Write-Host "  位置: D:\pagefile.sys" -ForegroundColor Cyan
        Write-Host "  初始大小: 16384 MB (16 GB)" -ForegroundColor Cyan
        Write-Host "  最大大小: 32768 MB (32 GB)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⚠ 重启电脑后生效！" -ForegroundColor Yellow
        
        # 验证设置
        Write-Host ""
        Write-Host "验证新设置..." -ForegroundColor Yellow
        $newConfig = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='d:\\pagefile.sys'"
        Write-Host "  InitialSize: $($newConfig.InitialSize) MB" -ForegroundColor Cyan
        Write-Host "  MaximumSize: $($newConfig.MaximumSize) MB" -ForegroundColor Cyan
    } else {
        Write-Host "✗ 未找到 D:\pagefile.sys 设置" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ 设置失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请以管理员身份运行此脚本" -ForegroundColor Yellow
}
