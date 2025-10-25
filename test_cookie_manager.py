# -*- coding: utf-8 -*-
"""
Cookie Manager 測試腳本
用於驗證 Cookie 載入和解析功能
"""
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from package.utils.CookieManager import CookieManager
from package.network.NetworkManager import NetworkManager


def test_cookie_manager():
    """測試 CookieManager 的各項功能"""
    
    print("=" * 60)
    print("Cookie Manager 功能測試")
    print("=" * 60)
    
    # 初始化 CookieManager
    cookie_manager = CookieManager()
    
    # 測試 1: 尋找 cookie 文件
    print("\n[測試 1] 尋找 Cookie 文件")
    print("-" * 60)
    cookie_file = cookie_manager.find_cookie_file()
    if cookie_file:
        print(f"[OK] 找到 Cookie 文件: {cookie_file}")
    else:
        print("[FAIL] 未找到 Cookie 文件")
        print("支援的文件名稱:")
        for filename in CookieManager.COOKIE_FILENAMES:
            print(f"  - {filename}")
        return False
    
    # 測試 2: 載入 cookies
    print("\n[測試 2] 載入 Cookies")
    print("-" * 60)
    cookies = cookie_manager.load_cookies()
    if cookies:
        print(f"[OK] 成功載入 {len(cookies)} 個 cookies")
        
        # 顯示 cookie 名稱
        cookie_names = [c.get('name') for c in cookies if c.get('name')]
        print(f"Cookie 名稱: {', '.join(cookie_names[:5])}")
        if len(cookie_names) > 5:
            print(f"  ...以及其他 {len(cookie_names) - 5} 個")
    else:
        print("[FAIL] 載入 Cookies 失敗")
        return False
    
    # 測試 3: 提取認證資訊
    print("\n[測試 3] 提取認證資訊")
    print("-" * 60)
    auth_token, cookie_string = cookie_manager.extract_auth_info(cookies)
    
    if auth_token:
        # 只顯示 token 的開頭和結尾
        display_token = f"{auth_token[:30]}...{auth_token[-20:]}" if len(auth_token) > 50 else auth_token
        print(f"[OK] Authorization Token: {display_token}")
    else:
        print("[WARN] 未找到 Authorization Token")
    
    if cookie_string:
        cookie_count = len(cookie_string.split('; '))
        print(f"[OK] Cookie 字串: 包含 {cookie_count} 個 cookies")
    else:
        print("[FAIL] 無法構建 Cookie 字串")
    
    # 測試 4: 獲取完整請求頭
    print("\n[測試 4] 生成請求頭")
    print("-" * 60)
    user_agent = NetworkManager.get_random_user_agent()
    headers = cookie_manager.get_headers(user_agent)
    
    print("請求頭內容:")
    for key, value in headers.items():
        if key == 'authorization' and value:
            display_value = f"{value[:30]}...{value[-20:]}" if len(value) > 50 else value
            print(f"  {key}: {display_value}")
        elif key == 'cookie' and value:
            cookie_count = len(value.split('; '))
            print(f"  {key}: [包含 {cookie_count} 個 cookies]")
        else:
            print(f"  {key}: {value[:50]}...")
    
    # 測試 5: 輸出摘要
    print("\n" + "=" * 60)
    print("測試摘要")
    print("=" * 60)
    
    # 簡化版的摘要輸出
    has_auth = 'authorization' in headers and headers['authorization']
    has_cookie = 'cookie' in headers and headers['cookie']
    
    if has_auth:
        print("[OK] Authorization: 已設定")
    else:
        print("[WARN] Authorization: 未設定")
    
    if has_cookie:
        cookie_count = len(headers['cookie'].split('; '))
        print(f"[OK] Cookies: 已載入 {cookie_count} 個 cookies")
    else:
        print("[WARN] Cookies: 未設定")
    
    return True


def main():
    """主函式"""
    try:
        success = test_cookie_manager()
        
        if success:
            print("\n[SUCCESS] 所有測試通過！Cookie Manager 運作正常。")
            print("\n提示: 你現在可以使用以下命令開始下載:")
            print('   uv run python Entry.py -u "https://www.jvid.com/v/[PAGE_ID]"')
            return 0
        else:
            print("\n[FAIL] 測試失敗！請檢查 Cookie 文件是否存在且格式正確。")
            print("\n請確保:")
            print("   1. Cookie 文件位於專案根目錄")
            print("   2. 文件名為 www.jvid.com_cookies.json")
            print("   3. JSON 格式正確")
            return 1
            
    except Exception as e:
        print(f"\n[ERROR] 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
