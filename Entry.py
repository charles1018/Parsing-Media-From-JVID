# -*- coding: utf-8 -*-
"""
JVID 媒體下載工具
==================

@author: PC
Update Time: 2024-12-15
最後修改: 2025-01-20 （完全遷移至 uv 管理，移除 requirements.txt）

使用方式（按推薦優先級）：

1. 便捷腳本（最簡單，推薦新手）:
   Windows CMD:
     jvid-download.bat "https://www.jvid.com/v/[PAGE_ID]"
   
   Windows PowerShell:
     .\\jvid-download.ps1 -Url "https://www.jvid.com/v/[PAGE_ID]" -AutoResume
   
   macOS/Linux:
     ./jvid-download.sh "https://www.jvid.com/v/[PAGE_ID]" -a

2. 專案入口點（簡潔，推薦熟手）:
   uv run jvid-dl -u "https://www.jvid.com/v/[PAGE_ID]"

3. 直接執行（開發調試用）:
   uv run python Entry.py -u "https://www.jvid.com/v/[PAGE_ID]"

參數說明：
  -u URL          目標 JVID 頁面 URL（必填）
  -p PATH         自定義保存路徑（可選）
  -a              啟用自動續傳（可選）
  -d              啟用診斷模式（可選）
  -n NUMBER       指定執行緒數量，預設1（可選）
  -w URL          添加成功案例供診斷模式參考（可選）

使用範例：
  # 基本下載
  uv run jvid-dl -u "https://www.jvid.com/v/12345"
  
  # 指定保存路徑
  uv run jvid-dl -u "https://www.jvid.com/v/12345" -p "my_videos"
  
  # 啟用自動續傳
  uv run jvid-dl -u "https://www.jvid.com/v/12345" -a
  
  # 診斷模式（解析問題時使用）
  uv run jvid-dl -u "https://www.jvid.com/v/12345" -d
  
  # 多執行緒下載（測試成功後使用）
  uv run jvid-dl -u "https://www.jvid.com/v/12345" -n 3

功能特點:
- 自動偵測頁面內容類型（影片/圖片）
- 自動下載所有可用的影片版本
- 自動清理暫存檔案
- 預設單執行緒確保下載完整性
- 支援中斷續傳

完整使用指南請參閱：
- 快速開始：QUICKSTART.md
- 使用指南：USER_GUIDE.md
- 開發指南：DEVELOPER_GUIDE.md
"""
from package.ParsingMediaLogic import ParsingMediaLogic
from package.ArgumentParser import AP

class Entry:
    def __init__(self):
        self.type = None
        self.url = None
        self.path = None
        self.auto_resume = False
        # 使用單執行緒作為預設設置

    def main(self):
        ap = AP(self)
        ap.config_once()
        pm = ParsingMediaLogic(self)
        pm.main()

def main():
    """專案入口點函數，供 uv run jvid-dl 使用"""
    entry = Entry()
    entry.main()

if __name__ == '__main__':
    main()