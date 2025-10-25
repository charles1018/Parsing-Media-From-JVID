# -*- coding: utf-8 -*-
"""
Cookie Manager - 自動讀取和管理 JVID cookies
@author: Charles
@created: 2025
"""
import json
import os
from typing import Dict, Optional, Tuple
from pathlib import Path


class CookieManager:
    """管理 JVID cookies 的讀取和解析"""
    
    # 支援的 cookie 文件名稱模式
    COOKIE_FILENAMES = [
        'www.jvid.com_cookies.json',
        'jvid_cookies.json',
        'cookies.json'
    ]
    
    def __init__(self, base_path: Optional[str] = None):
        """
        初始化 Cookie Manager
        
        Args:
            base_path: 專案根目錄路徑，預設為當前工作目錄
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    def find_cookie_file(self) -> Optional[Path]:
        """
        在專案目錄中尋找 cookie 文件
        
        Returns:
            找到的 cookie 文件路徑，若無則返回 None
        """
        for filename in self.COOKIE_FILENAMES:
            cookie_path = self.base_path / filename
            if cookie_path.exists():
                return cookie_path
        return None
    
    def load_cookies(self) -> Optional[list]:
        """
        載入 cookie 文件內容
        
        Returns:
            cookie 列表，若載入失敗則返回 None
        """
        cookie_file = self.find_cookie_file()
        if not cookie_file:
            return None
            
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            return cookies
        except Exception as e:
            print(f"警告: 無法讀取 cookie 文件: {e}")
            return None
    
    def extract_auth_info(self, cookies: list) -> Tuple[Optional[str], Optional[str]]:
        """
        從 cookie 列表中提取 authorization token 和完整 cookie 字串
        
        Args:
            cookies: cookie 字典列表
            
        Returns:
            (authorization_token, cookie_string) 元組
        """
        if not cookies:
            return None, None
        
        # 提取 auth cookie 中的 token
        auth_token = None
        for cookie in cookies:
            if cookie.get('name') == 'auth':
                try:
                    # 解析 auth cookie 的值
                    auth_value = cookie.get('value', '')
                    # URL decode
                    import urllib.parse
                    auth_data = urllib.parse.unquote(auth_value)
                    # 解析 JSON
                    auth_json = json.loads(auth_data)
                    auth_token = auth_json.get('token')
                    break
                except Exception as e:
                    print(f"警告: 無法解析 auth cookie: {e}")
        
        # 構建完整的 cookie 字串
        cookie_string = '; '.join([
            f"{cookie['name']}={cookie['value']}"
            for cookie in cookies
            if cookie.get('name') and cookie.get('value')
        ])
        
        return auth_token, cookie_string
    
    def get_headers(self, user_agent: str) -> Dict[str, str]:
        """
        獲取包含認證資訊的完整請求頭
        
        Args:
            user_agent: User-Agent 字串
            
        Returns:
            包含所有必要認證資訊的 headers 字典
        """
        headers = {'user-agent': user_agent}
        
        # 載入 cookies
        cookies = self.load_cookies()
        if not cookies:
            print("⚠️  警告: 未找到 cookie 文件，將使用基本請求頭")
            return headers
        
        # 提取認證資訊
        auth_token, cookie_string = self.extract_auth_info(cookies)
        
        if auth_token:
            headers['authorization'] = f'Bearer {auth_token}'
        else:
            print("⚠️  警告: 未能提取 authorization token")
        
        if cookie_string:
            headers['cookie'] = cookie_string
        else:
            print("⚠️  警告: 未能構建 cookie 字串")
        
        return headers
    
    @staticmethod
    def print_cookie_info(headers: Dict[str, str]):
        """
        輸出 cookie 資訊摘要（用於除錯）
        
        Args:
            headers: 請求頭字典
        """
        print("\n" + "="*60)
        print("[Authentication] 認證資訊摘要")
        print("="*60)
        
        if 'authorization' in headers:
            token = headers['authorization']
            # 只顯示 token 的前後部分
            if len(token) > 30:
                display_token = f"{token[:20]}...{token[-10:]}"
            else:
                display_token = token
            print(f"[OK] Authorization: {display_token}")
        else:
            print("[MISSING] Authorization: 未設定")
        
        if 'cookie' in headers:
            # 計算 cookie 數量
            cookie_count = len(headers['cookie'].split('; '))
            print(f"[OK] Cookies: 已載入 {cookie_count} 個 cookies")
        else:
            print("[MISSING] Cookies: 未設定")
        
        print("="*60 + "\n")
