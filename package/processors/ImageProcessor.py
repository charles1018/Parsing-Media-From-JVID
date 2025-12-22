# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
圖片處理器 - 負責處理圖片的下載
"""
import os
import random
import time
from threading import Lock
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImageProcessor:
    def __init__(self, network_manager, path, console):
        """
        初始化圖片處理器
        
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
        self.MAX_WORKERS = 1  # 預設使用單執行緒以確保下載完整性
    
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
        
        # 下載圖片
        self.download_images()
        
        return self.count
    
    def download_images(self):
        """下載所有圖片"""
        # 使用設定的執行緒數量（已通過 Lock 確保執行緒安全）
        current_workers = self.MAX_WORKERS

        self.console.print(f"開始下載圖片，執行緒數: {current_workers}")
        
        # 創建進度條
        schedule = tqdm(total=len(self.todo_list), desc='圖片下載進度: ')
        
        # 批次處理，避免一次提交所有任務導致記憶體問題
        todo_chunks = [self.todo_list[i:i+50] for i in range(0, len(self.todo_list), 50)]
        
        for chunk_index, current_chunk in enumerate(todo_chunks):
            with ThreadPoolExecutor(max_workers=current_workers) as executor:
                # 提交當前批次的任務
                future_to_url = {executor.submit(self.create_image, url): url for url in current_chunk}
                
                # 處理完成的任務
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        # 獲取任務結果
                        ret = future.result(timeout=20)
                        if ret == 0:  # 成功
                            schedule.update(1)
                    except Exception as e:
                        self.console.print(f"處理圖片時出錯: {type(e).__name__}: {str(e)}")
            
            # 顯示批次完成情況
            if chunk_index < len(todo_chunks) - 1:
                self.console.print(f"批次 {chunk_index+1}/{len(todo_chunks)} 完成")
                # 批次之間的間隔，模擬人類瀏覽行為
                wait_time = random.uniform(1.0, 2.0)
                time.sleep(wait_time)
        
        # 完成進度條            
        schedule.close()
        
        self.console.print(f"圖片下載完成，共下載 {self.count} 張圖片")
    
    def create_image(self, url):
        """
        下載單個圖片

        參數:
            url: 圖片URL

        返回:
            成功返回 0，失敗返回 -1
        """
        ret = -1
        try:
            # 添加輕微隨機延遲，模擬更自然的人類行為
            time.sleep(random.uniform(0.2, 0.5))

            # 使用重試機制下載
            res = self.network_manager.request_with_retry(url)
            if res:
                # 使用鎖保護計數器，確保執行緒安全
                with self.count_lock:
                    current_count = self.count
                    self.count += 1

                file_path = os.path.join(self.path, f'{current_count}.jpg')
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                ret = 0
        except Exception as e:
            self.console.print(f"處理圖片檔案錯誤: {type(e).__name__}: {str(e)}")
        return ret