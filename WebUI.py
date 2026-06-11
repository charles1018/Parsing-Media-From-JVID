"""
JVID 媒體下載工具 - Gradio Web UI
==================================

提供圖形化網頁介面，讓一般使用者更容易上手。

使用方式：
    uv run python WebUI.py

啟動後會自動開啟瀏覽器，訪問 http://localhost:7860
"""

import os
import signal
import sys
from collections.abc import Generator
from dataclasses import dataclass

import gradio as gr

from package.ParsingMediaLogic import ParsingMediaLogic


def shutdown_server():
    """關閉伺服器"""
    os.kill(os.getpid(), signal.SIGTERM)


@dataclass
class DownloadConfig:
    """下載配置資料類別，模擬命令行參數物件"""

    type: str = "auto"
    url: str = ""
    path: str = "media"
    auto_resume: bool = True
    diagnostic_mode: bool = False
    thread_count: int = 1
    # Web UI 無法以 input() 詢問使用者，未勾選自動續傳時直接重新檢查下載
    interactive: bool = False


def validate_url(url: str) -> tuple[bool, str]:
    """驗證 URL 格式"""
    if not url or not url.strip():
        return False, "請輸入 JVID 網址"
    if not url.startswith("http"):
        return False, "網址必須以 http:// 或 https:// 開頭"
    if "jvid.com" not in url.lower():
        return False, "請輸入有效的 JVID 網址"
    return True, ""


def download_media(
    url: str,
    save_path: str,
    auto_resume: bool,
    thread_count: int,
    progress: gr.Progress = gr.Progress(track_tqdm=True),  # noqa: B008
) -> Generator[str, None, None]:
    """
    執行下載任務

    Args:
        url: JVID 頁面網址
        save_path: 儲存路徑
        auto_resume: 是否自動續傳
        thread_count: 執行緒數量
        progress: Gradio 進度追蹤器

    Yields:
        下載狀態訊息
    """
    # 驗證輸入
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        yield f"❌ 錯誤: {error_msg}"
        return

    # 驗證執行緒數
    if thread_count < 1:
        thread_count = 1
    elif thread_count > 16:
        thread_count = 16
        yield "⚠️ 執行緒數過高，已自動調整為 16"

    # 建立配置
    config = DownloadConfig(
        url=url.strip(),
        path=save_path.strip() or "media",
        auto_resume=auto_resume,
        thread_count=thread_count,
    )

    yield f"🚀 開始下載...\n📁 儲存路徑: {os.path.abspath(config.path)}\n🔗 URL: {config.url}\n"

    try:
        # 初始化並執行下載
        progress(0, desc="初始化中...")
        logic = ParsingMediaLogic(config)

        progress(0.1, desc="解析頁面中...")
        logic.main()

        if logic.download_complete:
            yield "✅ 下載完成！"
        else:
            yield "⚠️ 下載未全部完成，請再次執行（勾選自動續傳）以繼續下載"

    except KeyboardInterrupt:
        yield "⚠️ 下載已被使用者中斷"
    except Exception as e:
        yield f"❌ 下載失敗: {str(e)}"


def create_ui() -> gr.Blocks:
    """建立 Gradio 介面"""

    with gr.Blocks(title="JVID 媒體下載器") as demo:
        # 標題
        gr.Markdown(
            """
            # 🎬 JVID 媒體下載器
            輸入 JVID 網址，自動下載影片或圖片
            """,
            elem_classes="main-title",
        )

        with gr.Row():
            with gr.Column(scale=2):
                # 輸入區域
                url_input = gr.Textbox(
                    label="JVID 網址",
                    placeholder="https://www.jvid.com/v/xxxxx",
                    info="貼上要下載的 JVID 頁面網址",
                )

                with gr.Row():
                    path_input = gr.Textbox(
                        label="儲存路徑",
                        value="media",
                        info="檔案將儲存到此資料夾",
                    )
                    thread_input = gr.Slider(
                        label="執行緒數",
                        minimum=1,
                        maximum=8,
                        value=1,
                        step=1,
                        info="建議使用 1-3 個執行緒",
                    )

                auto_resume_input = gr.Checkbox(
                    label="自動續傳",
                    value=True,
                    info="如果有未完成的下載，自動繼續",
                )

                # 按鈕
                with gr.Row():
                    download_btn = gr.Button(
                        "🚀 開始下載",
                        variant="primary",
                        scale=2,
                    )
                    clear_btn = gr.Button("🗑️ 清除", scale=1)

            with gr.Column(scale=1):
                # 狀態輸出
                status_output = gr.Textbox(
                    label="下載狀態",
                    lines=10,
                    max_lines=20,
                    interactive=False,
                    elem_classes="status-box",
                )

        # 使用說明
        with gr.Accordion("📖 使用說明", open=False):
            gr.Markdown(
                """
                ### 基本使用步驟
                1. 複製 JVID 頁面網址（格式如：`https://www.jvid.com/v/xxxxx`）
                2. 貼到「JVID 網址」欄位
                3. 點擊「開始下載」按鈕
                4. 等待下載完成

                ### 進階設定
                - **儲存路徑**：自訂下載檔案的儲存位置（預設為 `media` 資料夾）
                - **執行緒數**：增加可加快下載速度，但可能增加失敗風險，建議使用 1-3
                - **自動續傳**：若之前有中斷的下載，會自動繼續

                ### 注意事項
                - 請確保網路連線穩定
                - 下載過程中請勿關閉此頁面
                - 如遇問題，可嘗試降低執行緒數
                - 使用完畢後，請點擊「關閉伺服器」按鈕結束程式
                """
            )

        # 關閉伺服器按鈕
        with gr.Row():
            shutdown_btn = gr.Button(
                "⏹️ 關閉伺服器",
                variant="stop",
                size="sm",
            )

        # 事件綁定
        download_btn.click(
            fn=download_media,
            inputs=[url_input, path_input, auto_resume_input, thread_input],
            outputs=status_output,
        )

        clear_btn.click(
            fn=lambda: ("", "media", True, 1, ""),
            outputs=[
                url_input,
                path_input,
                auto_resume_input,
                thread_input,
                status_output,
            ],
        )

        shutdown_btn.click(
            fn=shutdown_server,
            inputs=None,
            outputs=None,
        )

    return demo


def _fix_windows_console_encoding():
    """Windows 主控台 UTF-8 編碼修正（同 Entry.py）"""
    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    """主程式入口"""
    _fix_windows_console_encoding()
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",  # 允許外部訪問
        server_port=7860,
        share=False,  # 設為 True 可產生公開連結
        show_error=True,
        inbrowser=True,  # 自動打開瀏覽器
    )


if __name__ == "__main__":
    main()
