@echo off
REM JVID 媒體下載工具 - Windows 啟動腳本
REM 使用方法: jvid-download.bat "https://www.jvid.com/v/PAGE_ID"

setlocal enabledelayedexpansion

echo ========================================
echo   JVID 媒體下載工具
echo ========================================
echo.

REM 檢查是否提供了 URL 參數
if "%~1"=="" (
    echo [錯誤] 請提供 JVID URL
    echo.
    echo 使用方法:
    echo   jvid-download.bat "https://www.jvid.com/v/PAGE_ID"
    echo.
    echo 可選參數:
    echo   -p PATH       指定保存路徑
    echo   -a            啟用自動續傳
    echo   -n NUMBER     指定執行緒數量
    echo   -d            啟用診斷模式
    echo.
    echo 範例:
    echo   jvid-download.bat "https://www.jvid.com/v/12345"
    echo   jvid-download.bat "https://www.jvid.com/v/12345" -p downloads -a
    echo   jvid-download.bat "https://www.jvid.com/v/12345" -n 3 -a
    exit /b 1
)

REM 執行下載（使用專案入口點）
echo [開始下載] %~1
echo.

uv run jvid-dl -u %*

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   下載完成！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   下載過程中發生錯誤
    echo ========================================
    exit /b %errorlevel%
)

endlocal
