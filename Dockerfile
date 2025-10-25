# ====================================
# 階段 1：Builder - 安裝依賴
# ====================================
FROM python:3.11-slim AS builder

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 將 uv 加入 PATH（需要在安裝後設定）
ENV PATH="/root/.local/bin:${PATH}"

# 設定工作目錄
WORKDIR /app

# 複製專案配置檔案（README.md 是 pyproject.toml 需要的）
COPY pyproject.toml uv.lock README.md ./

# 複製專案原始碼（安裝需要）
COPY Entry.py ./
COPY package/ ./package/

# 使用 uv pip 安裝專案及其依賴到系統 Python
RUN uv pip install --system .

# ====================================
# 階段 2：Runtime - 執行環境
# ====================================
FROM python:3.11-slim AS runtime

# 設定環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1 \
    PATH="/root/.local/bin:${PATH}"

# 安裝運行時必要的系統套件
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 從 builder 階段複製 uv
COPY --from=builder /root/.local/bin/uv /root/.local/bin/uv
COPY --from=builder /root/.local/bin/uvx /root/.local/bin/uvx

# 建立應用目錄和資料目錄
WORKDIR /app
RUN mkdir -p /app/media /app/cookies

# 從 builder 複製已安裝的依賴
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 複製應用程式碼
COPY Entry.py ./
COPY package/ ./package/
COPY pyproject.toml README.md ./

# 建立非 root 使用者（安全性考量）
RUN useradd -m -u 1000 jvid && \
    chown -R jvid:jvid /app

# 切換到非 root 使用者
USER jvid

# Volume 掛載點
VOLUME ["/app/media", "/app/cookies"]

# 健康檢查（檢查程式是否可執行）
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import Entry; print('OK')" || exit 1

# 設定入口點（使用 Python 直接執行）
ENTRYPOINT ["python", "Entry.py"]

# 預設參數（可被覆蓋）
CMD ["--help"]
