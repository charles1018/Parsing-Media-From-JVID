"""
ImageProcessor 單元測試
"""

from rich.console import Console

from package.processors.ImageProcessor import ImageProcessor


class MockResponse:
    def __init__(self, content):
        self.content = content


class MockNetworkManager:
    def __init__(self, responses):
        self.responses = responses

    def request_with_retry(self, url):
        return MockResponse(self.responses[url])


def test_deduplicate_urls_preserves_order():
    """測試 URL 去重時保留原始順序"""
    image_urls = [
        "https://example.com/1.jpg",
        "https://example.com/2.jpg",
        "https://example.com/1.jpg",
        "https://example.com/3.jpg",
    ]

    assert ImageProcessor._deduplicate_urls(image_urls) == [
        "https://example.com/1.jpg",
        "https://example.com/2.jpg",
        "https://example.com/3.jpg",
    ]


def test_download_single_image_skips_duplicate_content(tmp_path):
    """測試不同 URL 回傳相同圖片內容時只會存一份檔案"""
    network_manager = MockNetworkManager(
        {
            "https://example.com/a.jpg?token=1": b"same image content",
            "https://example.com/a.jpg?token=2": b"same image content",
        }
    )
    processor = ImageProcessor(network_manager, tmp_path, Console())
    processor.DELAY_MIN = 0
    processor.DELAY_MAX = 0

    assert (
        processor._download_single_image((0, "https://example.com/a.jpg?token=1")) == 0
    )
    assert (
        processor._download_single_image((1, "https://example.com/a.jpg?token=2")) == 0
    )

    saved_files = list(tmp_path.glob("*.jpg"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"same image content"


def test_download_single_image_skips_existing_file(tmp_path):
    """測試續傳時已存在的圖片不會重新下載"""

    class FailingNetworkManager:
        def request_with_retry(self, url):
            raise AssertionError("已存在的檔案不應發出網路請求")

    existing_file = tmp_path / "0.jpg"
    existing_file.write_bytes(b"already downloaded")

    processor = ImageProcessor(FailingNetworkManager(), tmp_path, Console())
    processor.DELAY_MIN = 0
    processor.DELAY_MAX = 0

    assert processor._download_single_image((0, "https://example.com/a.jpg")) == 0
    assert existing_file.read_bytes() == b"already downloaded"


def test_load_existing_hashes_keeps_dedup_across_resume(tmp_path):
    """測試續傳時會載入既有圖片雜湊，避免重複內容再次寫入"""
    (tmp_path / "0.jpg").write_bytes(b"same image content")

    network_manager = MockNetworkManager(
        {"https://example.com/b.jpg": b"same image content"}
    )
    processor = ImageProcessor(network_manager, tmp_path, Console())
    processor.DELAY_MIN = 0
    processor.DELAY_MAX = 0
    processor._load_existing_hashes()

    assert processor._download_single_image((1, "https://example.com/b.jpg")) == 0
    assert not (tmp_path / "1.jpg").exists()


def test_process_images_returns_completion_status(tmp_path):
    """測試 process_images 回傳是否全部完成"""
    network_manager = MockNetworkManager(
        {
            "https://example.com/1.jpg": b"image one",
            "https://example.com/2.jpg": b"image two",
        }
    )
    processor = ImageProcessor(network_manager, tmp_path, Console())
    processor.DELAY_MIN = 0
    processor.DELAY_MAX = 0

    assert (
        processor.process_images(
            ["https://example.com/1.jpg", "https://example.com/2.jpg"]
        )
        is True
    )
    assert (tmp_path / "0.jpg").read_bytes() == b"image one"
    assert (tmp_path / "1.jpg").read_bytes() == b"image two"


def test_process_images_reports_failures(tmp_path):
    """測試下載失敗時 process_images 回傳 False 且回報剩餘項目"""

    class PartialNetworkManager:
        def request_with_retry(self, url):
            if "bad" in url:
                return None
            return MockResponse(b"good image")

    processor = ImageProcessor(PartialNetworkManager(), tmp_path, Console())
    processor.DELAY_MIN = 0
    processor.DELAY_MAX = 0

    saved_progress = []
    processor.progress_callback = saved_progress.append

    result = processor.process_images(
        ["https://example.com/good.jpg", "https://example.com/bad.jpg"]
    )

    assert result is False
    assert (tmp_path / "0.jpg").exists()
    assert not (tmp_path / "1.jpg").exists()
    # 最後一次回報的剩餘清單應只包含失敗的項目
    assert saved_progress[-1] == [(1, "https://example.com/bad.jpg")]
