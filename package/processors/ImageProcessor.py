"""
@author: PC
Update Time: 2025-03-22
圖片處理器 - 負責處理圖片的下載
"""

import hashlib
import os
import random
import time
from threading import Lock

from .BaseProcessor import BaseProcessor


class ImageProcessor(BaseProcessor):
    """圖片處理器，繼承自 BaseProcessor"""

    # 批次處理常數
    BATCH_SIZE = 50
    DELAY_MIN = 0.2
    DELAY_MAX = 0.5

    def __init__(self, network_manager, path, console):
        """
        初始化圖片處理器

        參數:
            network_manager: 網路管理器物件
            path: 保存路徑
            console: 控制台物件
        """
        super().__init__(network_manager, path, console)
        self.seen_image_hashes = set()
        self.hash_lock = Lock()

    def process(self, urls):
        """
        實作抽象方法 - 處理圖片下載

        參數:
            urls: 圖片 URL 列表
        """
        self.process_images(urls)

    def process_images(self, image_urls):
        """
        處理圖片URL列表

        參數:
            image_urls: 圖片URL列表

        返回:
            全部圖片皆下載完成返回 True，否則返回 False
        """
        if not image_urls:
            self.console.print("沒有找到圖片URL")
            return True

        # 以 (索引, URL) 形式記錄，索引同時作為檔名，支援續傳跳過
        unique_urls = self._deduplicate_urls(image_urls)
        self.todo_list = list(enumerate(unique_urls))

        duplicate_count = len(image_urls) - len(self.todo_list)
        if duplicate_count > 0:
            self.console.print(f"已略過 {duplicate_count} 個重複圖片URL")

        self.console.print(f"偵測到 {len(self.todo_list)} 個圖片")

        # 續傳時：載入既有圖片的內容雜湊，維持跨執行的內容去重
        self._load_existing_hashes()

        # 使用基礎類別的批次下載功能
        failed_items = self.batch_download(
            todo_list=self.todo_list,
            download_func=self._download_single_image,
            batch_size=self.BATCH_SIZE,
            desc="圖片下載進度",
        )

        success_count = len(self.todo_list) - len(failed_items)
        self.console.print(
            f"圖片下載完成，共完成 {success_count}/{len(self.todo_list)} 張圖片"
        )
        if failed_items:
            self.console.print(
                f"[yellow]有 {len(failed_items)} 張圖片下載失敗，"
                f"重新執行（建議加上 -a）即可續傳[/yellow]"
            )
        return not failed_items

    def _load_existing_hashes(self):
        """載入儲存目錄中既有圖片的內容雜湊（續傳時維持內容去重）"""
        try:
            file_names = os.listdir(self.path)
        except OSError:
            return

        for file_name in file_names:
            if not file_name.endswith(".jpg"):
                continue
            file_path = os.path.join(self.path, file_name)
            try:
                with open(file_path, "rb") as f:
                    content_hash = hashlib.sha256(f.read()).hexdigest()
                self.seen_image_hashes.add(content_hash)
            except OSError:
                continue

    def _download_single_image(self, item):
        """
        下載單個圖片（供 batch_download 調用）

        參數:
            item: (索引, URL) 元組，索引作為圖片檔名

        返回:
            成功返回 0，失敗返回 -1
        """
        index, url = item
        file_path = os.path.join(self.path, f"{index}.jpg")

        # 續傳時：圖片已存在則跳過（檔案以原子改名寫入，存在即代表完整）
        if os.path.exists(file_path):
            return 0

        try:
            # 添加輕微隨機延遲，模擬更自然的人類行為
            time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))

            # 使用重試機制下載
            res = self.network_manager.request_with_retry(url)
            if res:
                content_hash = hashlib.sha256(res.content).hexdigest()
                with self.hash_lock:
                    if content_hash in self.seen_image_hashes:
                        return 0
                    self.seen_image_hashes.add(content_hash)

                # 先寫入暫存檔再原子改名，避免中斷時留下不完整的圖片
                temp_path = file_path + ".tmp"
                with open(temp_path, "wb") as f:
                    f.write(res.content)
                os.replace(temp_path, file_path)
                return 0
        except Exception as e:
            self.console.print(f"處理圖片檔案錯誤: {type(e).__name__}: {str(e)}")
        return -1

    @staticmethod
    def _deduplicate_urls(image_urls):
        """按原始順序移除重複圖片 URL。"""
        unique_urls = []
        seen_urls = set()

        for url in image_urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            unique_urls.append(url)

        return unique_urls
