"""
ContentDetector 單元測試
使用 pytest 框架測試 ContentDetector 的各項功能
"""

import pytest
from bs4 import BeautifulSoup

from package.utils.ContentDetector import ContentDetector


class TestDetectContentTypes:
    """測試 detect_content_types 方法"""

    @pytest.fixture
    def detector(self):
        """建立 ContentDetector 實例"""
        return ContentDetector()

    def test_detect_content_types_video_m3u8(self, detector):
        """測試偵測包含 m3u8 的影片內容"""
        html = """
        <html>
            <body>
                <div>https://example.com/video.m3u8</div>
            </body>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is True
        assert has_image is False

    def test_detect_content_types_video_transcode(self, detector):
        """測試偵測包含 transcode 的影片內容"""
        html = """
        <html>
            <head>
                <meta content="https://transcode.example.com/video.mp4">
            </head>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is True
        assert has_image is False

    def test_detect_content_types_video_playlist(self, detector):
        """測試偵測包含 playList 的影片內容"""
        html = """
        <html>
            <script>var playList = ["video1.ts", "video2.ts"];</script>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is True
        assert has_image is False

    def test_detect_content_types_video_vidsrc(self, detector):
        """測試偵測包含 vidSrc 的影片內容"""
        html = """
        <html>
            <script>vidSrc = "https://example.com/video.m3u8";</script>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is True
        assert has_image is False

    def test_detect_content_types_image(self, detector):
        """測試偵測圖片內容"""
        html = """
        <html>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image1.jpg"></div>
                    <div data-src="https://example.com/image2.jpg"></div>
                </div>
            </body>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is False
        assert has_image is True

    def test_detect_content_types_both(self, detector):
        """測試同時有影片和圖片"""
        html = """
        <html>
            <head>
                <meta content="https://transcode.example.com/video.mp4">
            </head>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image1.jpg"></div>
                </div>
            </body>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is True
        assert has_image is True

    def test_detect_content_types_none(self, detector):
        """測試空白頁面（沒有影片和圖片）"""
        html = """
        <html>
            <body>
                <div>Hello World</div>
            </body>
        </html>
        """
        has_video, has_image = detector.detect_content_types(html)
        assert has_video is False
        assert has_image is False

    def test_detect_content_types_with_soup(self, detector):
        """測試傳入已解析的 BeautifulSoup 物件"""
        html = """
        <html>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image.jpg"></div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        has_video, has_image = detector.detect_content_types(html, soup=soup)
        assert has_video is False
        assert has_image is True


class TestExtractVideoUrls:
    """測試 extract_video_urls 方法"""

    @pytest.fixture
    def detector(self):
        """建立 ContentDetector 實例"""
        return ContentDetector()

    def test_extract_video_urls_meta_transcode(self, detector):
        """測試從 meta 標籤提取 transcode URL"""
        html = """
        <html>
            <head>
                <meta content="https://transcode.example.com/video1.m3u8">
                <meta content="https://transcode.example.com/video2.m3u8">
            </head>
        </html>
        """
        video_urls, video_types = detector.extract_video_urls(html)
        assert len(video_urls) >= 2
        assert "meta_transcode" in video_types

    def test_extract_video_urls_div_m3u8(self, detector):
        """測試從 div 元素提取 m3u8 URL"""
        html = """
        <html>
            <body>
                <div class="w-full">
                    m3u8 playList transcode_video
                    vidSrc=https://example.com/video.m3u8
                </div>
            </body>
        </html>
        """
        video_urls, video_types = detector.extract_video_urls(html)
        assert len(video_urls) >= 1
        # 應該找到 div_m3u8_playlist 或 direct_regex_m3u8 類型
        assert any(
            t in video_types for t in ["div_m3u8_playlist", "direct_regex_m3u8"]
        )

    def test_extract_video_urls_regex(self, detector):
        """測試正則表達式提取 m3u8 URL"""
        html = """
        <html>
            <body>
                <script>
                    var url = "https://cdn.example.com/stream/video.m3u8";
                </script>
            </body>
        </html>
        """
        video_urls, video_types = detector.extract_video_urls(html)
        assert len(video_urls) >= 1
        assert "https://cdn.example.com/stream/video.m3u8" in video_urls
        assert "direct_regex_m3u8" in video_types

    def test_extract_video_urls_no_duplicates(self, detector):
        """測試不會產生重複的 URL"""
        html = """
        <html>
            <head>
                <meta content="https://transcode.example.com/video.m3u8">
            </head>
            <body>
                <div>https://transcode.example.com/video.m3u8</div>
            </body>
        </html>
        """
        video_urls, video_types = detector.extract_video_urls(html)
        # 檢查 URL 不重複
        assert len(video_urls) == len(set(video_urls))

    def test_extract_video_urls_empty(self, detector):
        """測試空白頁面不會提取任何 URL"""
        html = """
        <html>
            <body>
                <div>No video here</div>
            </body>
        </html>
        """
        video_urls, video_types = detector.extract_video_urls(html)
        assert len(video_urls) == 0
        assert len(video_types) == 0

    def test_extract_video_urls_with_soup(self, detector):
        """測試傳入已解析的 BeautifulSoup 物件"""
        html = """
        <html>
            <head>
                <meta content="https://transcode.example.com/video.m3u8">
            </head>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        video_urls, video_types = detector.extract_video_urls(html, soup=soup)
        assert len(video_urls) >= 1


