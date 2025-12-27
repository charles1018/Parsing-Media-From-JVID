# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
圖片處理器 - 負責處理圖片的下載
"""
import os
import random
import time

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
            成功下載的圖片數量
        """
        if not image_urls:
            self.console.print("沒有找到圖片URL")
            return 0

        self.todo_list = image_urls
        self.count = 0

        self.console.print(f"偵測到 {len(self.todo_list)} 個圖片")

        # 使用基礎類別的批次下載功能
        self.batch_download(
            todo_list=self.todo_list,
            download_func=self._download_single_image,
            batch_size=self.BATCH_SIZE,
            desc='圖片下載進度'
        )

        self.console.print(f"圖片下載完成，共下載 {self.count} 張圖片")
        return self.count

    def _download_single_image(self, url):
        """
        下載單個圖片（供 batch_download 調用）

        參數:
            url: 圖片URL

        返回:
            成功返回 0，失敗返回 -1
        """
        try:
            # 添加輕微隨機延遲，模擬更自然的人類行為
            time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))

            # 使用重試機制下載
            res = self.network_manager.request_with_retry(url)
            if res:
                # 使用基礎類別的執行緒安全計數器
                current_count = self.get_next_count()

                file_path = os.path.join(self.path, f'{current_count}.jpg')
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                return 0
        except Exception as e:
            self.console.print(f"處理圖片檔案錯誤: {type(e).__name__}: {str(e)}")
        return -1
    
