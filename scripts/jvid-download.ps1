# JVID 媒體下載工具 - PowerShell 啟動腳本
# 使用方法: .\jvid-download.ps1 "https://www.jvid.com/v/PAGE_ID"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Url,
    
    [Parameter(Mandatory=$false)]
    [string]$Path,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoResume,
    
    [Parameter(Mandatory=$false)]
    [int]$Threads = 1,
    
    [Parameter(Mandatory=$false)]
    [switch]$Diagnostic
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  JVID 媒體下載工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 構建命令參數
$arguments = @("-u", $Url)

if ($Path) {
    $arguments += @("-p", $Path)
}

if ($AutoResume) {
    $arguments += "-a"
}

if ($Threads -gt 1) {
    $arguments += @("-n", $Threads)
}

if ($Diagnostic) {
    $arguments += "-d"
}

# 顯示配置
Write-Host "[配置]" -ForegroundColor Yellow
Write-Host "  URL: $Url"
if ($Path) { Write-Host "  保存路徑: $Path" }
Write-Host "  執行緒: $Threads"
Write-Host "  自動續傳: $(if ($AutoResume) { '是' } else { '否' })"
Write-Host "  診斷模式: $(if ($Diagnostic) { '是' } else { '否' })"
Write-Host ""

# 執行下載（使用專案入口點）
Write-Host "[開始下載]" -ForegroundColor Green
Write-Host ""

try {
    & uv run jvid-dl $arguments
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  下載完成！" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "  下載過程中發生錯誤 (退出碼: $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  執行錯誤: $_" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
