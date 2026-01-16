"""
Cookie Manager - 自動讀取和管理 JVID cookies
@author: Charles
@created: 2025
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple


class CookieManager:
    """管理 JVID cookies 的讀取和解析"""

    # 支援的 cookie 文件名稱模式（按優先順序排列）
    COOKIE_FILENAMES = [
        "www.jvid.com_cookies.json",
        "jvid_cookies.json",
        "cookies.json",
        "cookies.txt",  # Netscape HTTP Cookie File 格式
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

        搜索順序：
        1. 根目錄 (base_path/)
        2. cookies 子目錄 (base_path/cookies/)

        Returns:
            找到的 cookie 文件路徑，若無則返回 None
        """
        # 搜索位置列表
        search_paths = [
            self.base_path,  # 根目錄（用於本地開發）
            self.base_path / "cookies",  # cookies 子目錄（用於 Docker）
        ]

        for search_path in search_paths:
            for filename in self.COOKIE_FILENAMES:
                cookie_path = search_path / filename
                if cookie_path.exists():
                    return cookie_path
        return None

    def _parse_netscape_cookies(self, content: str, domain_filter: str = "jvid.com") -> list:
        """
        解析 Netscape HTTP Cookie File 格式（cookies.txt）

        格式說明：
        - 以 # 開頭的行是註解
        - 每行以 TAB 分隔，包含 7 個欄位
        - 欄位順序：domain, flag, path, secure, expiration, name, value

        Args:
            content: cookies.txt 文件內容
            domain_filter: 只保留包含此字串的網域 cookies（預設為 "jvid.com"）

        Returns:
            cookie 字典列表，格式與 JSON 格式一致
        """
        cookies = []
        for line in content.splitlines():
            line = line.strip()
            # 跳過空行和註解
            if not line or line.startswith("#"):
                continue

            # 按 TAB 分割欄位
            fields = line.split("\t")
            if len(fields) >= 7:
                domain, flag, path, secure, expiration, name, value = fields[:7]

                # 過濾網域：只保留符合條件的 cookies
                if domain_filter and domain_filter not in domain:
                    continue

                cookies.append(
                    {
                        "domain": domain,
                        "hostOnly": flag.upper() != "TRUE",
                        "path": path,
                        "secure": secure.upper() == "TRUE",
                        "expirationDate": int(expiration) if expiration.isdigit() else 0,
                        "name": name,
                        "value": value,
                    }
                )
        return cookies

    def load_cookies(self) -> Optional[list]:
        """
        載入 cookie 文件內容

        支援格式：
        - JSON 格式 (.json)
        - Netscape HTTP Cookie File 格式 (.txt)

        Returns:
            cookie 列表，若載入失敗則返回 None
        """
        cookie_file = self.find_cookie_file()
        if not cookie_file:
            return None

        try:
            with open(cookie_file, encoding="utf-8") as f:
                content = f.read()

            # 根據副檔名決定解析方式
            if cookie_file.suffix.lower() == ".txt":
                cookies = self._parse_netscape_cookies(content)
            else:
                # 預設為 JSON 格式
                cookies = json.loads(content)

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
            if cookie.get("name") == "auth":
                try:
                    # 解析 auth cookie 的值
                    auth_value = cookie.get("value", "")
                    # URL decode
                    import urllib.parse

                    auth_data = urllib.parse.unquote(auth_value)
                    # 解析 JSON
                    auth_json = json.loads(auth_data)
                    auth_token = auth_json.get("token")
                    break
                except Exception as e:
                    print(f"警告: 無法解析 auth cookie: {e}")

        # 構建完整的 cookie 字串
        cookie_string = "; ".join(
            [
                f"{cookie['name']}={cookie['value']}"
                for cookie in cookies
                if cookie.get("name") and cookie.get("value")
            ]
        )

        return auth_token, cookie_string

    def get_headers(self, user_agent: str) -> Dict[str, str]:
        """
        獲取包含認證資訊的完整請求頭

        Args:
            user_agent: User-Agent 字串

        Returns:
            包含所有必要認證資訊的 headers 字典
        """
        headers = {"user-agent": user_agent}

        # 載入 cookies
        cookies = self.load_cookies()
        if not cookies:
            print("⚠️  警告: 未找到 cookie 文件，將使用基本請求頭")
            return headers

        # 提取認證資訊
        auth_token, cookie_string = self.extract_auth_info(cookies)

        if auth_token:
            headers["authorization"] = f"Bearer {auth_token}"
        else:
            print("⚠️  警告: 未能提取 authorization token")

        if cookie_string:
            headers["cookie"] = cookie_string
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
        print("\n" + "=" * 60)
        print("[Authentication] 認證資訊摘要")
        print("=" * 60)

        if "authorization" in headers:
            token = headers["authorization"]
            # 只顯示 token 的前後部分
            if len(token) > 30:
                display_token = f"{token[:20]}...{token[-10:]}"
            else:
                display_token = token
            print(f"[OK] Authorization: {display_token}")
        else:
            print("[MISSING] Authorization: 未設定")

        if "cookie" in headers:
            # 計算 cookie 數量
            cookie_count = len(headers["cookie"].split("; "))
            print(f"[OK] Cookies: 已載入 {cookie_count} 個 cookies")
        else:
            print("[MISSING] Cookies: 未設定")

        print("=" * 60 + "\n")
