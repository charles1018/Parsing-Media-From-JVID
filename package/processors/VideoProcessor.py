"""
@author: PC
Update Time: 2025-03-22
影片處理器 - 負責處理影片的下載和轉換
"""

import os
import random
import shutil
import subprocess
import time
from functools import partial
from subprocess import PIPE, STDOUT

from Crypto.Cipher import AES

from .BaseProcessor import BaseProcessor


class VideoProcessor(BaseProcessor):
    """影片處理器，繼承自 BaseProcessor"""

    # 批次處理常數
    BATCH_SIZE = 100
    DELAY_MIN = 0.1
    DELAY_MAX = 0.3

    def __init__(self, network_manager, base_path, console, auto_resume=False):
        """
        初始化影片處理器

        參數:
            network_manager: 網路管理器物件
            base_path: 基本下載路徑
            console: 控制台物件
            auto_resume: 是否自動恢復下載
        """
        super().__init__(network_manager, base_path, console)
        self.base_path = base_path  # 保留 base_path 別名以保持向後相容
        self.auto_resume = auto_resume
        self.aes_key = None  # 儲存 AES 金鑰，用於執行緒安全的解密
        self.base_url = None
        self.download_active = True
        self.paused = False

    def process_video_urls(self, video_urls, video_types):
        """
        處理影片URL列表，下載並轉換影片

        參數:
            video_urls: 影片URL列表
            video_types: 影片類型列表

        返回:
            全部版本皆完成（下載並合併）返回 True，否則返回 False
        """
        self.console.print(f"找到 {len(video_urls)} 個不同版本的影片，將下載全部版本")
        for i, (url, vtype) in enumerate(zip(video_urls, video_types, strict=True)):
            self.console.print(f"[{i + 1}] 類型: {vtype}, URL: {url}")

        all_complete = True
        # 依次處理每個影片URL
        for i, url in enumerate(video_urls):
            # 為每個版本創建不同的子目錄
            folder_name = f"版本_{i + 1}_{video_types[i]}"
            version_path = os.path.join(self.base_path, folder_name)
            if not os.path.exists(version_path):
                os.makedirs(version_path)

            # 續傳時：若該版本已合併出 MP4，直接略過
            if os.path.exists(os.path.join(version_path, folder_name + ".mp4")):
                self.console.print(f"第 {i + 1} 個版本已下載完成，略過")
                continue

            self.console.print(f"\n正在處理第 {i + 1} 個版本: {video_types[i]}")

            # 設置基本URL用於解析相對路徑
            self.base_url = url.replace(url.split("/")[-1], "")

            # 使用重試機制取得 m3u8 檔案
            res = self.network_manager.request_with_retry(url)
            if res is None:
                self.console.print(f"無法獲取 m3u8 檔案: {url}")
                all_complete = False
                continue

            with open(os.path.join(version_path, "media.m3u8"), "w") as f:
                f.write(res.text)

            # 讀取 m3u8 密鑰 & 目標清單
            with open(os.path.join(version_path, "media.m3u8")) as f:
                media = list(f)

            # 查找並解析密鑰行
            key_lines = [i for i in media if "#EXT-X-KEY" in i]
            if not key_lines:
                self.console.print("找不到加密密鑰行，可能是未加密影片或格式不兼容")
                continue

            try:
                key_line = key_lines[0]
                key_parts = key_line.split(",")
                uri_parts = [p for p in key_parts if "URI=" in p]

                if not uri_parts:
                    self.console.print("無法從密鑰行解析URI")
                    continue

                key = uri_parts[0].split("URI=")[-1][1:-1]
            except Exception as e:
                self.console.print(f"解析密鑰時出錯: {str(e)}")
                continue

            # 使用重試機制取得解密金鑰
            res = self.network_manager.request_with_retry(self.base_url + key)
            if res is None:
                self.console.print(f"無法獲取解密金鑰: {self.base_url + key}")
                all_complete = False
                continue

            # 儲存 AES 金鑰（每個執行緒會建立自己的解密器以確保執行緒安全）
            self.aes_key = res.content

            # 準備下載分段列表，以 (索引, URL) 形式記錄，
            # 索引同時作為分段檔名，確保合併順序正確並支援續傳跳過
            with open(os.path.join(version_path, "media.m3u8")) as f:
                media = list(f)
            segments = [
                i for i in "".join(media).split("\n") if "#EXT" not in i and i != ""
            ]
            self.todo_list = [
                (index, self.base_url + segment)
                for index, segment in enumerate(segments)
            ]

            # 下載 TS 分段（傳遞 version_path 而非修改實例變數）
            failed_items = self.download_ts_segments(save_path=version_path)

            if failed_items:
                self.console.print(
                    f"[yellow]第 {i + 1} 個版本有 {len(failed_items)} 個分段"
                    f"下載失敗，保留暫存檔以便續傳[/yellow]"
                )
                all_complete = False
                continue

            # 創建合併文件列表（依分段索引順序）
            with open(os.path.join(version_path, "media.txt"), "w") as f:
                for index in range(len(self.todo_list)):
                    f.write(f"file '{index}.ts'\n")

            # 合併 ts 檔並轉為 mp4（傳遞 version_path 而非修改實例變數）
            if not self.combine_ts_to_mp4(save_path=version_path):
                self.console.print(
                    f"[yellow]第 {i + 1} 個版本合併失敗，保留暫存檔以便修復後續傳[/yellow]"
                )
                all_complete = False
                continue

        # 全部版本完成後才刪除暫存檔，否則保留以供續傳
        if all_complete:
            self.remove_all_temp_files()
        else:
            self.console.print(
                "[yellow]部分影片版本未完成，重新執行（建議加上 -a）即可續傳[/yellow]"
            )

        return all_complete

    def process(self, urls):
        """
        實作抽象方法 - 處理影片下載

        參數:
            urls: 包含 (video_urls, video_types) 的元組
        """
        video_urls, video_types = urls
        self.process_video_urls(video_urls, video_types)

    def download_ts_segments(self, save_path=None):
        """
        下載所有TS分段，使用基礎類別的批次下載功能

        參數:
            save_path: 保存路徑（如未指定則使用 self.base_path）

        返回:
            下載失敗的 (索引, URL) 項目列表，全部成功時為空列表
        """
        if save_path is None:
            save_path = self.base_path

        # 使用 partial 綁定 save_path 參數
        download_func = partial(self._download_single_ts, save_path=save_path)

        return self.batch_download(
            todo_list=self.todo_list,
            download_func=download_func,
            batch_size=self.BATCH_SIZE,
            desc="Downloads Schedule",
        )

    def _download_single_ts(self, item, save_path=None):
        """
        下載並解密單個 TS 分段檔案（供 batch_download 調用）

        參數:
            item: (索引, URL) 元組，索引作為分段檔名
            save_path: 保存路徑（如未指定則使用 self.base_path）

        返回:
            成功返回 0，失敗返回 -1
        """
        if save_path is None:
            save_path = self.base_path

        index, url = item
        ts_file_path = os.path.join(save_path, f"{index}.ts")

        # 續傳時：分段已存在則跳過（檔案以原子改名寫入，存在即代表完整）
        if os.path.exists(ts_file_path):
            return 0

        try:
            # 添加輕微隨機延遲，模擬更自然的人類行為
            time.sleep(random.uniform(self.DELAY_MIN, self.DELAY_MAX))

            # 使用重試機制下載
            res = self.network_manager.request_with_retry(url)
            if res:
                # 每個執行緒建立自己的 AES 解密器（AES Cipher 不是執行緒安全的）
                cryptor = AES.new(self.aes_key, AES.MODE_CBC)
                decrypted_data = cryptor.decrypt(res.content)

                # 先寫入暫存檔再原子改名，避免中斷時留下不完整的分段
                temp_path = ts_file_path + ".tmp"
                with open(temp_path, "wb") as f:
                    f.write(decrypted_data)
                os.replace(temp_path, ts_file_path)
                return 0
        except Exception as e:
            self.console.print(f"處理 TS 檔案錯誤: {type(e).__name__}: {str(e)}")
        return -1

    def combine_ts_to_mp4(self, save_path=None):
        """
        合併 TS 文件為 MP4

        參數:
            save_path: 保存路徑（如未指定則使用 self.base_path）

        返回:
            合併成功返回 True，ffmpeg 不存在或執行失敗返回 False
        """
        if save_path is None:
            save_path = self.base_path

        # 合併影片必須依賴 ffmpeg；缺少時明確報錯而非在下載完成後才崩潰
        if shutil.which("ffmpeg") is None:
            self.console.print(
                "[red]找不到 ffmpeg，無法合併影片。請先安裝 ffmpeg 並確認已在 PATH 中，"
                "分段暫存檔已保留，安裝後重新執行即可續傳。[/red]"
            )
            return False

        # 提取當前處理的版本名稱
        folder_name = os.path.basename(save_path)
        output_name = "media.mp4"

        # 如果是版本目錄，使用自定義名稱
        if folder_name.startswith("版本_"):
            output_name = folder_name + ".mp4"

        # 使用列表形式傳遞命令，避免 shell=True 的安全風險
        cmd = ["ffmpeg", "-f", "concat", "-i", "media.txt", "-c", "copy", output_name]
        self.console.print(f"執行合併命令: {' '.join(cmd)}")

        try:
            pop = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT, cwd=save_path)
        except OSError as e:
            self.console.print(f"[red]啟動 ffmpeg 失敗: {e}[/red]")
            return False

        while pop.poll() is None:
            line = pop.stdout.readline()
            try:
                line = line.decode("utf8")
                self.console.print(line, end="")
            except UnicodeDecodeError:
                pass
            except OSError as e:
                self.console.print(f"讀取輸出時發生錯誤: {e}")

        # 檢查 ffmpeg 回傳碼，非 0 代表合併失敗
        if pop.returncode != 0:
            self.console.print(
                f"[red]ffmpeg 合併失敗（回傳碼 {pop.returncode}），保留暫存檔以便重試[/red]"
            )
            return False

        output_path = os.path.join(save_path, output_name)
        self.console.print(f"合併完成: {output_path}")
        return True

    def remove_all_temp_files(self):
        """直接刪除所有版本的暫存檔，不詢問"""
        deleted_count = 0
        failed_files = []

        # 先收集所有需要刪除的檔案（避免在遍歷時修改目錄結構）
        files_to_delete = []
        for root, dirs, _files in os.walk(self.base_path):
            for dir_name in dirs:
                if dir_name.startswith("版本_"):
                    version_path = os.path.join(root, dir_name)
                    try:
                        for file in os.listdir(version_path):
                            if file.split(".")[-1] in ["ts", "m3u8", "txt", "tmp"]:
                                files_to_delete.append(os.path.join(version_path, file))
                    except OSError as e:
                        self.console.print(f"列舉目錄時出錯 {version_path}: {e}")

        # 刪除檔案
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
            except OSError as e:
                self.console.print(f"刪除檔案失敗 {file_path}: {e}")
                failed_files.append(file_path)

        self.console.print(f"已刪除 {deleted_count} 個暫存檔")
        if failed_files:
            self.console.print(f"警告: {len(failed_files)} 個檔案無法刪除")
