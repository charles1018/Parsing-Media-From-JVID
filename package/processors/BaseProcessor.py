"""
@author: PC
Update Time: 2025-03-22
基礎處理器 - 提供影片和圖片處理器的共用功能
"""

import random
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from tqdm import tqdm


class BaseProcessor(ABC):
    """處理器基礎類別，提供共用的批次下載功能"""

    # 執行緒和批次處理常數
    DEFAULT_MAX_WORKERS = 1
    DEFAULT_BATCH_SIZE = 100
    TASK_TIMEOUT = 20

    # 批次間隔常數
    BATCH_WAIT_MIN = 1.0
    BATCH_WAIT_MAX = 3.0

    def __init__(self, network_manager, path, console):
        """
        初始化基礎處理器

        參數:
            network_manager: 網路管理器物件
            path: 保存路徑
            console: 控制台物件
        """
        self.network_manager = network_manager
        self.path = path
        self.console = console
        self.count = 0
        self.count_lock = Lock()  # 保護計數器的執行緒鎖
        self.todo_list = []
        self.MAX_WORKERS = self.DEFAULT_MAX_WORKERS

    def batch_download(
        self, todo_list, download_func, batch_size=None, desc="下載進度"
    ):
        """
        通用批次下載邏輯

        參數:
            todo_list: 待下載項目列表
            download_func: 下載單個項目的函數
            batch_size: 每批次處理的數量（預設使用 DEFAULT_BATCH_SIZE）
            desc: 進度條描述文字
        """
        if batch_size is None:
            batch_size = self.DEFAULT_BATCH_SIZE

        # 使用設定的執行緒數量
        current_workers = self.MAX_WORKERS

        self.console.print(f"開始下載，執行緒數: {current_workers}")

        # 創建進度條
        schedule = tqdm(total=len(todo_list), desc=desc)

        # 批次處理，避免一次提交所有任務導致記憶體問題
        todo_chunks = [
            todo_list[i : i + batch_size] for i in range(0, len(todo_list), batch_size)
        ]

        for chunk_index, current_chunk in enumerate(todo_chunks):
            with ThreadPoolExecutor(max_workers=current_workers) as executor:
                # 提交當前批次的任務
                future_to_item = {
                    executor.submit(download_func, item): item for item in current_chunk
                }

                # 處理完成的任務
                for future in as_completed(future_to_item):
                    try:
                        # 獲取任務結果
                        ret = future.result(timeout=self.TASK_TIMEOUT)
                        if ret == 0:  # 成功
                            schedule.update(1)
                    except Exception as e:
                        self.console.print(
                            f"處理任務時出錯: {type(e).__name__}: {str(e)}"
                        )

            # 顯示批次完成情況
            if chunk_index < len(todo_chunks) - 1:
                self.console.print(f"批次 {chunk_index + 1}/{len(todo_chunks)} 完成")
                # 批次之間的間隔，模擬人類瀏覽行為
                wait_time = random.uniform(self.BATCH_WAIT_MIN, self.BATCH_WAIT_MAX)
                self.console.print(f"休息 {wait_time:.1f} 秒以避免限流...")
                time.sleep(wait_time)

        # 完成進度條
        schedule.close()

    def get_next_count(self):
        """
        執行緒安全地取得下一個計數值

        返回:
            當前計數值（取得後計數器會自動加 1）
        """
        with self.count_lock:
            current_count = self.count
            self.count += 1
        return current_count

    @abstractmethod
    def process(self, urls):
        """
        處理下載項目（子類別必須實作）

        參數:
            urls: 待處理的 URL 列表
        """
        pass
