"""
NetworkManager 單元測試

重點驗證 request_with_retry 在持續 429/403/5xx 時能有界終止（不會無限迴圈），
以及正常成功與例外情境的行為。所有測試皆離線，並將 time.sleep 置換為 no-op。
"""

from unittest.mock import MagicMock, patch

import requests

from package.network.NetworkManager import NetworkManager


def make_response(status_code):
    """建立一個假的 requests.Response 物件"""
    res = MagicMock()
    res.status_code = status_code
    res.text = "body"
    res.content = b"body"
    return res


def make_manager():
    """建立測試用 NetworkManager，關閉節流以加速測試"""
    return NetworkManager(
        headers={"user-agent": "test-agent"},
        timeout=1,
        min_request_interval=0,
    )


@patch("time.sleep", lambda *_a, **_k: None)
def test_persistent_403_terminates_and_returns_none():
    """持續 403 應在有界次數內放棄並回傳 None（不無限迴圈）"""
    manager = make_manager()
    manager.session.get = MagicMock(return_value=make_response(403))

    result = manager.request_with_retry("https://example.com/x")

    assert result is None
    # 有界：呼叫次數不得超過限流重試上限
    assert manager.session.get.call_count <= NetworkManager.MAX_THROTTLE_RETRIES


@patch("time.sleep", lambda *_a, **_k: None)
def test_persistent_429_terminates_and_returns_none():
    """持續 429 應在有界次數內放棄並回傳 None"""
    manager = make_manager()
    manager.session.get = MagicMock(return_value=make_response(429))

    result = manager.request_with_retry("https://example.com/x")

    assert result is None
    assert manager.session.get.call_count <= NetworkManager.MAX_THROTTLE_RETRIES


@patch("time.sleep", lambda *_a, **_k: None)
def test_persistent_500_terminates_and_returns_none():
    """持續 500 應在有界次數內放棄並回傳 None"""
    manager = make_manager()
    manager.session.get = MagicMock(return_value=make_response(500))

    result = manager.request_with_retry("https://example.com/x")

    assert result is None
    assert manager.session.get.call_count <= NetworkManager.MAX_THROTTLE_RETRIES


@patch("time.sleep", lambda *_a, **_k: None)
def test_success_after_two_failures():
    """前兩次 500 後第三次 200 應回傳成功的 Response"""
    manager = make_manager()
    ok = make_response(200)
    manager.session.get = MagicMock(
        side_effect=[make_response(500), make_response(500), ok]
    )

    result = manager.request_with_retry("https://example.com/x")

    assert result is ok
    assert manager.session.get.call_count == 3


@patch("time.sleep", lambda *_a, **_k: None)
def test_immediate_success():
    """首次即 200 應直接回傳，僅呼叫一次"""
    manager = make_manager()
    ok = make_response(200)
    manager.session.get = MagicMock(return_value=ok)

    result = manager.request_with_retry("https://example.com/x")

    assert result is ok
    assert manager.session.get.call_count == 1


@patch("time.sleep", lambda *_a, **_k: None)
def test_persistent_exception_returns_none():
    """持續拋出連線例外時應在 max_retries 內放棄並回傳 None"""
    manager = make_manager()
    manager.session.get = MagicMock(
        side_effect=requests.exceptions.ConnectionError("boom")
    )

    result = manager.request_with_retry("https://example.com/x", max_retries=3)

    assert result is None
    assert manager.session.get.call_count == 3


@patch("time.sleep", lambda *_a, **_k: None)
def test_generic_non_200_uses_normal_retries():
    """一般非特殊狀態碼（如 404）應走 max_retries 計數後放棄"""
    manager = make_manager()
    manager.session.get = MagicMock(return_value=make_response(404))

    result = manager.request_with_retry("https://example.com/x", max_retries=3)

    assert result is None
    assert manager.session.get.call_count == 3
