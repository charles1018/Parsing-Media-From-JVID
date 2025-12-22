# -*- coding: utf-8 -*-
"""
@author: PC
Update Time: 2025-03-22
內容偵測器 - 負責檢測頁面的內容類型和提取媒體URL
"""
from bs4 import BeautifulSoup
import re

class ContentDetector:
    @staticmethod
    def detect_content_types(html_content, soup=None):
        """
        檢測頁面中的內容類型
        
        參數:
            html_content: 頁面HTML內容
            soup: BeautifulSoup物件，如果已有則不需重新解析
            
        返回:
            (has_video, has_image): 元組，表示是否有影片和圖片
        """
        if soup is None:
            soup = BeautifulSoup(html_content, 'html.parser')
        
        has_video = False
        has_image = False
        
        # 檢查是否有影片內容
        video_indicators = ['m3u8', 'transcode', 'playList', 'vidSrc']
        for indicator in video_indicators:
            if indicator in html_content:
                has_video = True
                break
        
        # 檢查是否有圖片內容
        image_divs = soup.find_all('div', {'class': 'w-full lightbox_fancybox'})
        if image_divs:
            for div in image_divs[0].find_all('div') if image_divs else []:
                try:
                    if div.get('data-src', '').startswith('https'):
                        has_image = True
                        break
                except (AttributeError, TypeError):
                    # div 可能沒有預期的屬性，跳過此元素
                    continue
                    
        return has_video, has_image
    
    @staticmethod
    def extract_video_urls(html_content, soup=None):
        """
        提取頁面中的影片URL
        
        參數:
            html_content: 頁面HTML內容
            soup: BeautifulSoup物件，如果已有則不需重新解析
            
        返回:
            (video_urls, video_types): 元組，包含影片URL列表和對應的類型列表
        """
        if soup is None:
            soup = BeautifulSoup(html_content, 'html.parser')
            
        video_urls = []
        video_types = []
        
        # 方法1: 從meta標籤尋找transcode
        meta_urls = [i['content'] for i in soup.find_all('meta') if 'transcode' in str(i)]
        for url in meta_urls:
            video_urls.append(url)
            video_types.append("meta_transcode")
        
        # 方法2: 從div元素尋找m3u8和playList
        div_urls = []
        for div in soup.find_all('div', {'class', 'w-full'}):
            if 'm3u8' in str(div) and 'playList' in str(div) and 'transcode_video' in str(div):
                try:
                    # 從div中提取URL
                    m3u8_url = str(div).split('vidSrc=')[-1].split('.m3u8')[0] + '.m3u8'
                    div_urls.append(m3u8_url)
                except (IndexError, ValueError):
                    # URL 解析失敗，跳過此 div
                    continue
        
        for url in div_urls:
            if url not in video_urls:  # 避免重複
                video_urls.append(url)
                video_types.append("div_m3u8_playlist")
        
        # 方法3: 直接使用正則表達式尋找m3u8 URL
        m3u8_urls = re.findall(r'https?://[^\s\'"\)]+\.m3u8', html_content)
        for url in m3u8_urls:
            if url not in video_urls:  # 避免重複
                video_urls.append(url)
                video_types.append("direct_regex_m3u8")
                
        return video_urls, video_types
    
    @staticmethod
    def extract_image_urls(soup):
        """
        提取頁面中的圖片URL
        
        參數:
            soup: BeautifulSoup物件
            
        返回:
            image_urls: 圖片URL列表
        """
        image_urls = []
        
        # 從lightbox_fancybox中提取圖片URL
        image_divs = soup.find_all('div', {'class': 'w-full lightbox_fancybox'})
        if image_divs:
            for div in image_divs[0].find_all('div'):
                try:
                    if div.get('data-src', '').startswith('https'):
                        image_urls.append(div['data-src'])
                except (AttributeError, TypeError, KeyError):
                    # div 可能沒有預期的屬性，跳過此元素
                    continue

        return image_urls