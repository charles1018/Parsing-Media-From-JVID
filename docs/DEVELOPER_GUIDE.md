# JVID 媒體下載工具 - 開發者指南 🛠️

本指南面向希望理解、修改或擴展此專案的開發者。

## 目錄

1. [專案架構](#專案架構)
2. [開發環境設置](#開發環境設置)
3. [核心模組說明](#核心模組說明)
4. [工作流程](#工作流程)
5. [擴展指南](#擴展指南)
6. [測試與除錯](#測試與除錯)
7. [貢獻指南](#貢獻指南)

---

## 專案架構

### 目錄結構

```
Parsing-Media-From-JVID/
├── Entry.py                        # 程式入口，處理命令列參數
├── pyproject.toml                  # uv 專案配置
├── uv.lock                         # 依賴鎖定檔
├── .gitignore                      # Git 忽略規則
├── README.md                       # 專案說明
├── USER_GUIDE.md                   # 使用者指南
├── DEVELOPER_GUIDE.md              # 本文件
│
├── package/                        # 主要功能包
│   ├── __init__.py                # 包初始化
│   ├── ArgumentParser.py          # 命令列參數解析
│   ├── ParsingMediaLogic.py       # 核心解析邏輯
│   ├── DiagnosticMode.py          # 診斷模式實現
│   │
│   ├── network/                   # 網路相關模組
│   │   ├── __init__.py
│   │   └── NetworkManager.py     # HTTP 請求管理
│   │
│   ├── processors/                # 媒體處理器
│   │   ├── __init__.py
│   │   ├── VideoProcessor.py     # 影片下載與處理
│   │   └── ImageProcessor.py     # 圖片下載與處理
│   │
│   └── utils/                     # 工具模組
│       ├── __init__.py
│       ├── CookieManager.py       # Cookie 自動管理 ⭐ 新增
│       ├── ContentDetector.py     # 內容類型偵測
│       └── ProgressManager.py     # 下載進度管理
│
├── media/                          # 預設下載目錄
│   ├── downloads_log.txt          # 下載記錄
│   ├── working_examples.txt       # 成功案例列表
│   └── diagnostic_reports/        # 診斷報告目錄
│
└── .venv/                          # uv 虛擬環境（不追蹤）
```

### 資料流向

```
User Input (CLI)
      ↓
Entry.py → ArgumentParser
      ↓
ParsingMediaLogic
      ↓
CookieManager → 讀取認證
      ↓
NetworkManager → 發送請求
      ↓
ContentDetector → 判斷內容類型
      ↓
VideoProcessor / ImageProcessor → 處理下載
      ↓
ProgressManager → 顯示進度
      ↓
Downloaded Media
```

---

## 開發環境設置

### 1. 克隆專案

```bash
git clone https://github.com/yourusername/Parsing-Media-From-JVID.git
cd Parsing-Media-From-JVID
```

### 2. 安裝 uv（如果尚未安裝）

**Windows:**
```powershell
scoop install uv
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 創建虛擬環境


```bash
# 創建 Python 3.11 虛擬環境
uv venv --python 3.11

# 或使用系統預設 Python
uv venv
```

### 4. 安裝依賴（包含開發依賴）

```bash
uv sync
```

### 5. 驗證安裝

```bash
# 方法 1：使用入口點（最簡潔，推薦）
uv run jvid-dl --help

# 方法 2：直接執行（開發調試用）
uv run python Entry.py --help

# 方法 3：使用便捷腳本
./scripts/jvid-download.sh --help  # macOS/Linux
scripts/jvid-download.bat --help   # Windows
```

> 💡 **uv 最佳實踐：** 使用 `uv run` 命令會自動管理虛擬環境，無需手動啟動。這是 uv 的核心優勢之一！

---

## 核心模組說明

### 1. Entry.py - 程式入口

**職責:**
- 接收命令列參數
- 初始化主要邏輯
- 處理程式生命週期

**關鍵類別:**
```python
class Entry:
    def __init__(self):
        self.type = None
        self.url = None
        self.path = None
        self.auto_resume = False
    
    def main(self):
        ap = AP(self)
        ap.config_once()
        pm = ParsingMediaLogic(self)
        pm.main()
```

### 2. ArgumentParser.py - 參數解析

**職責:**
- 定義命令列參數
- 解析使用者輸入
- 處理工作 URL 記錄

**主要方法:**
```python
class AP:
    @staticmethod
    def parse_args() -> Namespace:
        # 定義並解析參數
        
    def config_once(self):
        # 配置參數到物件
        
    def add_working_example(self, url):
        # 記錄成功案例
```

**支援的參數:**
- `-u, --url`: 目標 URL（必填）
- `-p, --path`: 保存路徑
- `-a, --auto-resume`: 自動續傳
- `-d, --diagnostic-mode`: 診斷模式
- `-n, --threads`: 執行緒數量
- `-w, --working-url`: 添加成功案例

### 3. CookieManager.py - Cookie 管理 ⭐ 核心新功能

**職責:**
- 自動尋找並讀取 Cookie 文件
- 解析 Cookie 中的認證資訊
- 構建請求頭（Headers）

**類別結構:**
```python
class CookieManager:
    COOKIE_FILENAMES = [
        'www.jvid.com_cookies.json',
        'jvid_cookies.json',
        'cookies.json'
    ]
    
    def __init__(self, base_path: Optional[str] = None):
        # 初始化基礎路徑
        
    def find_cookie_file(self) -> Optional[Path]:
        # 尋找 cookie 文件
        
    def load_cookies(self) -> Optional[list]:
        # 載入 cookies
        
    def extract_auth_info(self, cookies: list) -> Tuple:
        # 提取 authorization 和 cookie 字串
        
    def get_headers(self, user_agent: str) -> Dict:
        # 獲取完整請求頭
```

**工作流程:**
1. 在專案目錄中搜尋 cookie 文件
2. 讀取並解析 JSON 格式的 cookies
3. 從 `auth` cookie 提取 token
4. 構建完整的 Cookie 字串
5. 返回包含認證資訊的 headers

**範例使用:**
```python
from package.utils.CookieManager import CookieManager
from package.network.NetworkManager import NetworkManager

# 創建 CookieManager 實例
cookie_manager = CookieManager()

# 獲取帶認證的 headers
user_agent = NetworkManager.get_random_user_agent()
headers = cookie_manager.get_headers(user_agent)

# 使用 headers 發送請求
response = requests.get(url, headers=headers)
```

### 4. ParsingMediaLogic.py - 核心解析邏輯

**職責:**
- 協調整體下載流程
- 管理網路請求
- 調度處理器

**核心方法:**
```python
class ParsingMediaLogic:
    def __init__(self, obj):
        # 初始化模組
        self.headers = self.update_headers()  # 使用 CookieManager
        self.network_manager = NetworkManager(...)
        self.content_detector = ContentDetector()
        
    @staticmethod
    def update_headers() -> dict:
        # 優先使用 CookieManager
        # 回退到 permissions.txt
        
    def main(self):
        # 主要工作流程
```

### 5. NetworkManager.py - 網路管理

**職責:**
- 處理 HTTP 請求
- 管理重試邏輯
- 提供隨機 User-Agent

**關鍵功能:**

- 自動重試失敗的請求
- 隨機化 User-Agent
- 處理網路異常

### 6. VideoProcessor.py & ImageProcessor.py - 媒體處理器

**職責:**
- 下載影片/圖片
- 處理 m3u8 串流
- 合併影片片段
- 管理暫存檔案

### 7. ContentDetector.py - 內容偵測

**職責:**
- 分析頁面結構
- 判斷內容類型
- 提取媒體 URL

### 8. ProgressManager.py - 進度管理

**職責:**
- 記錄下載進度
- 管理續傳狀態
- 提供進度查詢

### 9. DiagnosticMode.py - 診斷模式

**職責:**
- 詳細頁面分析
- 多策略嘗試
- 生成診斷報告
- 案例比較

---

## 工作流程

### 完整下載流程

```python
# 1. 程式啟動
Entry.main()
    ↓
# 2. 解析參數
ArgumentParser.parse_args()
    ↓
# 3. 初始化核心邏輯
ParsingMediaLogic.__init__()
    ↓
# 4. 載入認證資訊
CookieManager.get_headers()
    ├─ find_cookie_file()        # 尋找 cookie 文件
    ├─ load_cookies()            # 讀取 cookies
    ├─ extract_auth_info()       # 提取認證
    └─ 回退到 permissions.txt（如果需要）
    ↓
# 5. 初始化網路管理
NetworkManager.__init__(headers)
    ↓
# 6. 獲取頁面內容
NetworkManager.get(url)
    ↓
# 7. 偵測內容類型
ContentDetector.detect(html)
    ↓
# 8. 選擇處理器
if video:
    VideoProcessor.process()
else:
    ImageProcessor.process()
    ↓
# 9. 下載媒體
Processor.download()
    ↓
# 10. 顯示進度
ProgressManager.update()
    ↓
# 11. 完成
```

### Cookie 認證流程（詳細）

```python
# CookieManager 工作流程
CookieManager()
    ↓
find_cookie_file()
    ├─ 搜尋 www.jvid.com_cookies.json
    ├─ 搜尋 jvid_cookies.json
    └─ 搜尋 cookies.json
    ↓
load_cookies()
    ├─ 讀取 JSON 文件
    ├─ 解析 JSON 結構
    └─ 返回 cookie 列表
    ↓
extract_auth_info(cookies)
    ├─ 尋找 'auth' cookie
    ├─ URL decode cookie value
    ├─ 解析 JSON 獲取 token
    └─ 構建完整 cookie 字串
    ↓
get_headers(user_agent)
    ├─ 基礎 headers = {'user-agent': ...}
    ├─ 添加 'authorization': 'Bearer {token}'
    ├─ 添加 'cookie': '{cookie_string}'
    └─ 返回完整 headers
```

---

## 擴展指南

### 添加新的媒體處理器

1. 在 `package/processors/` 創建新文件
2. 繼承基礎處理器類別
3. 實現必要方法

```python
# package/processors/AudioProcessor.py
class AudioProcessor:
    def __init__(self, network_manager, path):
        self.network_manager = network_manager
        self.path = path
    
    def process(self, url, soup):
        # 實現音訊下載邏輯
        pass
```

### 添加新的 Cookie 文件格式支援

修改 `CookieManager.py`：

```python
class CookieManager:
    COOKIE_FILENAMES = [
        'www.jvid.com_cookies.json',
        'jvid_cookies.json',
        'cookies.json',
        'my_custom_cookies.json'  # 添加新格式
    ]
```

### 添加新的命令列參數

修改 `ArgumentParser.py`：

```python
parse.add_argument('-x', '--new-feature',
                   help='Description of new feature',
                   default='default_value', type=str)
```

### 擴展診斷模式

修改 `DiagnosticMode.py` 添加新的分析策略：

```python
def analyze_with_new_method(self, soup):
    # 實現新的分析方法
    pass
```

---

## 測試與除錯

### 本地測試

```bash
# 測試基本下載
uv run jvid-dl -u "https://www.jvid.com/v/TEST_ID"

# 測試 Cookie 載入
uv run python test_cookie_manager.py

# 測試多執行緒
uv run jvid-dl -u "https://www.jvid.com/v/TEST_ID" -n 3

# 測試診斷模式
uv run jvid-dl -u "https://www.jvid.com/v/TEST_ID" -d
```

### 除錯技巧

#### 1. 檢查 Cookie 載入

在 `ParsingMediaLogic.py` 中：

```python
headers = self.update_headers()
print("Headers:", headers)  # 除錯輸出
```

#### 2. 查看網路請求

在 `NetworkManager.py` 中添加日誌：

```python
def get(self, url):
    print(f"Request URL: {url}")
    print(f"Headers: {self.headers}")
    response = requests.get(url, headers=self.headers)
    print(f"Status: {response.status_code}")
    return response
```

#### 3. 診斷模式輸出

```bash
# 啟用診斷模式獲取詳細資訊
uv run jvid-dl -u "URL" -d

# 查看診斷報告
cat media/diagnostic_reports/diagnostic_report_*.txt
```

#### 4. Python 除錯器

```python
# 在需要除錯的地方添加
import pdb; pdb.set_trace()
```

### 常見問題排查

#### Cookie 載入失敗

```python
# 測試 CookieManager
from package.utils.CookieManager import CookieManager

cm = CookieManager()
cookie_file = cm.find_cookie_file()
print(f"Found: {cookie_file}")

cookies = cm.load_cookies()
print(f"Loaded: {len(cookies) if cookies else 0} cookies")
```

#### 認證失敗

檢查：
1. Cookie 文件格式是否正確
2. auth cookie 中是否包含 token
3. token 是否已過期

---

## uv 套件管理

### 添加新依賴

```bash
# 添加生產依賴
uv add package-name

# 添加開發依賴
uv add --dev package-name

# 添加特定版本
uv add package-name==1.2.3
```

### 更新依賴

```bash
# 更新所有依賴
uv sync --upgrade

# 更新特定套件
uv add package-name --upgrade
```

### 移除依賴

```bash
uv remove package-name
```

### 鎖定依賴版本

```bash
# 生成鎖定文件
uv lock

# 根據鎖定文件同步
uv sync
```

### 查看依賴

```bash
# 列出所有已安裝套件
uv pip list

# 顯示依賴樹
uv pip tree
```

---

## Git 工作流程

### 分支策略

- `main`: 穩定版本
- `develop`: 開發版本
- `feature/*`: 新功能分支
- `bugfix/*`: 錯誤修復分支

### 提交規範

使用語義化提交訊息：

```
feat: 新增 CookieManager 模組
fix: 修復下載中斷問題
docs: 更新使用者指南
refactor: 重構網路請求邏輯
test: 添加單元測試
chore: 更新依賴
```

### 開發流程

```bash
# 1. 創建功能分支
git checkout -b feature/new-feature

# 2. 開發並提交
git add .
git commit -m "feat: 實現新功能"

# 3. 推送到遠端
git push origin feature/new-feature

# 4. 創建 Pull Request

# 5. 合併到 develop
git checkout develop
git merge feature/new-feature
```

---

## 貢獻指南

### 貢獻流程

1. Fork 專案
2. 創建功能分支
3. 實現功能並測試
4. 提交 Pull Request
5. 等待審核

### 程式碼風格

- 遵循 PEP 8 規範
- 使用有意義的變數名稱
- 添加適當的註解和文檔字串
- 保持函式簡潔（單一職責）

### Pull Request 檢查清單

- [ ] 程式碼通過測試
- [ ] 添加必要的註解
- [ ] 更新相關文檔
- [ ] 遵循專案程式碼風格
- [ ] 提交訊息清晰明確

---

## 技術棧

- **語言**: Python 3.8+
- **套件管理**: uv
- **HTTP 請求**: requests
- **HTML 解析**: BeautifulSoup4
- **進度顯示**: tqdm, rich
- **加密**: pycryptodome

---

## 參考資源

- [uv 官方文檔](https://github.com/astral-sh/uv)
- [Python 最佳實踐](https://docs.python-guide.org/)
- [PEP 8 風格指南](https://pep8.org/)
- [TS 串流解碼參考](https://cloud.tencent.com/developer/article/2258872)

---

**需要幫助?** 歡迎提交 Issue 或聯繫維護者！
