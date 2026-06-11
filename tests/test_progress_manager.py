"""
ProgressManager 單元測試
"""

import json

from rich.console import Console

from package.utils.ProgressManager import ProgressManager

URL = "https://www.jvid.com/v/12345"


def make_manager(tmp_path):
    return ProgressManager(str(tmp_path), Console())


def test_save_and_load_progress(tmp_path):
    """測試進度儲存後可正確載入"""
    manager = make_manager(tmp_path)
    data = {
        "url": URL,
        "type": "auto",
        "todo_list": [[0, "https://a"], [1, "https://b"]],
    }

    assert manager.save_progress(data, quiet=True) is True

    loaded = manager.load_progress(URL)
    assert loaded is not None
    assert loaded["url"] == URL
    assert loaded["todo_list"] == [[0, "https://a"], [1, "https://b"]]
    assert "timestamp" in loaded


def test_load_progress_url_mismatch(tmp_path):
    """測試 URL 不一致時不會載入進度"""
    manager = make_manager(tmp_path)
    manager.save_progress({"url": URL, "todo_list": [[0, "https://a"]]}, quiet=True)

    assert manager.load_progress("https://www.jvid.com/v/99999") is None


def test_load_progress_empty_todo_list(tmp_path):
    """測試剩餘清單為空時視為已完成，不載入進度"""
    manager = make_manager(tmp_path)
    manager.save_progress({"url": URL, "todo_list": []}, quiet=True)

    assert manager.load_progress(URL) is None


def test_check_and_resume_with_auto_resume(tmp_path):
    """測試自動續傳模式直接回傳進度資料"""
    manager = make_manager(tmp_path)
    manager.save_progress({"url": URL, "todo_list": [[0, "https://a"]]}, quiet=True)

    progress = manager.check_and_resume_download(URL, auto_resume=True)
    assert progress is not None
    assert progress["todo_list"] == [[0, "https://a"]]


def test_check_and_resume_non_interactive_without_auto_resume(tmp_path):
    """測試非互動環境未啟用自動續傳時不會卡在 input()，直接回傳 None"""
    manager = make_manager(tmp_path)
    manager.save_progress({"url": URL, "todo_list": [[0, "https://a"]]}, quiet=True)

    progress = manager.check_and_resume_download(
        URL, auto_resume=False, interactive=False
    )
    assert progress is None


def test_delete_progress_file(tmp_path):
    """測試完成後可刪除進度檔"""
    manager = make_manager(tmp_path)
    manager.save_progress({"url": URL, "todo_list": [[0, "https://a"]]}, quiet=True)

    progress_file = tmp_path / "download_progress.json"
    assert progress_file.exists()

    assert manager.delete_progress_file() is True
    assert not progress_file.exists()

    # 檔案不存在時也應回傳 True
    assert manager.delete_progress_file() is True


def test_progress_file_content_is_valid_json(tmp_path):
    """測試進度檔為合法 JSON 且使用 UTF-8 編碼"""
    manager = make_manager(tmp_path)
    manager.save_progress(
        {"url": URL, "type": "auto", "todo_list": [[0, "https://中文路徑/圖.jpg"]]},
        quiet=True,
    )

    with open(tmp_path / "download_progress.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["todo_list"][0][1] == "https://中文路徑/圖.jpg"
