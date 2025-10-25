#!/bin/bash
# JVID 媒體下載工具 - Bash 啟動腳本
# 使用方法: ./jvid-download.sh "https://www.jvid.com/v/PAGE_ID"

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 顯示標題
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  JVID 媒體下載工具${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# 檢查參數
if [ -z "$1" ]; then
    echo -e "${RED}[錯誤] 請提供 JVID URL${NC}"
    echo ""
    echo "使用方法:"
    echo "  ./jvid-download.sh \"https://www.jvid.com/v/PAGE_ID\" [選項]"
    echo ""
    echo "可選參數:"
    echo "  -p PATH       指定保存路徑"
    echo "  -a            啟用自動續傳"
    echo "  -n NUMBER     指定執行緒數量"
    echo "  -d            啟用診斷模式"
    echo ""
    echo "範例:"
    echo "  ./jvid-download.sh \"https://www.jvid.com/v/12345\""
    echo "  ./jvid-download.sh \"https://www.jvid.com/v/12345\" -p downloads -a"
    echo "  ./jvid-download.sh \"https://www.jvid.com/v/12345\" -n 3 -a"
    exit 1
fi

# 顯示下載信息
echo -e "${GREEN}[開始下載]${NC} $1"
echo ""

# 執行下載（使用專案入口點）
uv run jvid-dl -u "$@"

# 檢查執行結果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  下載完成！${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}  下載過程中發生錯誤${NC}"
    echo -e "${RED}========================================${NC}"
    exit $?
fi