class TestExtractImageUrls:
    """測試 extract_image_urls 方法"""

    @pytest.fixture
    def detector(self):
        """建立 ContentDetector 實例"""
        return ContentDetector()

    def test_extract_image_urls_basic(self, detector):
        """測試基本圖片 URL 提取"""
        html = """
        <html>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image1.jpg"></div>
                    <div data-src="https://example.com/image2.jpg"></div>
                    <div data-src="https://example.com/image3.jpg"></div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        image_urls = detector.extract_image_urls(soup)
        assert len(image_urls) == 3
        assert "https://example.com/image1.jpg" in image_urls
        assert "https://example.com/image2.jpg" in image_urls
        assert "https://example.com/image3.jpg" in image_urls

    def test_extract_image_urls_empty(self, detector):
        """測試沒有圖片的頁面"""
        html = """
        <html>
            <body>
                <div>No images here</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        image_urls = detector.extract_image_urls(soup)
        assert len(image_urls) == 0

    def test_extract_image_urls_non_https(self, detector):
        """測試過濾非 https 開頭的 URL"""
        html = """
        <html>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image1.jpg"></div>
                    <div data-src="http://example.com/image2.jpg"></div>
                    <div data-src="/relative/image3.jpg"></div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        image_urls = detector.extract_image_urls(soup)
        # 只有 https 開頭的 URL 應該被提取
        assert len(image_urls) == 1
        assert "https://example.com/image1.jpg" in image_urls

    def test_extract_image_urls_no_lightbox_class(self, detector):
        """測試沒有 lightbox_fancybox 類別的頁面"""
        html = """
        <html>
            <body>
                <div class="w-full other-class">
                    <div data-src="https://example.com/image.jpg"></div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        image_urls = detector.extract_image_urls(soup)
        assert len(image_urls) == 0

    def test_extract_image_urls_missing_data_src(self, detector):
        """測試處理缺少 data-src 屬性的元素"""
        html = """
        <html>
            <body>
                <div class="w-full lightbox_fancybox">
                    <div data-src="https://example.com/image1.jpg"></div>
                    <div>No data-src attribute</div>
                    <div data-src="">Empty data-src</div>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, "html.parser")
        image_urls = detector.extract_image_urls(soup)
        # 只有有效的 https URL 應該被提取
        assert len(image_urls) == 1
        assert "https://example.com/image1.jpg" in image_urls
