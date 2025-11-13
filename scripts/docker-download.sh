#!/bin/bash
# JVID Docker 下載便利腳本 (Bash)

# 顏色輸出
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 使用說明
usage() {
    echo "使用方式: $0 <URL> [選項]"
    echo ""
    echo "必要參數:"
    echo "  URL                  JVID 影片網址"
    echo ""
    echo "可選參數:"
    echo "  -n, --threads NUM    指定執行緒數量"
    echo "  -a, --auto-resume    自動續傳"
    echo "  -d, --diagnostic     啟用診斷模式"
    echo "  -h, --help           顯示此說明"
    echo ""
    echo "範例:"
    echo "  $0 'https://www.jvid.com/v/12345'"
    echo "  $0 'https://www.jvid.com/v/12345' -n 3 -a"
    exit 1
}

# 檢查參數
if [ $# -eq 0 ]; then
    usage
fi

# 檢查是否是 help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    usage
fi

# 解析參數
URL="$1"
shift

DOCKER_ARGS="-u $URL"

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--threads)
            DOCKER_ARGS="$DOCKER_ARGS -n $2"
            shift 2
            ;;
        -a|--auto-resume)
            DOCKER_ARGS="$DOCKER_ARGS -a"
            shift
            ;;
        -d|--diagnostic)
            DOCKER_ARGS="$DOCKER_ARGS -d"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "未知參數: $1"
            usage
            ;;
    esac
done

# 執行 Docker Compose
echo -e "${GREEN}開始下載: $URL${NC}"
echo -e "${CYAN}執行命令: docker compose run --rm jvid-dl $DOCKER_ARGS${NC}"
echo ""

docker compose run --rm jvid-dl $DOCKER_ARGS
