# Pagefile Configuration Script
# Requires Administrator privileges

# Check admin rights
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Pagefile Configuration Tool" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Show current config
Write-Host "Current Configuration:" -ForegroundColor Yellow
$current = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='d:\\pagefile.sys'"
if ($current) {
    Write-Host "  Location: $($current.Name)" -ForegroundColor White
    Write-Host "  Initial Size: $($current.InitialSize) MB" -ForegroundColor White
    Write-Host "  Maximum Size: $($current.MaximumSize) MB" -ForegroundColor White
}
Write-Host ""

# Show physical memory
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$physicalMemory = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
Write-Host "Physical Memory: $physicalMemory GB" -ForegroundColor Green
Write-Host ""

# Apply new settings
Write-Host "Applying new configuration..." -ForegroundColor Yellow

try {
    $pagefile = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name='d:\\pagefile.sys'"
    
    if ($pagefile) {
        $pagefile.InitialSize = 16384
        $pagefile.MaximumSize = 32768
        Set-CimInstance -InputObject $pagefile
        
        Write-Host ""
        Write-Host "Success! New settings:" -ForegroundColor Green
        Write-Host "  Initial Size: 16384 MB (16 GB)" -ForegroundColor Cyan
        Write-Host "  Maximum Size: 32768 MB (32 GB)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "======================================" -ForegroundColor Yellow
        Write-Host "  RESTART REQUIRED!" -ForegroundColor Yellow
        Write-Host "======================================" -ForegroundColor Yellow
        Write-Host ""
        
        $restart = Read-Host "Restart now? (Y/N)"
        if ($restart -eq 'Y' -or $restart -eq 'y') {
            Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
            shutdown /r /t 10
        } else {
            Write-Host "Please restart manually to apply changes" -ForegroundColor Cyan
        }
    } else {
        Write-Host "Error: D:\pagefile.sys not found" -ForegroundColor Red
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Yellow
    Write-Host "1. Right-click 'This PC' > Properties > Advanced system settings" -ForegroundColor White
    Write-Host "2. Performance > Settings > Advanced > Virtual memory > Change" -ForegroundColor White
    Write-Host "3. Uncheck 'Automatically manage paging file size'" -ForegroundColor White
    Write-Host "4. Select D: drive" -ForegroundColor White
    Write-Host "5. Select 'Custom size':" -ForegroundColor White
    Write-Host "   Initial: 16384" -ForegroundColor Cyan
    Write-Host "   Maximum: 32768" -ForegroundColor Cyan
    Write-Host "6. Set > OK > Restart" -ForegroundColor White
}

Write-Host ""
Read-Host "Press Enter to exit"
