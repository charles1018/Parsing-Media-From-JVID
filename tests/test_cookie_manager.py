"""
Cookie Manager 單元測試
使用 pytest 框架測試 CookieManager 的各項功能
"""

import json
from pathlib import Path

import pytest

from package.network.NetworkManager import NetworkManager
from package.utils.CookieManager import CookieManager


class TestCookieManager:
    """CookieManager 測試類別"""

    @pytest.fixture
    def sample_cookies(self):
        """提供測試用的 cookie 資料"""
        return [
            {
                "name": "session_id",
                "value": "abc123",
                "domain": ".jvid.com",
                "path": "/",
            },
            {
                "name": "auth_token",
                "value": "test_auth_token_value",
                "domain": ".jvid.com",
                "path": "/",
            },
            {
                "name": "user_pref",
                "value": "dark_mode",
                "domain": ".jvid.com",
                "path": "/",
            },
        ]

    @pytest.fixture
    def cookie_file(self, tmp_path, sample_cookies):
        """建立臨時 cookie 檔案"""
        cookie_path = tmp_path / "www.jvid.com_cookies.json"
        cookie_path.write_text(json.dumps(sample_cookies), encoding="utf-8")
        return cookie_path

    @pytest.fixture
    def cookie_manager(self, tmp_path, cookie_file, monkeypatch):
        """建立設定好的 CookieManager"""
        # 將工作目錄切換到包含 cookie 檔案的目錄
        monkeypatch.chdir(tmp_path)
        return CookieManager()

    def test_find_cookie_file_exists(self, cookie_manager, cookie_file):
        """測試能找到存在的 cookie 檔案"""
        found_file = cookie_manager.find_cookie_file()
        assert found_file is not None
        assert Path(found_file).name == "www.jvid.com_cookies.json"

    def test_find_cookie_file_not_exists(self, tmp_path, monkeypatch):
        """測試找不到 cookie 檔案時返回 None"""
        # 使用空目錄
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)

        manager = CookieManager()
        found_file = manager.find_cookie_file()
        assert found_file is None

    def test_load_cookies_success(self, cookie_manager, sample_cookies):
        """測試成功載入 cookies"""
        cookies = cookie_manager.load_cookies()
        assert cookies is not None
        assert len(cookies) == len(sample_cookies)
        assert cookies[0]["name"] == "session_id"

    def test_load_cookies_invalid_json(self, tmp_path, monkeypatch):
        """測試載入無效 JSON 時的處理"""
        invalid_cookie_path = tmp_path / "www.jvid.com_cookies.json"
        invalid_cookie_path.write_text("invalid json {", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        manager = CookieManager()
        cookies = manager.load_cookies()
        # 應該返回空列表或 None
        assert cookies is None or len(cookies) == 0

    def test_extract_auth_info(self, cookie_manager, sample_cookies):
        """測試提取認證資訊"""
        auth_token, cookie_string = cookie_manager.extract_auth_info(sample_cookies)

        # 驗證 cookie 字串包含所有 cookies
        assert cookie_string is not None
        assert "session_id=abc123" in cookie_string
        assert "auth_token=test_auth_token_value" in cookie_string

    def test_extract_auth_info_empty_cookies(self, cookie_manager):
        """測試空 cookies 列表"""
        auth_token, cookie_string = cookie_manager.extract_auth_info([])
        # 空列表應該返回空值
        assert cookie_string == "" or cookie_string is None

    def test_get_headers(self, cookie_manager, sample_cookies, monkeypatch):
        """測試生成請求頭"""
        # 載入 cookies
        cookie_manager.load_cookies()

        user_agent = NetworkManager.get_random_user_agent()
        headers = cookie_manager.get_headers(user_agent)

        assert headers is not None
        assert "user-agent" in headers
        assert headers["user-agent"] == user_agent

    def test_cookie_filenames_constant(self):
        """測試支援的 cookie 檔名常數"""
        assert hasattr(CookieManager, "COOKIE_FILENAMES")
        assert isinstance(CookieManager.COOKIE_FILENAMES, (list, tuple))
        assert len(CookieManager.COOKIE_FILENAMES) > 0
        assert "www.jvid.com_cookies.json" in CookieManager.COOKIE_FILENAMES


class TestNetworkManagerUserAgent:
    """NetworkManager User-Agent 相關測試"""

    def test_get_random_user_agent_not_empty(self):
        """測試取得的 User-Agent 不為空"""
        user_agent = NetworkManager.get_random_user_agent()
        assert user_agent is not None
        assert len(user_agent) > 0

    def test_get_random_user_agent_is_string(self):
        """測試取得的 User-Agent 是字串"""
        user_agent = NetworkManager.get_random_user_agent()
        assert isinstance(user_agent, str)

    def test_get_random_user_agent_contains_browser_info(self):
        """測試 User-Agent 包含瀏覽器資訊"""
        user_agent = NetworkManager.get_random_user_agent()
        # 應該包含常見的瀏覽器標識
        browser_keywords = ["Mozilla", "Chrome", "Safari", "Firefox", "Edge"]
        assert any(keyword in user_agent for keyword in browser_keywords)
