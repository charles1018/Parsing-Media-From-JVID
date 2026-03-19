# JVID 媒體下載工具 🎬

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/badge/uv-package%20manager-green.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一個高效、易用的 JVID 媒體下載工具，支援影片和圖片的自動下載。使用 **uv** 進行套件管理，提供完全隔離的執行環境。

## ✨ 功能特點

- 🎯 智能偵測頁面中的影片和圖片內容
- 📦 自動下載所有可用的影片版本
- 🔐 從 `cookies.json` 或 `cookies.txt` (Netscape 格式) 自動讀取認證資訊
- 🔄 支援中斷後自動恢復下載 (實驗性功能)
- 🧵 支援多執行緒下載（1-16 個執行緒，執行緒安全）
- 🔍 詳細診斷功能幫助解決解析問題
- ⚡ 使用 uv 進行依賴管理，安裝速度快 10-100 倍
- 🛠️ 模組化架構，易於維護和擴展
- 🌐 **全新 Web UI** - Gradio 網頁介面，適合不熟悉命令列的使用者

## 📋 系統需求

- **Python**: 3.8 或更高版本
- **uv**: 已安裝（透過 scoop 或其他方式）
- **作業系統**: Windows / macOS / Linux
- **FFmpeg**: 用於影片處理（可選）

## 🚀 快速開始

### 1. 安裝

```bash
git clone https://github.com/charles1018/Parsing-Media-From-JVID.git
cd Parsing-Media-From-JVID
uv sync
```

### 2. 準備 Cookies

使用瀏覽器擴充套件（如 EditThisCookie）導出 JVID cookies，保存為 `www.jvid.com_cookies.json` 或 `cookies.txt` (Netscape 格式) 放在專案根目錄。

詳細步驟請參閱 [使用者指南](docs/USER_GUIDE.md#-準備-cookies)

### 3. 開始下載

**命令列方式：**
```bash
uv run jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]"
```

**Web UI 方式（推薦新手）：**
```bash
uv run jvid-webui
```
啟動後會自動開啟瀏覽器，在網頁介面中輸入網址即可下載。

## 🐳 Docker 部署（推薦）

支援使用 Docker 進行一鍵部署，無需配置 Python 環境！

### 快速開始

```bash
# 1. 建構映像
docker compose build

# 2. 執行下載（使用便利腳本）
./scripts/docker-download.sh "https://www.jvid.com/v/[PAGE_ID]"

# 或使用 docker compose 命令
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]"
```

**便利腳本：**
```bash
# macOS/Linux/Git Bash
./scripts/docker-download.sh "URL" -n 3 -a

# Windows PowerShell
.\scripts\docker-download.ps1 -Url "URL" -Threads 3 -AutoResume
```

**優勢：**
- ✅ 環境隔離，無依賴衝突
- ✅ 跨平台一致性
- ✅ 一鍵部署，快速上手
- ✅ 便利腳本簡化命令

**詳細說明請參閱：** [DOCKER.md](docs/DOCKER.md)

---

## 📖 完整文檔

| 文檔 | 說明 | 連結 |
|------|------|------|
| 🐳 Docker 部署 | Docker 容器化部署完整指南 | [DOCKER.md](docs/DOCKER.md) |
| 📘 使用者指南 | 詳細使用說明、FAQ、批次下載 | [USER_GUIDE.md](docs/USER_GUIDE.md) |
| 🔧 開發者指南 | 開發環境、專案結構、貢獻指南 | [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) |
| 📝 變更日誌 | 版本歷史和更新記錄 | [CHANGELOG.md](CHANGELOG.md) |

## 📊 基本命令

| 功能 | 命令 | 說明 |
|------|------|------|
| 🌐 Web UI | `uv run jvid-webui` | 網頁介面（推薦新手） |
| 標準下載 | `uv run jvid-dl -u "URL"` | |
| 自動續傳 | `uv run jvid-dl -u "URL" -a` | 實驗性功能 |
| 指定路徑 | `uv run jvid-dl -u "URL" -p "路徑"` | |
| 多執行緒 | `uv run jvid-dl -u "URL" -n 3` | |
| 診斷模式 | `uv run jvid-dl -u "URL" -d` | |

**可用的入口點別名：**
- `jvid-dl` (推薦)
- `jvid`
- `jvid-download`
- `jvid-webui` (Web UI)

**便捷腳本：**
- Windows: `scripts/jvid-download.bat` 或 `scripts/jvid-download.ps1`
- macOS/Linux: `scripts/jvid-download.sh`

## 🎯 使用範例

### 基本下載
```bash
uv run jvid-dl -u "https://www.jvid.com/v/12345"
```

### 自動續傳下載
```bash
uv run jvid-dl -u "https://www.jvid.com/v/12345" -a
```

### 多執行緒下載
```bash
uv run jvid-dl -u "https://www.jvid.com/v/12345" -n 3 -a
```

### 使用便捷腳本
```bash
# Windows
.\scripts\jvid-download.ps1 -Url "https://www.jvid.com/v/12345" -AutoResume

# macOS/Linux
./scripts/jvid-download.sh "https://www.jvid.com/v/12345"
```

更多使用情境請參閱 [使用者指南](docs/USER_GUIDE.md#-使用情境)

## 🔧 專案結構

```
Parsing-Media-From-JVID/
├── Entry.py                      # 命令列主程式入口
├── WebUI.py                      # Gradio Web UI 入口
├── pyproject.toml                # uv 專案配置（含 ruff 設定）
├── package/                      # 主要功能包
│   ├── ParsingMediaLogic.py      # 核心解析邏輯
│   ├── ArgumentParser.py         # 命令列參數解析
│   ├── DiagnosticMode.py         # 診斷模式實現
│   ├── processors/               # 媒體處理器
│   │   ├── BaseProcessor.py      # 處理器基礎類別
│   │   ├── VideoProcessor.py     # 影片下載處理
│   │   └── ImageProcessor.py     # 圖片下載處理
│   ├── network/                  # 網路相關模組
│   │   └── NetworkManager.py     # HTTP 請求管理
│   └── utils/                    # 工具模組
│       ├── CookieManager.py      # Cookie 自動管理（支援 JSON 及 Netscape 格式）
│       ├── ContentDetector.py    # 內容類型偵測
│       └── ProgressManager.py    # 下載進度管理
├── scripts/                      # 執行腳本
│   ├── docker-download.*         # Docker 便利腳本
│   └── jvid-download.*           # 本地執行腳本
└── tests/                        # 測試檔案
    ├── test_cookie_manager.py    # Cookie 測試
    └── test_path_fix.py          # 路徑處理測試
```

詳細結構說明請參閱 [開發者指南](docs/DEVELOPER_GUIDE.md#-專案結構)

## 🤝 貢獻

歡迎提交 Pull Request 或 Issue！

開發環境設置和貢獻指南請參閱 [開發者指南](docs/DEVELOPER_GUIDE.md#-開發環境設置)

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

---

**注意**: 使用時請遵守 JVID 使用條款，僅供個人學習研究使用。
