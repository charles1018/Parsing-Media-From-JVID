# JVID 媒體下載工具 - 使用者指南 📖

本指南將幫助你快速上手 JVID 媒體下載工具。

## 目錄

1. [安裝與設置](#安裝與設置)
2. [獲取 Cookies](#獲取-cookies)
3. [基本使用](#基本使用)
4. [進階功能](#進階功能)
5. [常見問題](#常見問題)
6. [最佳實踐](#最佳實踐)

---

## 安裝與設置

### 前置需求

- **Python 3.8+**: 確保系統已安裝 Python
- **uv**: 套件管理工具（透過 scoop 安裝）
- **Git**: 用於克隆專案

### 安裝步驟

#### 1. 安裝 uv（如果尚未安裝）

**Windows (使用 Scoop):**
```powershell
scoop install uv
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 克隆專案

```bash
git clone https://github.com/charles1018/Parsing-Media-From-JVID.git
cd Parsing-Media-From-JVID
```

#### 3. 創建虛擬環境

```bash
# 創建虛擬環境（使用系統 Python）
uv venv

# 或指定 Python 版本
uv venv --python 3.11
```

#### 4. 安裝依賴

```bash
uv sync
```

完成！你的環境已準備就緒。

---

## 獲取 Cookies

Cookie 是訪問 JVID 內容所必需的認證資訊。

### 方法 1: 使用瀏覽器擴充套件（推薦）

#### Chrome / Edge

1. 安裝 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie) 擴充套件
2. 登入 [JVID](https://www.jvid.com)
3. 點擊瀏覽器工具列的 EditThisCookie 圖示
4. 點擊「Export」匯出 Cookies
5. 將匯出的內容保存為 `www.jvid.com_cookies.json`
6. 將文件放置在專案根目錄

#### Firefox

1. 安裝 [Cookie Quick Manager](https://addons.mozilla.org/firefox/addon/cookie-quick-manager/)
2. 登入 [JVID](https://www.jvid.com)
3. 打開擴充套件
4. 找到 `jvid.com` 的 cookies
5. 匯出為 JSON 格式
6. 保存為 `www.jvid.com_cookies.json`

### 方法 2: 使用開發者工具

1. 登入 JVID
2. 按 `F12` 打開開發者工具
3. 切換到「Application」或「儲存空間」標籤
4. 在左側選擇「Cookies」→「https://www.jvid.com」
5. 手動複製所需的 cookie 值

### Cookie 文件格式

你的 `www.jvid.com_cookies.json` 應該看起來像這樣：

```json
[
  {
    "domain": ".jvid.com",
    "name": "auth",
    "value": "{\"token\":\"...\",\"mediaToken\":\"...\"}",
    ...
  },
  ...
]
```

### 支援的文件名稱

工具會自動搜尋以下文件名稱（優先順序由高到低）：

1. `www.jvid.com_cookies.json` ✅ 推薦
2. `jvid_cookies.json`
3. `cookies.json`

---

## 基本使用

### 標準下載流程

#### 1. 找到要下載的內容

在 JVID 找到你想下載的頁面，複製 URL。例如：
```
https://www.jvid.com/v/12345
```

#### 2. 執行下載命令

**三種執行方式（按推薦優先級）：**

**方式 1：便捷腳本（推薦新手）**

Windows:
```powershell
# CMD
scripts\jvid-download.bat "https://www.jvid.com/v/12345"

# PowerShell
.\scripts\jvid-download.ps1 -Url "https://www.jvid.com/v/12345"
```

macOS/Linux:
```bash
./scripts/jvid-download.sh "https://www.jvid.com/v/12345"
```

**方式 2：入口點（推薦熟手，最簡潔）**

使用專案定義的 `jvid-dl` 入口點：

```bash
uv run jvid-dl -u "https://www.jvid.com/v/12345"
```

> 💡 **為什麼推薦入口點？**
> - ✨ 命令最簡潔，只需記住 `uv run jvid-dl`
> - 📦 符合 Python 套件管理最佳實踐
> - 🔧 支援別名：也可使用 `jvid` 或 `jvid-download`
> - ⚡ uv 自動處理虛擬環境，無需手動啟動

**方式 3：直接執行（開發調試用）**
```bash
uv run python Entry.py -u "https://www.jvid.com/v/12345"
```

#### 3. 等待下載完成

程式會自動：
- 偵測頁面內容類型（影片/圖片）
- 下載所有可用版本的影片
- 顯示下載進度
- 自動清理暫存檔案

#### 4. 查看下載結果

預設情況下，媒體會保存在 `media/` 目錄中。

### 命令列參數說明

| 參數 | 簡寫 | 說明 | 是否必填 | 預設值 | 範例 |
|-----|------|------|---------|--------|------|
| `--url` | `-u` | JVID 頁面 URL | ✅ 是 | 無 | `"https://www.jvid.com/v/123"` |
| `--path` | `-p` | 保存路徑 | ❌ 否 | `media` | `"downloads"` |
| `--auto-resume` | `-a` | 自動續傳 | ❌ 否 | `false` | （無值） |
| `--diagnostic-mode` | `-d` | 診斷模式 | ❌ 否 | `false` | （無值） |
| `--threads` | `-n` | 執行緒數量 | ❌ 否 | `1` | `3` |
| `--working-url` | `-w` | 添加成功案例 | ❌ 否 | 無 | `"https://www.jvid.com/v/456"` |

---

## 進階功能

### 自訂保存路徑

將下載內容保存到指定目錄：

```bash
# 使用入口點（推薦）
uv run jvid-dl -u "https://www.jvid.com/v/12345" -p "my_downloads"

# 使用便捷腳本
./scripts/jvid-download.sh "https://www.jvid.com/v/12345" -p "my_downloads"
```

這會創建 `my_downloads/` 目錄並將媒體保存在其中。

### 自動續傳

當下載中斷時，使用 `-a` 參數可以自動恢復下載，無需手動確認：

```bash
# 使用入口點（推薦）
uv run jvid-dl -u "https://www.jvid.com/v/12345" -a

# 使用便捷腳本
./scripts/jvid-download.sh "https://www.jvid.com/v/12345" -a
```

**何時使用:**
- 網路不穩定
- 下載大型檔案
- 批次下載多個頁面

### 多執行緒下載

支援 1-16 個執行緒的並行下載，預設為單執行緒。多執行緒下載已確保執行緒安全，不會發生檔案覆寫或資料損壞問題。

```bash
# 使用入口點（推薦）
uv run jvid-dl -u "https://www.jvid.com/v/12345" -n 3

# 使用便捷腳本
./scripts/jvid-download.sh "https://www.jvid.com/v/12345" -n 3
```

**執行緒數設定:**
- 預設值：1（單執行緒）
- 最小值：1
- 最大值：16（超過會自動調整）
- 建議值：2-4 個執行緒可獲得較好的速度與穩定性平衡

### 診斷模式

當遇到解析問題時使用：

```bash
# 使用入口點（推薦）
uv run jvid-dl -u "https://www.jvid.com/v/12345" -d

# 使用便捷腳本
./scripts/jvid-download.sh "https://www.jvid.com/v/12345" -d
```

**診斷模式會做什麼:**
1. 詳細分析頁面 HTML 結構
2. 嘗試 5 種不同的解析策略
3. 與成功案例進行結構比較
4. 生成完整的診斷報告

**診斷報告位置:**
```
media/diagnostic_reports/diagnostic_report_[timestamp].txt
```

### 記錄成功案例

將成功下載的 URL 記錄下來，幫助診斷模式：

```bash
# 使用入口點（推薦）
uv run jvid-dl -w "https://www.jvid.com/v/12345"

# 使用便捷腳本
./scripts/jvid-download.sh -w "https://www.jvid.com/v/12345"
```

成功案例會保存在 `media/working_examples.txt` 中。

---

## 常見問題

### Q1: 程式顯示「未找到 cookie 文件」

**A:** 確認以下事項：
1. Cookie 文件名稱正確（`www.jvid.com_cookies.json`）
2. 文件位於專案**根目錄**（不是 `package/` 或其他子目錄）
3. JSON 格式正確（可用線上 JSON 驗證器檢查）

### Q2: 下載速度很慢

**A:** 嘗試以下方法：
1. 增加執行緒數量：`-n 2` 或 `-n 3`
2. 檢查網路連線速度
3. 嘗試不同時段下載
4. 確認 JVID 伺服器狀態

### Q3: 下載的影片無法播放

**A:** 可能原因：
1. 下載未完成 → 使用 `-a` 參數續傳
2. FFmpeg 未安裝 → 安裝 FFmpeg（用於影片處理）
3. 影片格式問題 → 嘗試使用 VLC 播放器

### Q4: Cookie 認證失效

**A:** Cookie 會過期，需要定期更新：
1. 重新登入 JVID
2. 使用瀏覽器擴充套件匯出新的 cookies
3. 覆蓋舊的 `www.jvid.com_cookies.json`

### Q5: 如何批次下載多個 URL？

**A:** 創建一個批次腳本：

**Windows (batch 腳本):**
```batch
@echo off
uv run jvid-dl -u "https://www.jvid.com/v/12345" -a
uv run jvid-dl -u "https://www.jvid.com/v/67890" -a
uv run jvid-dl -u "https://www.jvid.com/v/11111" -a
```

**macOS/Linux (bash 腳本):**
```bash
#!/bin/bash
urls=(
  "https://www.jvid.com/v/12345"
  "https://www.jvid.com/v/67890"
  "https://www.jvid.com/v/11111"
)

for url in "${urls[@]}"; do
  uv run jvid-dl -u "$url" -a
done
```

### Q6: 程式卡住不動

**A:** 可能原因及解決方法：
1. 網路逾時 → 按 `Ctrl+C` 中斷後重試
2. 頁面結構改變 → 使用診斷模式 `-d`
3. Cookie 過期 → 更新 cookies

### Q7: uv sync 失敗

**A:** 嘗試以下步驟：
```bash
# 清除快取
uv cache clean

# 重新創建虛擬環境
rm -rf .venv  # Windows: rmdir /s .venv
uv venv

# 重新同步
uv sync
```

---

## 最佳實踐

### 1. Cookie 管理

✅ **推薦做法:**
- 定期更新 cookies（建議每月）
- 使用瀏覽器擴充套件自動化匯出
- 在 `.gitignore` 中排除 cookie 文件

❌ **避免做法:**
- 將 cookies 上傳到公開倉庫
- 使用過期的 cookies
- 與他人分享你的 cookies

### 2. 下載策略

✅ **推薦做法:**
- 首次下載使用單執行緒測試
- 啟用自動續傳 `-a`
- 為不同類型內容設置不同保存路徑
- 定期清理下載目錄

❌ **避免做法:**
- 一開始就使用高執行緒數
- 同時下載過多內容
- 忽略錯誤訊息

### 3. 診斷與除錯

✅ **推薦做法:**
- 遇到問題先查看控制台輸出
- 使用診斷模式收集資訊
- 記錄成功案例以供參考
- 查看日誌檔案 `media/downloads_log.txt`

❌ **避免做法:**
- 忽略警告訊息
- 不保存診斷報告
- 重複嘗試失敗的 URL 而不改變策略

### 4. 環境管理

✅ **推薦做法:**
- 使用 uv 管理依賴
- 定期執行 `uv sync` 更新套件
- 使用虛擬環境隔離專案
- 保持 Python 和 uv 為最新版本

❌ **避免做法:**
- 直接修改系統 Python 環境
- 混用 pip 和 uv
- 忽略依賴版本衝突

---

## 範例使用情境

### 情境 1: 下載單個影片

```bash
# 使用入口點（推薦）
uv run jvid-dl -u "https://www.jvid.com/v/12345"

# 或使用便捷腳本
./scripts/jvid-download.sh "https://www.jvid.com/v/12345"
```

### 情境 2: 下載到特定資料夾

```bash
# 按日期組織
uv run jvid-dl -u "https://www.jvid.com/v/12345" -p "downloads/2025-01"
```

### 情境 3: 不穩定網路環境

```bash
# 啟用自動續傳
uv run jvid-dl -u "https://www.jvid.com/v/12345" -a
```

### 情境 4: 解析問題排查

```bash
# 啟用診斷模式
uv run jvid-dl -u "https://www.jvid.com/v/12345" -d

# 查看診斷報告
cat media/diagnostic_reports/diagnostic_report_*.txt
```

### 情境 5: 快速批次下載

```bash
# 使用多執行緒
uv run jvid-dl -u "https://www.jvid.com/v/12345" -n 3 -a
```

---

## 技術支援

如需進一步協助：

1. 📖 查閱 [開發者指南](DEVELOPER_GUIDE.md)
2. 🐛 提交 [Issue](https://github.com/yourusername/Parsing-Media-From-JVID/issues)
3. 💬 參與討論
4. 📧 聯繫維護者

---

**提示**: 使用時請遵守 JVID 使用條款，僅供個人學習研究使用。


---

## 🔄 批次下載

### PowerShell 批次腳本

```powershell
$urls = @(
    "https://www.jvid.com/v/12345",
    "https://www.jvid.com/v/67890"
)

foreach ($url in $urls) {
    uv run jvid-dl -u $url -a
}
```

### Bash 批次腳本

```bash
urls=(
    "https://www.jvid.com/v/12345"
    "https://www.jvid.com/v/67890"
)

for url in "${urls[@]}"; do
    uv run jvid-dl -u "$url" -a
done
```

---

## ❓ 常見問題 FAQ

### Q: 顯示「未找到 cookie 文件」

**解決方案：**
1. 確認 `www.jvid.com_cookies.json` 在專案根目錄
2. 運行測試：`uv run python test_cookie_manager.py`

### Q: 下載速度很慢

**解決方案：**
```bash
# 增加執行緒到 2-3
uv run jvid-dl -u "URL" -n 3 -a
```

### Q: 下載中斷

**解決方案：**
```bash
# 使用自動續傳重新運行
uv run jvid-dl -u "URL" -a
```

### Q: 無法解析頁面

**解決方案：**
```bash
# 啟用診斷模式
uv run jvid-dl -u "URL" -d
```

---

## 🔧 專案維護

### 更新專案到最新版本

```bash
# 拉取最新代碼
git pull

# 更新依賴
uv sync --upgrade
```

### 清理下載緩存

```bash
# Windows PowerShell
Remove-Item -Recurse -Force media\*

# macOS/Linux
rm -rf media/*
```

---

**提示**: 使用時請遵守 JVID 使用條款，僅供個人學習研究使用。
