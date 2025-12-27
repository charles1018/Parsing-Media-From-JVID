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
    """網路管理器，處理所有網路請求和重試邏輯"""

    # 請求間隔常數
    DEFAULT_TIMEOUT = 20
    DEFAULT_MIN_REQUEST_INTERVAL = 0.5
    INTERVAL_JITTER_MAX = 0.5
    MAX_REQUEST_INTERVAL = 4.0
    INTERVAL_MULTIPLIER = 1.5

    # 限流和錯誤處理常數
    RATE_LIMIT_WAIT_MIN = 30
    RATE_LIMIT_WAIT_MAX = 60
    FORBIDDEN_WAIT_MIN = 15
    FORBIDDEN_WAIT_MAX = 30
    SERVER_ERROR_WAIT_MIN = 5
    SERVER_ERROR_WAIT_MAX = 15

    # 重試相關常數
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 1.5
    BACKOFF_JITTER_MIN = 0.5
    BACKOFF_JITTER_MAX = 1.5
    UA_CHANGE_PROBABILITY = 0.1  # 每次請求更換 UA 的機率

    def __init__(
        self, headers=None, timeout=None, min_request_interval=None, console=None
    ):
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
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self.min_request_interval = (
            min_request_interval
            if min_request_interval is not None
            else self.DEFAULT_MIN_REQUEST_INTERVAL
        )
        self.last_request_time = 0
        self.console = console

    def throttle_request(self):
        """控制請求頻率，避免過快請求"""
        now = time.time()
        elapsed = now - self.last_request_time

        # 加入隨機成分，使請求間隔更自然
        target_interval = self.min_request_interval + random.uniform(
            0, self.INTERVAL_JITTER_MAX
        )

        if elapsed < target_interval:
            sleep_time = target_interval - elapsed
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def handle_response_status(self, status_code, url):
        """根據狀態碼處理不同的錯誤情況"""
        if status_code == 429:  # Too Many Requests
            # 遇到限流，大幅增加等待時間
            wait_time = random.uniform(
                self.RATE_LIMIT_WAIT_MIN, self.RATE_LIMIT_WAIT_MAX
            )
            if self.console:
                self.console.print(f"遇到限流 (429)，暫停 {wait_time:.1f} 秒: {url}")
            # 動態增加最小請求間隔
            self.min_request_interval = min(
                self.min_request_interval * self.INTERVAL_MULTIPLIER,
                self.MAX_REQUEST_INTERVAL,
            )
            time.sleep(wait_time)
            # 更換 User-Agent
            if "user-agent" in self.headers:
                self.headers["user-agent"] = self.get_random_user_agent()
            return False

        elif status_code == 403:  # Forbidden
            # 可能被識別為爬蟲，更換 UA 並延長等待
            wait_time = random.uniform(self.FORBIDDEN_WAIT_MIN, self.FORBIDDEN_WAIT_MAX)
            if self.console:
                self.console.print(f"請求被禁止 (403)，暫停 {wait_time:.1f} 秒: {url}")
            time.sleep(wait_time)
            # 更換 User-Agent
            if "user-agent" in self.headers:
                self.headers["user-agent"] = self.get_random_user_agent()
            return False

        elif status_code >= 500:  # Server errors
            # 服務器錯誤，短時間等待後重試
            wait_time = random.uniform(
                self.SERVER_ERROR_WAIT_MIN, self.SERVER_ERROR_WAIT_MAX
            )
            if self.console:
                self.console.print(
                    f"服務器錯誤 ({status_code})，等待 {wait_time:.1f} 秒後重試: {url}"
                )
            time.sleep(wait_time)
            return False

        return True  # 其他情況，例如200，直接繼續

    def request_with_retry(self, url, max_retries=None, backoff_factor=None):
        """
        實現請求重試機制，使用指數退避策略

        參數:
            url: 請求的URL
            max_retries: 最大重試次數（預設使用 DEFAULT_MAX_RETRIES）
            backoff_factor: 退避係數，用於計算重試間隔時間（預設使用 DEFAULT_BACKOFF_FACTOR）

        返回:
            成功時返回 Response 物件，失敗時返回 None
        """
        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        if backoff_factor is None:
            backoff_factor = self.DEFAULT_BACKOFF_FACTOR

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

                # 每次請求隨機更換 User-Agent
                if (
                    "user-agent" in self.headers
                    and random.random() < self.UA_CHANGE_PROBABILITY
                ):
                    self.headers["user-agent"] = self.get_random_user_agent()

                # 發起請求
                res = self.session.get(
                    current_url, headers=self.headers, timeout=self.timeout
                )

                # 處理狀態碼
                if res.status_code == 200:
                    return res

                # 處理非200狀態碼
                if not self.handle_response_status(res.status_code, current_url):
                    # 如果特殊處理了狀態碼，嘗試使用相同URL重試
                    continue

                # 一般的非200狀態碼處理
                if self.console:
                    self.console.print(
                        f"下載失敗，狀態碼: {res.status_code}，URL: {current_url}"
                    )

            except (requests.exceptions.RequestException, TimeoutError) as e:
                last_exception = e
                if self.console:
                    self.console.print(f"下載異常: {type(e).__name__}: {str(e)}")

            # 計算退避時間並等待
            retries += 1
            if retries < max_retries:  # 只有在還有重試機會時才等待
                # 加入隨機因素，使退避時間更自然
                jitter = random.uniform(
                    self.BACKOFF_JITTER_MIN, self.BACKOFF_JITTER_MAX
                )
                wait_time = backoff_factor * (2 ** (retries - 1)) * jitter
                if self.console:
                    self.console.print(
                        f"第 {retries} 次重試失敗，{wait_time:.1f} 秒後重試: {current_url}"
                    )
                time.sleep(wait_time)

                # 更換 User-Agent
                if "user-agent" in self.headers:
                    self.headers["user-agent"] = self.get_random_user_agent()

        # 所有重試都失敗
        if last_exception and self.console:
            self.console.print(f"達到最大重試次數 {max_retries}，下載失敗: {url}")
        return None

    @staticmethod
    def get_random_user_agent():
        """生成隨機 User-Agent 以減少被識別為爬蟲的風險"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        ]
        return random.choice(user_agents)
