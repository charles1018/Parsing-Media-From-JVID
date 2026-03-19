# 🐳 Docker 部署指南

本文檔說明如何使用 Docker 部署和執行 JVID 媒體下載工具。

## 📋 目錄

- [系統需求](#系統需求)
- [快速開始](#快速開始)
- [詳細說明](#詳細說明)
- [使用方式](#使用方式)
- [進階配置](#進階配置)
- [故障排除](#故障排除)

---

## 🔧 系統需求

### 必需

- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本（可選，但推薦）
- **作業系統**: Windows 10/11, macOS, Linux

### 檢查安裝

```bash
# 檢查 Docker 版本
docker --version

# 檢查 Docker Compose 版本
docker compose version
```

---

## 🚀 快速開始

### 1. 準備 Cookie 檔案

將 Cookie 檔案放在專案根目錄，支援以下檔名（自動搜尋）：
- `www.jvid.com_cookies.json`（推薦）
- `jvid_cookies.json`
- `cookies.json`
- `cookies.txt`（Netscape HTTP Cookie File 格式）

### 2. 建構映像

```bash
# 使用 Docker Compose（推薦）
docker compose build

# 或使用 Docker 命令
docker build -t jvid-dl:latest .
```

### 3. 執行下載

```bash
# 使用 Docker Compose
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]"

# 或使用 Docker 命令
docker run --rm \
  -v "$(pwd)/www.jvid.com_cookies.json:/app/cookies/www.jvid.com_cookies.json:ro" \
  -v "$(pwd)/media:/app/media" \
  jvid-dl:latest -u "https://www.jvid.com/v/[PAGE_ID]"
```

---

## 📖 詳細說明

### Docker 映像結構

本專案使用**多階段建構**來優化映像大小：

1. **Builder 階段**: 安裝 uv 和專案依賴
2. **Runtime 階段**: 只複製必要的檔案和執行環境

### 映像特點

- ✅ 基於 `python:3.11-slim`（最小化系統）
- ✅ 整合 `uv` 套件管理工具
- ✅ 非 root 使用者執行（安全性）
- ✅ 健康檢查配置
- ✅ 優化的分層快取

### Volume 掛載

容器需要兩個 Volume：

| Volume | 用途 | 權限 | 說明 |
|--------|------|------|------|
| `/app/cookies` | 存放 Cookie 檔案 | 只讀 (ro) | 認證資訊，不應被修改 |
| `/app/media` | 下載目錄 | 讀寫 (rw) | 儲存下載的影片和圖片 |

---

## 🎯 使用方式

### 基本命令

#### 1. 查看說明

```bash
docker compose run --rm jvid-dl --help
```

#### 2. 標準下載

```bash
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]"
```

#### 3. 自動續傳下載

```bash
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]" -a
```

#### 4. 多執行緒下載

```bash
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]" -n 3 -a
```

#### 5. 診斷模式

```bash
docker compose run --rm jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]" -d
```

#### 6. 指定下載路徑（容器內）

```bash
docker compose run --rm jvid-dl \
  -u "https://www.jvid.com/v/[PAGE_ID]" \
  -p "/app/media/custom_folder"
```

### Windows 使用範例

```powershell
# PowerShell
docker compose run --rm jvid-dl `
  -u "https://www.jvid.com/v/12345" `
  -a -n 3
```

### macOS/Linux 使用範例

```bash
# Bash/Zsh
docker compose run --rm jvid-dl \
  -u "https://www.jvid.com/v/12345" \
  -a -n 3
```

### 便利腳本（推薦）

專案提供了簡化的便利腳本，無需記住長命令：

#### Windows PowerShell

```powershell
# 基本使用
.\scripts\docker-download.ps1 -Url "https://www.jvid.com/v/12345"

# 多執行緒 + 自動續傳
.\scripts\docker-download.ps1 -Url "https://www.jvid.com/v/12345" -Threads 3 -AutoResume

# 診斷模式
.\scripts\docker-download.ps1 -Url "https://www.jvid.com/v/12345" -Diagnostic
```

#### macOS/Linux/Git Bash

```bash
# 查看說明
./scripts/docker-download.sh --help

# 基本使用
./scripts/docker-download.sh "https://www.jvid.com/v/12345"

# 多執行緒 + 自動續傳
./scripts/docker-download.sh "https://www.jvid.com/v/12345" -n 3 -a

# 診斷模式
./scripts/docker-download.sh "https://www.jvid.com/v/12345" -d
```

**優點：**
- ✅ 簡化命令，易於使用
- ✅ 參數驗證，減少錯誤
- ✅ 清晰的輸出訊息
- ✅ 跨平台支援

---

## ⚙️ 進階配置

### 自訂環境變數

編輯 `.env` 檔案來設定預設行為：

```bash
# 複製範例檔案
cp .env.example .env

# 編輯配置
nano .env  # 或使用你喜歡的編輯器
```

**支援的環境變數：**

| 變數 | 說明 | 預設值 | 範例 |
|------|------|--------|------|
| `DEFAULT_THREADS` | 預設執行緒數量 | `1` | `3` |
| `AUTO_RESUME` | 預設啟用自動續傳 | `false` | `true` |

**範例 `.env` 配置：**

```bash
# 使用 3 個執行緒
DEFAULT_THREADS=3

# 預設啟用自動續傳
AUTO_RESUME=true
```

**注意：**
- 環境變數設定預設行為
- 命令列參數優先級高於環境變數
- 修改後需重新啟動容器才能生效

### 使用不同的 Cookie 檔案

容器會自動搜尋以下檔名，無需修改配置：
- `www.jvid.com_cookies.json`
- `jvid_cookies.json`
- `cookies.json`
- `cookies.txt`（Netscape HTTP Cookie File 格式）

只需將 Cookie 檔案放在專案根目錄即可。

### 資源限制

修改 `docker-compose.yml` 中的資源配置：

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # CPU 核心數上限
      memory: 4G       # 記憶體上限
    reservations:
      cpus: '1.0'      # 保證的 CPU 核心數
      memory: 1G       # 保證的記憶體
```

### 批次下載

建立一個包含多個 URL 的 shell 腳本：

```bash
#!/bin/bash
# batch_download.sh

urls=(
  "https://www.jvid.com/v/12345"
  "https://www.jvid.com/v/12346"
  "https://www.jvid.com/v/12347"
)

for url in "${urls[@]}"; do
  echo "下載: $url"
  # 使用便利腳本
  ./scripts/docker-download.sh "$url" -a
  # 或使用 docker compose 命令
  # docker compose run --rm jvid-dl -u "$url" -a
  echo "完成: $url"
  echo "---"
done
```

執行批次下載：

```bash
chmod +x batch_download.sh
./batch_download.sh
```

---

## 🔍 維護與管理

### 查看映像

```bash
# 列出所有映像
docker images | grep jvid-dl
```

### 清理容器和映像

```bash
# 停止所有相關容器
docker compose down

# 移除映像
docker rmi jvid-dl:latest

# 清理未使用的映像和容器
docker system prune -a
```

### 更新映像

```bash
# 重新建構映像
docker compose build --no-cache

# 或者只建構特定服務
docker compose build jvid-dl
```

### 查看容器日誌

```bash
# 如果容器在背景執行
docker compose logs -f jvid-dl
```

---

## 🐛 故障排除

### 常見問題

#### 1. Cookie 檔案找不到

**錯誤訊息:**
```
Error: Cookie file not found
```

**解決方法:**
- 確認 `www.jvid.com_cookies.json` 在專案根目錄
- 檢查檔案權限（應該可讀）
- 檢查 `docker-compose.yml` 中的 volume 路徑

#### 2. 下載失敗 - 認證錯誤

**錯誤訊息:**
```
Authentication failed
```

**解決方法:**
- 使用瀏覽器重新導出 Cookie
- 確認 Cookie 未過期
- 檢查 Cookie 檔案格式是否正確

#### 3. 映像建構失敗

**錯誤訊息:**
```
ERROR: failed to solve: ...
```

**解決方法:**
```bash
# 清理 Docker 快取
docker builder prune -a

# 重新建構
docker compose build --no-cache
```

#### 4. Volume 掛載問題（Windows）

**錯誤訊息:**
```
Error: cannot mount volume
```

**解決方法（Windows）:**
- 確保在 Docker Desktop 設定中啟用檔案共享
- 使用完整路徑：
  ```powershell
  docker run --rm `
    -v "${PWD}\www.jvid.com_cookies.json:/app/cookies/www.jvid.com_cookies.json:ro" `
    -v "${PWD}\media:/app/media" `
    jvid-dl:latest -u "URL"
  ```

#### 5. 容器內找不到檔案

**問題:** 下載成功但找不到檔案

**解決方法:**
- 檢查 `./media` 目錄
- 確認 volume 掛載正確
- 查看容器內路徑：
  ```bash
  docker compose run --rm jvid-dl ls -la /app/media
  ```

#### 6. 權限問題

**錯誤訊息:**
```
Permission denied
```

**解決方法:**
```bash
# Linux/macOS: 修改目錄權限
sudo chown -R $USER:$USER ./media

# 或在 docker-compose.yml 中使用當前使用者 UID
user: "1000:1000"
```

### 除錯模式

如果遇到問題，可以進入容器進行除錯：

```bash
# 進入容器 shell
docker compose run --rm --entrypoint /bin/bash jvid-dl

# 在容器內測試
ls -la /app
ls -la /app/cookies
python -c "import Entry; print('OK')"
```

---

## 🛡️ 安全最佳實踐

### 1. Cookie 檔案保護

```bash
# 設定適當的檔案權限
chmod 600 www.jvid.com_cookies.json

# 不要將 Cookie 檔案加入 Git
echo "*.json" >> .gitignore
```

### 2. 使用 .env 檔案

```bash
# .env 檔案不應該被追蹤
echo ".env" >> .gitignore

# 只提供 .env.example 作為範本
```

### 3. 定期更新映像

```bash
# 更新基礎映像
docker compose build --pull

# 更新依賴
docker compose build --no-cache
```

### 4. 限制資源使用

在 `docker-compose.yml` 中設定資源限制，避免容器消耗過多系統資源。

---

## 📊 效能優化

### 1. 使用 BuildKit

```bash
# 啟用 BuildKit 加速建構
export DOCKER_BUILDKIT=1
docker compose build
```

### 2. 快取優化

Dockerfile 已經優化了層快取：
- 先複製 `pyproject.toml` 和 `uv.lock`
- 再安裝依賴
- 最後複製應用程式碼

這樣當只修改程式碼時，不需要重新安裝依賴。

### 3. 多執行緒下載

```bash
# 根據網路狀況調整執行緒數
docker compose run --rm jvid-dl -u "URL" -n 3 -a
```

**建議:**
- 穩定網路：2-3 執行緒
- 不穩定網路：1 執行緒
- 高速網路：3-5 執行緒

---

## 📈 Docker vs 本地執行比較

| 特性 | Docker 部署 | 本地執行 |
|------|------------|----------|
| **環境隔離** | ✅ 完全隔離 | ❌ 可能衝突 |
| **依賴管理** | ✅ 自動處理 | ⚠️ 需手動安裝 |
| **跨平台** | ✅ 完全一致 | ⚠️ 可能有差異 |
| **部署速度** | ⚠️ 首次建構慢 | ✅ 快速 |
| **更新維護** | ✅ 簡單 | ⚠️ 需手動更新 |
| **資源消耗** | ⚠️ 稍高 | ✅ 較低 |
| **除錯便利性** | ⚠️ 需進入容器 | ✅ 直接除錯 |

---

## 🔗 相關資源

### 官方文檔

- [Docker 官方文檔](https://docs.docker.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)
- [uv 官方文檔](https://github.com/astral-sh/uv)

### 專案文檔

- [README.md](../README.md) - 專案概覽
- [USER_GUIDE.md](USER_GUIDE.md) - 使用者指南
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - 開發者指南

---

## ❓ 常見問題 FAQ

### Q1: Docker 映像有多大？

**A:** 約 300-400 MB（使用 slim 基礎映像優化後）

### Q2: 可以在 Raspberry Pi 上執行嗎？

**A:** 可以，但需要使用 ARM 架構的基礎映像：
```dockerfile
FROM python:3.11-slim-bullseye
# 其他內容保持不變
```

### Q3: 如何在容器間共享下載的檔案？

**A:** 使用命名 volume：
```yaml
volumes:
  shared_media:
    driver: local

services:
  jvid-dl:
    volumes:
      - shared_media:/app/media
```

### Q4: 如何在 CI/CD 中使用？

**A:** GitHub Actions 範例：
```yaml
name: Download Media
on: [workflow_dispatch]

jobs:
  download:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker compose build
      - name: Run download
        run: |
          docker compose run --rm jvid-dl \
            -u "${{ secrets.JVID_URL }}" -a
```

### Q5: 可以同時執行多個下載任務嗎？

**A:** 可以，使用不同的容器名稱：
```bash
# 終端機 1
docker compose run --rm --name dl1 jvid-dl -u "URL1"

# 終端機 2  
docker compose run --rm --name dl2 jvid-dl -u "URL2"
```

---

## 📞 支援與回饋

### 遇到問題？

1. 查看 [故障排除](#故障排除) 章節
2. 檢查 [常見問題 FAQ](#常見問題-faq)
3. 提交 [GitHub Issue](https://github.com/charles1018/Parsing-Media-From-JVID/issues)

### 改進建議

歡迎透過 Pull Request 或 Issue 提供改進建議！

---

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 文件

---

**🎉 恭喜！** 你已經完成 Docker 部署設定。現在可以開始使用容器化的 JVID 下載工具了！

**提示：** 記得定期更新 Cookie 檔案以保持認證有效。
