# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
最後修改: 2025-03-22 (模組化重構，優化架構)

解碼參考來源: https://cloud.tencent.com/developer/article/2258872
"""
from datetime import datetime, timezone, timedelta
import os
import json
from bs4 import BeautifulSoup
from rich.console import Console

from package.network.NetworkManager import NetworkManager
from package.processors.VideoProcessor import VideoProcessor
from package.processors.ImageProcessor import ImageProcessor
from package.utils.ContentDetector import ContentDetector
from package.utils.ProgressManager import ProgressManager
from package.utils.CookieManager import CookieManager
from package.DiagnosticMode import DiagnosticMode

class ParsingMediaLogic:
    def __init__(self, obj):
        self.type = obj.type
        self.url = obj.url
        self.path = os.getcwd() + '\\' + obj.path
        self.auto_resume = obj.auto_resume  # 自動恢復選項
        self.console = Console()
        self.diagnostic_mode = None  # 初始化診斷模式為 None
        self.diagnostic_enabled = obj.diagnostic_mode if hasattr(obj, 'diagnostic_mode') else False  # 從命令列參數獲取診斷模式設置
        self.thread_count = obj.thread_count if hasattr(obj, 'thread_count') else 1  # 從命令列參數獲取執行緒數量，預設為1

        # 記錄下載
        self.log_record()
        
        # 初始化模組
        self.headers = self.update_headers()
        self.network_manager = NetworkManager(self.headers, 20, 0.5, self.console)
        self.content_detector = ContentDetector()
        self.progress_manager = ProgressManager(self.path, self.console)
        
        # 如果啟用診斷模式，進行初始化
        if self.diagnostic_enabled:
            self.initialize_diagnostic_mode()

    @staticmethod
    def check_folder(path: str):
        """確保資料夾存在"""
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    @staticmethod
    def update_headers() -> dict:
        """
        取得請求頭，優先從 cookies.json 讀取，否則回退到 permissions.txt
        """
        # 優先使用 CookieManager 讀取 cookies
        cookie_manager = CookieManager()
        user_agent = NetworkManager.get_random_user_agent()
        headers = cookie_manager.get_headers(user_agent)
        
        # 如果成功載入 cookies，輸出資訊並返回
        if 'authorization' in headers or 'cookie' in headers:
            cookie_manager.print_cookie_info(headers)
            return headers
        
        # 回退：嘗試從舊的 permissions.txt 讀取
        print("⚠️  未找到 cookies 文件，嘗試讀取 permissions.txt...")
        try:
            txt = [i for i in open(os.getcwd() + '\\package\\permissions.txt', 'r')]
            headers = {
                'user-agent': user_agent,
                'authorization': txt[0].split(',')[-1].replace('\n', ''),
                'cookie': txt[1].split(',')[-1].replace('\n', ''),
            }
            print("✓ 成功從 permissions.txt 讀取認證資訊")
            return headers
        except Exception as e:
            print(f"⚠️  無法讀取 permissions.txt: {e}")
            print("⚠️  將使用基本請求頭（部分功能可能受限）")
            return {'user-agent': user_agent}

    @staticmethod
    def get_target_title(soup: BeautifulSoup) -> str:
        """取得頁面標題並清理不合法字符"""
        get_title = soup.find('title').text
        for symbol in ['/', '<' , '>', ':', '|', '?', '*', '"']:
            get_title = get_title.replace(symbol, '')
        return get_title

    @staticmethod
    def utc_to_now():
        """獲取台北時區的當前時間"""
        return datetime.now(timezone(timedelta(hours=8)))

    def log_record(self):
        """記錄下載日誌"""
        # 確保目錄存在
        ParsingMediaLogic.check_folder(self.path)
        file = self.path + '\\downloads_log.txt'
        content = f'{str(ParsingMediaLogic.utc_to_now())[:19]} | {self.url}\n'
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write(content)
        else:
            new = [i for i in open(file, 'r')] + [content]
            open(file, 'w').write(''.join(new))

    def progress_bar(self, task: str, symbol: str='='):
        """顯示進度提示"""
        if task == 'Args':
            self.console.print(f'Get Parameter... {symbol * 46} 100%')
        elif task == 'Get_Downloads_List':
            self.console.print(f'Get Downloads List... {symbol * 41} 100%')
        elif task == 'Finish_Task':
            self.console.print('Finish Task ! Exit Program ...')

    def initialize_diagnostic_mode(self):
        """初始化診斷模式"""
        try:
            # 創建診斷目錄
            diagnostic_path = os.path.join(os.path.dirname(self.path), 'diagnostics')
            ParsingMediaLogic.check_folder(diagnostic_path)
            
            # 初始化診斷模式
            self.diagnostic_mode = DiagnosticMode(base_path=diagnostic_path)
            self.console.print("[診斷模式] 診斷模式已初始化")
        except Exception as e:
            self.console.print(f"[診斷模式] 初始化診斷模式時出錯: {str(e)}")
            self.diagnostic_mode = None
            
    def diagnostic_analyze_page(self, url, html_content):
        """
        使用診斷模式分析頁面結構
        
        參數:
            url: 頁面URL
            html_content: 頁面HTML內容
        """
        if not self.diagnostic_mode:
            return
            
        try:
            # 開始診斷會話
            self.diagnostic_mode.start_session(url)
            
            # 記錄頁面獲取
            self.diagnostic_mode.log_step("fetch_page", {
                "url": url,
                "status": "success",
                "content_length": len(html_content)
            })
            
            # 分析頁面結構
            analysis_result = self.diagnostic_mode.analyze_page_structure(html_content)
            self.diagnostic_mode.log_step("analyze_structure", {
                "title": analysis_result["title"],
                "meta_tags_count": len(analysis_result["meta_tags"]),
                "scripts_count": len(analysis_result["scripts"]),
                "media_containers_count": len(analysis_result["potential_media_containers"])
            })
            
            # 獲取建議的提取策略
            suggestions = self.diagnostic_mode.suggest_extraction_strategies(analysis_result)
            self.diagnostic_mode.log_step("extraction_suggestions", {
                "suggestions_count": len(suggestions),
                "suggestions": suggestions
            })
            
            # 測試各種提取方法
            for method in ["meta_transcode", "div_m3u8_playlist", "direct_regex_m3u8", 
                          "json_data_extraction", "script_variable_extraction"]:
                result = self.diagnostic_mode.test_extraction_method(method, html_content)
                self.diagnostic_mode.log_extraction_attempt(method, result)
                
                # 如果找到URL，記錄並退出
                if result["success"]:
                    self.console.print(f"[診斷模式] 方法 '{method}' 成功提取URL: {result['url']}")
            
            # 如果有成功的工作示例，與當前頁面進行比較
            working_urls_file = os.path.join(os.path.dirname(self.path), 'working_examples.txt')
            if os.path.exists(working_urls_file):
                with open(working_urls_file, 'r') as f:
                    working_urls = [line.strip() for line in f if line.strip()]
                
                if working_urls:
                    comparison = self.diagnostic_mode.compare_with_working_examples(working_urls, html_content)
                    self.diagnostic_mode.log_step("compare_with_working", comparison)
                    
                    if comparison["differences_found"]:
                        self.console.print("[診斷模式] 檢測到與工作示例的結構差異")
        except Exception as e:
            self.console.print(f"[診斷模式] 分析頁面時出錯: {str(e)}")
            if self.diagnostic_mode:
                self.diagnostic_mode.log_step("error", {"message": str(e), "type": type(e).__name__})
    
    def diagnostic_finalize(self, success, final_url=None, notes=None):
        """
        完成診斷會話
        
        參數:
            success: 是否成功解析URL
            final_url: 最終解析的URL
            notes: 額外註釋
        """
        if not self.diagnostic_mode:
            return
            
        try:
            self.diagnostic_mode.finalize_session(success, final_url, notes)
            
            # 生成並顯示報告
            report = self.diagnostic_mode.generate_report()
            self.console.print("\n" + report)
            
            # 如果解析失敗，建議添加工作示例
            if not success:
                self.console.print("\n[診斷建議] 請添加成功解析的URL到 working_examples.txt 文件中")
                self.console.print("[診斷建議] 這將有助於比較不同頁面結構，找出解析失敗的原因")
        except Exception as e:
            self.console.print(f"[診斷模式] 完成診斷時出錯: {str(e)}")

    def identify_type_operation(self):
        """智能識別內容類型並處理下載"""
        # 使用網路模組獲取初始頁面
        res = self.network_manager.request_with_retry(self.url)
        if res is None:
            self.console.print(f"無法獲取頁面內容: {self.url}")
            return
            
        # 解析頁面
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 取得標題並建立目錄
        self.path += f'\\{ParsingMediaLogic.get_target_title(soup)}'
        if not os.path.exists(self.path):
            ParsingMediaLogic.check_folder(self.path)
        
        # 使用內容檢測器判斷頁面類型
        has_video, has_image = self.content_detector.detect_content_types(res.text, soup)
        
        # 輸出偵測結果
        content_types = []
        if has_video:
            content_types.append("影片")
        if has_image:
            content_types.append("圖片")
            
        if content_types:
            self.console.print(f"偵測到頁面包含: {', '.join(content_types)}")
        else:
            self.console.print("無法偵測到頁面內容類型")
            return
            
        # 如果啟用了診斷模式，則分析頁面
        if has_video and self.diagnostic_enabled and self.diagnostic_mode:
            self.diagnostic_analyze_page(self.url, res.text)
            
        # 處理影片內容
        if has_video:
            # 提取影片URL
            video_urls, video_types = self.content_detector.extract_video_urls(res.text, soup)
            
            # 處理診斷模式的額外提取方法
            if self.diagnostic_enabled and self.diagnostic_mode:
                # 嘗試直接正則表達式
                regex_result = self.diagnostic_mode.test_extraction_method("direct_regex_m3u8", res.text)
                if regex_result["success"] and regex_result["url"] not in video_urls:
                    video_urls.append(regex_result["url"])
                    video_types.append("direct_regex_m3u8")
                    self.console.print(f"[診斷模式] 使用正則表達式成功提取URL: {regex_result['url']}")
                
                # 嘗試JSON數據提取
                json_result = self.diagnostic_mode.test_extraction_method("json_data_extraction", res.text)
                if json_result["success"] and json_result["url"] not in video_urls:
                    video_urls.append(json_result["url"])
                    video_types.append("json_data_extraction")
                    self.console.print(f"[診斷模式] 從JSON數據成功提取URL: {json_result['url']}")
                
                # 嘗試腳本變量提取
                script_result = self.diagnostic_mode.test_extraction_method("script_variable_extraction", res.text)
                if script_result["success"] and script_result["url"] not in video_urls:
                    video_urls.append(script_result["url"])
                    video_types.append("script_variable_extraction")
                    self.console.print(f"[診斷模式] 從腳本變量成功提取URL: {script_result['url']}")
            
            # 檢查是否有找到任何影片URL
            if not video_urls:
                self.console.print('未找到任何 m3u8 檔案')
                
                # 診斷模式記錄失敗結果
                if self.diagnostic_enabled and self.diagnostic_mode:
                    self.diagnostic_finalize(False, None, "找不到 m3u8 文件")
            else:
                # 建立視頻處理器處理下載
                video_processor = VideoProcessor(self.network_manager, self.path, self.console)
                # 設定執行緒數量
                video_processor.MAX_WORKERS = self.thread_count
                self.console.print(f"使用 {self.thread_count} 個執行緒下載影片")
                video_processor.process_video_urls(video_urls, video_types)
        
        # 處理圖片內容
        if has_image:
            # 如果已經處理過影片，創建圖片子目錄
            image_path = self.path
            if has_video:
                image_path = f"{self.path}\\images"
                if not os.path.exists(image_path):
                    ParsingMediaLogic.check_folder(image_path)
            
            # 提取圖片URL
            image_urls = self.content_detector.extract_image_urls(soup)
            
            # 建立圖片處理器處理下載
            image_processor = ImageProcessor(self.network_manager, image_path, self.console)
            # 設定執行緒數量
            image_processor.MAX_WORKERS = self.thread_count
            self.console.print(f"使用 {self.thread_count} 個執行緒下載圖片")
            image_processor.process_images(image_urls)

    def main(self):
        """主要程序入口點"""
        ParsingMediaLogic.check_folder(self.path)
        self.progress_bar('Args')
        
        # 檢查是否有未完成的下載
        resume_data = self.progress_manager.check_and_resume_download(self.url, self.type, self.auto_resume)
        if resume_data:
            self.console.print("繼續上次未完成的下載")
            # TODO: 根據進度數據恢復下載
            # 由於需要深度重構，此功能暫不實現
            # 在新的架構中，需要重新設計續傳機制
        else:
            # 如果沒有恢復下載，就開始新的下載
            self.identify_type_operation()
                
        self.progress_bar('Finish_Task')