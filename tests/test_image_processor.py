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

    assert processor._download_single_image("https://example.com/a.jpg?token=1") == 0
    assert processor._download_single_image("https://example.com/a.jpg?token=2") == 0

    saved_files = list(tmp_path.glob("*.jpg"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"same image content"
    assert processor.count == 1
