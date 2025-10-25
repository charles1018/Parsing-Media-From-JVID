# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
網路管理器 - 負責處理所有網路請求和重試邏輯
"""
import time
import random
import requests

class NetworkManager:
    def __init__(self, headers=None, timeout=20, min_request_interval=0.5, console=None):
        """
        初始化網路管理器
        
        參數:
            headers: 請求頭
            timeout: 請求超時時間(秒)
            min_request_interval: 最小請求間隔(秒)
            console: 控制台物件，用於輸出訊息
        """
        self.session = requests.Session()
        self.headers = headers or {}
        self.timeout = timeout
        self.min_request_interval = min_request_interval
        self.last_request_time = 0
        self.console = console
        
    def throttle_request(self):
        """控制請求頻率，避免過快請求"""
        now = time.time()
        elapsed = now - self.last_request_time
        
        # 加入隨機成分，使請求間隔更自然
        target_interval = self.min_request_interval + random.uniform(0, 0.5)
        
        if elapsed < target_interval:
            sleep_time = target_interval - elapsed
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def handle_response_status(self, status_code, url):
        """根據狀態碼處理不同的錯誤情況"""
        if status_code == 429:  # Too Many Requests
            # 遇到限流，大幅增加等待時間
            wait_time = random.uniform(30, 60)
            if self.console:
                self.console.print(f"遇到限流 (429)，暫停 {wait_time:.1f} 秒: {url}")
            # 動態增加最小請求間隔
            self.min_request_interval = min(self.min_request_interval * 1.5, 4.0)
            time.sleep(wait_time)
            # 更換 User-Agent
            if 'user-agent' in self.headers:
                self.headers['user-agent'] = self.get_random_user_agent()
            return False
            
        elif status_code == 403:  # Forbidden
            # 可能被識別為爬蟲，更換 UA 並延長等待
            wait_time = random.uniform(15, 30)
            if self.console:
                self.console.print(f"請求被禁止 (403)，暫停 {wait_time:.1f} 秒: {url}")
            time.sleep(wait_time)
            # 更換 User-Agent
            if 'user-agent' in self.headers:
                self.headers['user-agent'] = self.get_random_user_agent()
            return False
            
        elif status_code >= 500:  # Server errors
            # 服務器錯誤，短時間等待後重試
            wait_time = random.uniform(5, 15)
            if self.console:
                self.console.print(f"服務器錯誤 ({status_code})，等待 {wait_time:.1f} 秒後重試: {url}")
            time.sleep(wait_time)
            return False
            
        return True  # 其他情況，例如200，直接繼續
    
    def request_with_retry(self, url, max_retries=3, backoff_factor=1.5):
        """
        實現請求重試機制，使用指數退避策略
        
        參數:
            url: 請求的URL
            max_retries: 最大重試次數
            backoff_factor: 退避係數，用於計算重試間隔時間
            
        返回:
            成功時返回 Response 物件，失敗時返回 None
        """
        retries = 0
        last_exception = None
        
        # 不同域名的重試嘗試
        attempted_urls = set()
        attempted_urls.add(url)
        current_url = url
        
        while retries < max_retries:
            try:
                # 控制請求速率
                self.throttle_request()
                
                # 每次請求隨機更換 User-Agent (10%機率)
                if 'user-agent' in self.headers and random.random() < 0.1:
                    self.headers['user-agent'] = self.get_random_user_agent()
                
                # 發起請求
                res = self.session.get(current_url, headers=self.headers, timeout=self.timeout)
                
                # 處理狀態碼
                if res.status_code == 200:
                    return res
                    
                # 處理非200狀態碼
                if not self.handle_response_status(res.status_code, current_url):
                    # 如果特殊處理了狀態碼，嘗試使用相同URL重試
                    continue
                    
                # 一般的非200狀態碼處理
                if self.console:
                    self.console.print(f"下載失敗，狀態碼: {res.status_code}，URL: {current_url}")
                
            except (requests.exceptions.RequestException, TimeoutError) as e:
                last_exception = e
                if self.console:
                    self.console.print(f"下載異常: {type(e).__name__}: {str(e)}")
            
            # 計算退避時間並等待
            retries += 1
            if retries < max_retries:  # 只有在還有重試機會時才等待
                # 加入隨機因素，使退避時間更自然
                jitter = random.uniform(0.5, 1.5)
                wait_time = backoff_factor * (2 ** (retries - 1)) * jitter
                if self.console:
                    self.console.print(f"第 {retries} 次重試失敗，{wait_time:.1f} 秒後重試: {current_url}")
                time.sleep(wait_time)
                
                # 更換 User-Agent
                if 'user-agent' in self.headers:
                    self.headers['user-agent'] = self.get_random_user_agent()
        
        # 所有重試都失敗
        if last_exception and self.console:
            self.console.print(f"達到最大重試次數 {max_retries}，下載失敗: {url}")
        return None
    
    @staticmethod
    def get_random_user_agent():
        """生成隨機 User-Agent 以減少被識別為爬蟲的風險"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)