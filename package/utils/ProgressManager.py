# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
進度管理器 - 負責管理下載進度的保存和恢復
"""

import os
import json
from datetime import datetime, timezone, timedelta


class ProgressManager:
    def __init__(self, path, console):
        """
        初始化進度管理器

        參數:
            path: 保存路徑
            console: 控制台物件
        """
        self.path = path
        self.console = console

    @staticmethod
    def utc_to_now():
        """
        獲取當前時間（台北/UTC+8）

        返回:
            當前時間
        """
        return datetime.now(timezone(timedelta(hours=8)))

    def save_progress(self, data):
        """
        儲存下載進度

        參數:
            data: 要保存的數據字典

        返回:
            成功返回 True，失敗返回 False
        """
        try:
            # 確保目錄存在
            if not os.path.exists(self.path):
                os.makedirs(self.path)

            # 添加時間戳
            data["timestamp"] = str(ProgressManager.utc_to_now())

            # 儲存進度到檔案
            progress_file = os.path.join(self.path, "download_progress.json")
            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.console.print(f"下載進度已儲存至: {progress_file}")
            return True
        except Exception as e:
            self.console.print(f"儲存進度失敗: {type(e).__name__}: {str(e)}")
            return False

    def load_progress(self, url, type_name="auto"):
        """
        載入先前的下載進度

        參數:
            url: 當前URL
            type_name: 媒體類型

        返回:
            如存在進度返回進度數據字典，否則返回None
        """
        progress_file = os.path.join(self.path, "download_progress.json")
        if not os.path.exists(progress_file):
            return None

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)

            # 檢查URL是否一致，確保是同一下載任務
            if progress_data.get("url") != url:
                self.console.print("找到進度檔案，但與當前下載任務不符")
                return None

            # 如果任務已完成，不需恢復
            remaining_todo_list = progress_data.get("todo_list", [])
            if not remaining_todo_list:
                self.console.print("找到進度檔案，但已無剩餘下載任務")
                return None

            save_time = progress_data.get("timestamp", "未知時間")
            self.console.print(
                f"已從 {save_time} 的進度恢復，將繼續下載剩餘 {len(remaining_todo_list)} 個檔案"
            )
            return progress_data

        except Exception as e:
            self.console.print(f"載入進度失敗: {type(e).__name__}: {str(e)}")
            return None

    def check_and_resume_download(self, url, type_name="auto", auto_resume=False):
        """
        檢查是否有未完成的下載，並根據設定決定是否自動恢復或詢問使用者

        參數:
            url: 當前URL
            type_name: 媒體類型
            auto_resume: 是否自動恢復

        返回:
            有可恢復的進度返回進度數據，否則返回None
        """
        progress_file = os.path.join(self.path, "download_progress.json")
        if not os.path.exists(progress_file):
            return None

        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)

            # 檢查URL是否一致
            if progress_data.get("url") == url:
                remaining_count = len(progress_data.get("todo_list", []))
                if remaining_count > 0:
                    save_time = progress_data.get("timestamp", "未知時間")
                    self.console.print(
                        f"發現在 {save_time} 的未完成下載，剩餘 {remaining_count} 個檔案"
                    )

                    # 如果設置了自動恢復，則直接恢復
                    if auto_resume:
                        self.console.print("自動恢復模式已啟用，繼續上次下載")
                        return progress_data
                    else:
                        # 詢問使用者是否繼續下載
                        resume_choice = (
                            str(input("是否繼續上次的下載? (y/n): ")).lower().strip()
                        )
                        if resume_choice in ["y", "yes"]:
                            return progress_data
        except Exception as e:
            self.console.print(f"檢查進度檔案失敗: {type(e).__name__}: {str(e)}")

        return None

    def delete_progress_file(self):
        """
        刪除進度檔案

        返回:
            成功返回 True，失敗返回 False
        """
        progress_file = os.path.join(self.path, "download_progress.json")
        if os.path.exists(progress_file):
            try:
                os.remove(progress_file)
                self.console.print("下載完成，已刪除進度檔案")
                return True
            except Exception as e:
                self.console.print(f"刪除進度檔案失敗: {type(e).__name__}: {str(e)}")
                return False
        return True
