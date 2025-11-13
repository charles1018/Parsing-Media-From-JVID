#!/usr/bin/env pwsh
# JVID Docker 下載便利腳本 (PowerShell)

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Url,

    [Parameter(Mandatory=$false)]
    [int]$Threads,

    [Parameter(Mandatory=$false)]
    [switch]$AutoResume,

    [Parameter(Mandatory=$false)]
    [switch]$Diagnostic
)

# 建構參數
$args_list = @("-u", $Url)

if ($Threads) {
    $args_list += @("-n", $Threads)
}

if ($AutoResume) {
    $args_list += "-a"
}

if ($Diagnostic) {
    $args_list += "-d"
}

# 執行 Docker Compose
Write-Host "開始下載: $Url" -ForegroundColor Green
Write-Host "執行命令: docker compose run --rm jvid-dl $($args_list -join ' ')" -ForegroundColor Cyan

docker compose run --rm jvid-dl @args_list
