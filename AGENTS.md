# AGENTS.md

> 給在此儲存庫工作的 AI 編碼代理（Codex CLI、Claude Code 等）。此檔刻意精簡，**不重複**其他文件內容。

## 先讀這些

1. **`CLAUDE.md`** — 專案慣例與常用指令（每個 session 必讀）。
2. **`FUTURE_AGENT_REPO_GUIDE.md`** — 完整的架構、風險與改善路線圖（英文）。動手改 code 前先讀其 §1、§4、§5、§11。

## 指令速查

```bash
uv sync                                   # 安裝依賴（含 dev）
uv run pytest                             # 全部測試（應全綠）
uv run jvid-dl -u "https://www.jvid.com/v/PAGE_ID"   # CLI
uv run jvid-webui                         # Web UI（port 7860）
ruff check --fix . && ruff format .       # 提交前必跑
```

提交前檢查：`ruff check --fix . && ruff format .` 然後 `uv run pytest`。無 CI，本地驗證是唯一關卡。

## 安全紅線（務必遵守）

- 工作目錄含**真實**的 JVID session cookie 與付費/NSFW 內容：
  `www.jvid.com_cookies.json`、`.env`、`media/**`。三者皆已被 `.gitignore` 排除。
- **絕不** 執行 `git add -A` / `git add -f` 於儲存庫根目錄；**絕不** 弱化 `.gitignore`。
- **絕不** 讀取或印出上述檔案的內容；`media/` 的目錄名稱是露骨標題，不得出現在 commit、PR、log 或任何送往外部服務的內容中。
- **絕不** 自行拿使用者的 cookie 發真實請求或跑真實下載；需要實測時停下來請使用者執行並貼上輸出。

## 慣例重點

- 所有註解、訊息、commit 主旨用**台灣繁體中文**；語義化 commit 前綴（`feat:`/`fix:`/`docs:`/`refactor:`/`test:`/`chore:`）。
- 輸出用 `rich` 的 `console.print()`，勿用裸 `print()`；子程序用 list 形式命令，禁止 `shell=True`；檔案 I/O 明確指定 UTF-8。
