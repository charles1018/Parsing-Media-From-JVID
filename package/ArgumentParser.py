# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
"""
from argparse import ArgumentParser, Namespace
import os

class AP:
    def __init__(self, obj):
        self.obj = obj

    @staticmethod
    def parse_args() -> Namespace:
        # 從環境變數讀取預設值
        default_path = os.getenv('DOWNLOAD_PATH', 'media')
        default_threads = int(os.getenv('DEFAULT_THREADS', '1'))
        default_auto_resume = os.getenv('AUTO_RESUME', 'false').lower() == 'true'

        parse = ArgumentParser()
        parse.add_argument('-t', '--type',
                           help='已梳除，保留以向下兼容 | ex: image / mp4',
                           default='auto', type=str)

        parse.add_argument('-u', '--url',
                           help="give a url of JVID | ex: 'https://www.jvid.com/v/[PAGE_ID]'",
                           default='', type=str)

        parse.add_argument('-p', '--path',
                           help=f"give a save path | ex: './media/' (default: {default_path})",
                           default=default_path, type=str)

        parse.add_argument('-a', '--auto-resume',
                           help=f"automatically resume download without asking (default: {default_auto_resume})",
                           action='store_true',
                           default=default_auto_resume)

        parse.add_argument('-d', '--diagnostic-mode',
                           help="enable diagnostic mode for troubleshooting | ex: true",
                           action='store_true')

        parse.add_argument('-w', '--working-url',
                           help="add a working URL to the examples list | ex: 'https://www.jvid.com/v/[WORKING_ID]'",
                           default='', type=str)

        parse.add_argument('-n', '--threads',
                           help=f"specify the number of threads to use (default: {default_threads}) | ex: 3",
                           default=default_threads, type=int)

        return parse.parse_args()

    def config_once(self):
        args = AP.parse_args()
        self.obj.type = args.type
        self.obj.url = args.url
        self.obj.path = args.path
        self.obj.auto_resume = args.auto_resume
        self.obj.diagnostic_mode = args.diagnostic_mode
        self.obj.thread_count = args.threads  # 設置執行緒數量
        
        # 處理添加工作URL的情況
        if args.working_url:
            self.add_working_example(args.working_url)
            
    def add_working_example(self, url):
        """添加工作URL到示例列表"""
        # 確保目錄存在
        media_path = os.path.join(os.getcwd(), self.obj.path)
        if not os.path.exists(media_path):
            os.makedirs(media_path)
            
        # 添加到工作示例文件
        examples_file = os.path.join(media_path, 'working_examples.txt')
        
        # 檢查URL是否已存在
        existing_urls = []
        if os.path.exists(examples_file):
            with open(examples_file, 'r') as f:
                existing_urls = [line.strip() for line in f if line.strip()]
                
        if url not in existing_urls:
            with open(examples_file, 'a') as f:
                f.write(f"{url}\n")
            print(f"已添加URL到工作示例: {url}")
        else:
            print(f"URL已存在於工作示例: {url}")