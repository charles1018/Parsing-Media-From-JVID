"""
@author: Diagnostic Module
Create Time: 2025-03-22

診斷模式模組 - 用於分析難以解析的頁面結構
"""

import json
import os
import time
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from package.network.NetworkManager import NetworkManager
import re
from urllib.parse import urlparse


class DiagnosticMode:
    def __init__(self, base_path: str = "diagnostics", verbose: bool = True):
        """
        初始化診斷模式

        參數:
            base_path: 儲存診斷資料的基本路徑
            verbose: 是否輸出詳細日誌
        """
        self.base_path = base_path
        self.verbose = verbose
        self.current_url = None
        self.current_session_id = None
        self.diagnostic_data = {}

        # 確保診斷資料目錄存在
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def start_session(self, url: str) -> None:
        """
        開始一個新的診斷會話

        參數:
            url: 要診斷的URL
        """
        self.current_url = url
        self.current_session_id = (
            f"{int(time.time())}_{urlparse(url).path.split('/')[-1]}"
        )
        self.diagnostic_data = {
            "url": url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": self.current_session_id,
            "steps": [],
            "extraction_attempts": [],
            "html_patterns": {},
            "final_result": None,
        }

        if self.verbose:
            print(f"[診斷] 開始診斷會話: {self.current_session_id} for {url}")

    def log_step(self, step_name: str, details: Dict[str, Any]) -> None:
        """
        記錄診斷步驟

        參數:
            step_name: 步驟名稱
            details: 步驟詳細資訊
        """
        if not self.current_session_id:
            print("[診斷] 錯誤: 在開始會話前嘗試記錄步驟")
            return

        step_data = {
            "step": step_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": details,
        }

        self.diagnostic_data["steps"].append(step_data)

        if self.verbose:
            print(f"[診斷] 步驟 '{step_name}' 已記錄")

    def analyze_page_structure(self, html_content: str) -> Dict[str, Any]:
        """
        分析頁面結構，尋找可能包含媒體URL的元素

        參數:
            html_content: 頁面HTML內容

        返回:
            包含分析結果的字典
        """
        soup = BeautifulSoup(html_content, "html.parser")
        analysis_result = {
            "title": soup.title.text if soup.title else "無標題",
            "meta_tags": {},
            "scripts": [],
            "potential_media_containers": [],
            "patterns_found": {},
        }

        # 分析 meta 標籤
        for meta in soup.find_all("meta"):
            if meta.get("content") and meta.get("name"):
                analysis_result["meta_tags"][meta.get("name")] = meta.get("content")
            elif meta.get("content") and meta.get("property"):
                analysis_result["meta_tags"][meta.get("property")] = meta.get("content")

        # 分析腳本標籤
        for script in soup.find_all("script"):
            if script.string:
                # 只儲存可能包含媒體URL的腳本
                script_content = script.string
                if any(
                    keyword in script_content
                    for keyword in ["video", "m3u8", "mp4", "transcode", "playList"]
                ):
                    analysis_result["scripts"].append(
                        {
                            "type": script.get("type", "text/javascript"),
                            "content_preview": script_content[:500] + "..."
                            if len(script_content) > 500
                            else script_content,
                        }
                    )

        # 尋找可能的媒體容器
        media_containers = []
        for div in soup.find_all("div"):
            div_str = str(div)
            if any(
                keyword in div_str
                for keyword in ["video", "m3u8", "mp4", "transcode", "playList"]
            ):
                container = {
                    "id": div.get("id", "unknown"),
                    "class": div.get("class", []),
                    "attributes": {
                        k: v for k, v in div.attrs.items() if k not in ["id", "class"]
                    },
                    "content_preview": div_str[:500] + "..."
                    if len(div_str) > 500
                    else div_str,
                }
                media_containers.append(container)

        analysis_result["potential_media_containers"] = media_containers

        # 尋找特定模式
        patterns = {
            "m3u8_urls": re.findall(r'https?://[^\s\'"\)]+\.m3u8', html_content),
            "mp4_urls": re.findall(r'https?://[^\s\'"\)]+\.mp4', html_content),
            "transcode_patterns": re.findall(r'transcode[^\s\'"\)]+', html_content),
            "playlist_patterns": re.findall(r'playList[^\s\'"\)]{0,50}', html_content),
        }

        analysis_result["patterns_found"] = patterns

        # 將模式添加到診斷數據中
        self.diagnostic_data["html_patterns"] = patterns

        return analysis_result

    def log_extraction_attempt(self, method_name: str, result: Dict[str, Any]) -> None:
        """
        記錄URL提取嘗試

        參數:
            method_name: 提取方法名稱
            result: 提取結果
        """
        if not self.current_session_id:
            print("[診斷] 錯誤: 在開始會話前嘗試記錄提取嘗試")
            return

        attempt_data = {
            "method": method_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "success": result.get("success", False),
            "extracted_url": result.get("url"),
            "details": result,
        }

        self.diagnostic_data["extraction_attempts"].append(attempt_data)

        if self.verbose:
            status = "成功" if result.get("success", False) else "失敗"
            print(f"[診斷] URL提取嘗試 '{method_name}' {status}")

    def compare_with_working_examples(
        self,
        working_urls: List[str],
        current_html: str,
        network_manager: Optional["NetworkManager"] = None,
    ) -> Dict[str, Any]:
        """
        將當前頁面與已知工作的例子進行比較

        參數:
            working_urls: 已知可以正常解析的URL列表
            current_html: 當前頁面的HTML
            network_manager: 可選的 NetworkManager 實例，用於發送請求

        返回:
            包含比較結果的字典
        """
        comparison_result = {
            "differences_found": False,
            "structure_differences": [],
            "pattern_differences": {},
        }

        # 如果沒有提供可工作的例子，則無法比較
        if not working_urls:
            comparison_result["error"] = "沒有提供可比較的工作URL"
            return comparison_result

        # 分析當前頁面的模式
        current_patterns = self.analyze_page_structure(current_html)["patterns_found"]

        # 嘗試獲取一個工作例子並分析
        for working_url in working_urls[:1]:  # 只取第一個工作URL進行比較
            try:
                # 使用 NetworkManager 發送請求（如果提供）
                if network_manager:
                    response = network_manager.request_with_retry(working_url)
                else:
                    # 回退到直接使用 requests（向後相容）
                    headers = self.get_headers_from_main_program()
                    response = requests.get(working_url, headers=headers, timeout=20)

                if response and response.status_code == 200:
                    working_html = response.text
                    working_patterns = self.analyze_page_structure(working_html)[
                        "patterns_found"
                    ]

                    # 比較模式差異
                    for pattern_type in working_patterns:
                        if pattern_type in current_patterns:
                            if (
                                working_patterns[pattern_type]
                                and not current_patterns[pattern_type]
                            ):
                                comparison_result["differences_found"] = True
                                comparison_result["pattern_differences"][
                                    pattern_type
                                ] = {
                                    "working_example": working_patterns[pattern_type],
                                    "current_page": "無匹配模式",
                                }
                            elif set(working_patterns[pattern_type]) != set(
                                current_patterns[pattern_type]
                            ):
                                comparison_result["differences_found"] = True
                                comparison_result["pattern_differences"][
                                    pattern_type
                                ] = {
                                    "working_example": working_patterns[pattern_type],
                                    "current_page": current_patterns[pattern_type],
                                }
                elif response:
                    comparison_result["error"] = (
                        f"無法獲取工作URL: HTTP {response.status_code}"
                    )
                else:
                    comparison_result["error"] = "無法獲取工作URL: 請求失敗"
            except Exception as e:
                comparison_result["error"] = f"比較過程發生錯誤: {str(e)}"

        return comparison_result

    def get_headers_from_main_program(self) -> Dict[str, str]:
        """
        從主程序獲取請求頭，使用 CookieManager 以確保與主程式一致

        返回:
            請求頭字典
        """
        from package.network.NetworkManager import NetworkManager
        from package.utils.CookieManager import CookieManager

        # 優先使用 CookieManager（與主程式一致）
        try:
            cookie_manager = CookieManager()
            user_agent = NetworkManager.get_random_user_agent()
            headers = cookie_manager.get_headers(user_agent)

            # 如果成功取得認證資訊，直接返回
            if "authorization" in headers and "cookie" in headers:
                return headers
        except Exception as e:
            print(f"[診斷] 使用 CookieManager 時發生錯誤: {str(e)}")

        # 回退到舊版 permissions.txt（向後相容）
        try:
            headers_path = os.path.join(os.getcwd(), "package", "permissions.txt")
            if os.path.exists(headers_path):
                with open(headers_path, encoding="utf-8") as f:
                    txt = list(f)
                return {
                    "user-agent": NetworkManager.get_random_user_agent(),
                    "authorization": txt[0].split(",")[-1].replace("\n", ""),
                    "cookie": txt[1].split(",")[-1].replace("\n", ""),
                }
        except Exception as e:
            print(f"[診斷] 讀取 permissions.txt 時發生錯誤: {str(e)}")

        # 最終回退：只有 User-Agent
        return {"user-agent": NetworkManager.get_random_user_agent()}

    def suggest_extraction_strategies(
        self, analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        基於頁面分析建議提取策略

        參數:
            analysis_result: 頁面分析結果

        返回:
            建議的提取策略列表
        """
        suggestions = []

        patterns = analysis_result["patterns_found"]

        # 如果找到 m3u8 URL
        if patterns["m3u8_urls"]:
            suggestions.append(
                {
                    "strategy": "direct_m3u8_extraction",
                    "description": "直接從頁面提取 m3u8 URL",
                    "urls": patterns["m3u8_urls"],
                    "priority": "高",
                }
            )

        # 如果找到 transcode 模式
        if patterns["transcode_patterns"]:
            suggestions.append(
                {
                    "strategy": "transcode_pattern_extraction",
                    "description": "通過 transcode 模式提取",
                    "patterns": patterns["transcode_patterns"],
                    "priority": "中",
                }
            )

        # 如果找到播放列表模式
        if patterns["playlist_patterns"]:
            suggestions.append(
                {
                    "strategy": "playlist_extraction",
                    "description": "通過播放列表模式提取",
                    "patterns": patterns["playlist_patterns"],
                    "priority": "中",
                }
            )

        # 檢查腳本中的媒體信息
        if analysis_result["scripts"]:
            suggestions.append(
                {
                    "strategy": "script_content_extraction",
                    "description": "分析JavaScript腳本中的媒體信息",
                    "script_count": len(analysis_result["scripts"]),
                    "priority": "中",
                }
            )

        # 檢查API請求
        suggestions.append(
            {
                "strategy": "network_request_monitoring",
                "description": "監控網絡請求以捕獲媒體URL",
                "priority": "低",
            }
        )

        return suggestions

    def test_extraction_method(
        self, method_name: str, html_content: str
    ) -> Dict[str, Any]:
        """
        測試特定的提取方法

        參數:
            method_name: 提取方法名稱
            html_content: 頁面HTML內容

        返回:
            測試結果
        """
        soup = BeautifulSoup(html_content, "html.parser")
        result = {"method": method_name, "success": False, "url": None, "details": {}}

        if method_name == "meta_transcode":
            # 方法1: 通過meta標籤尋找transcode
            content_check = [
                i["content"] for i in soup.find_all("meta") if "transcode" in str(i)
            ]
            if len(content_check) != 0:
                result["success"] = True
                result["url"] = content_check[0]
                result["details"]["meta_tags_found"] = len(content_check)

        elif method_name == "div_m3u8_playlist":
            # 方法2: 通過div元素尋找m3u8和playList
            content_check = []
            for div in soup.find_all("div", {"class", "w-full"}):
                if (
                    "m3u8" in str(div)
                    and "playList" in str(div)
                    and "transcode_video" in str(div)
                ):
                    content_check += [str(div)]
            if len(content_check) != 0:
                m3u8_url = (
                    content_check[0].split("vidSrc=")[-1].split(".m3u8")[0] + ".m3u8"
                )
                result["success"] = True
                result["url"] = m3u8_url
                result["details"]["div_elements_found"] = len(content_check)

        elif method_name == "direct_regex_m3u8":
            # 方法3: 直接使用正則表達式尋找m3u8 URL
            m3u8_urls = re.findall(r'https?://[^\s\'"\)]+\.m3u8', html_content)
            if m3u8_urls:
                result["success"] = True
                result["url"] = m3u8_urls[0]
                result["details"]["urls_found"] = m3u8_urls
                result["details"]["url_count"] = len(m3u8_urls)

        elif method_name == "json_data_extraction":
            # 方法4: 尋找JSON數據中的媒體URL
            json_pattern = re.compile(r'({[^{}]*"[^"]*video[^"]*"[^{}]*})')
            json_matches = json_pattern.findall(html_content)

            for json_str in json_matches:
                try:
                    # 嘗試修復和解析JSON
                    fixed_json = re.sub(
                        r"([{,])\s*([a-zA-Z0-9_]+):", r'\1"\2":', json_str
                    )
                    data = json.loads(fixed_json)

                    # 在數據中尋找URL
                    for _key, value in data.items():
                        if isinstance(value, str) and (
                            value.endswith(".m3u8") or value.endswith(".mp4")
                        ):
                            result["success"] = True
                            result["url"] = value
                            result["details"]["json_data"] = data
                            break
                except json.JSONDecodeError:
                    continue

        elif method_name == "script_variable_extraction":
            # 方法5: 從腳本變量中提取URL
            script_pattern = re.compile(
                r'var\s+(\w+)\s*=\s*[\'"]([^\'"]*(\.m3u8|\.mp4))[\'"]'
            )
            script_matches = script_pattern.findall(html_content)

            if script_matches:
                result["success"] = True
                result["url"] = script_matches[0][1]
                result["details"]["variable_matches"] = script_matches

        return result

    def finalize_session(
        self,
        success: bool,
        final_url: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """
        完成診斷會話並保存結果

        參數:
            success: 是否成功解析URL
            final_url: 最終解析的URL
            notes: 額外註釋
        """
        if not self.current_session_id:
            print("[診斷] 錯誤: 在開始會話前嘗試完成會話")
            return

        self.diagnostic_data["final_result"] = {
            "success": success,
            "url": final_url,
            "notes": notes,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 保存診斷數據
        save_path = os.path.join(
            self.base_path, f"diagnostic_{self.current_session_id}.json"
        )
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(self.diagnostic_data, f, ensure_ascii=False, indent=2)

        if self.verbose:
            status = "成功" if success else "失敗"
            print(f"[診斷] 會話 {self.current_session_id} 已完成 ({status})")
            print(f"[診斷] 診斷數據已保存至: {save_path}")

        # 清理當前會話
        self.current_url = None
        self.current_session_id = None
        self.diagnostic_data = {}

    def generate_report(self, session_id: Optional[str] = None) -> str:
        """
        生成診斷報告

        參數:
            session_id: 特定會話ID，如果為None則使用當前會話

        返回:
            診斷報告的字符串表示
        """
        data = None

        if session_id:
            # 讀取指定會話的診斷數據
            save_path = os.path.join(self.base_path, f"diagnostic_{session_id}.json")
            if os.path.exists(save_path):
                with open(save_path, encoding="utf-8") as f:
                    data = json.load(f)
            else:
                return f"找不到會話ID: {session_id} 的診斷數據"
        elif self.current_session_id:
            # 使用當前會話的診斷數據
            data = self.diagnostic_data
        else:
            return "沒有活動的診斷會話"

        # 生成報告
        report = []
        report.append("=" * 50)
        report.append("JVID 媒體解析診斷報告")
        report.append("=" * 50)
        report.append(f"URL: {data['url']}")
        report.append(f"時間: {data['timestamp']}")
        report.append(f"會話ID: {data['session_id']}")
        report.append("-" * 50)

        # 最終結果
        final_result = data.get("final_result", {})
        if final_result:
            status = "成功" if final_result.get("success", False) else "失敗"
            report.append(f"解析結果: {status}")
            if final_result.get("url"):
                report.append(f"解析URL: {final_result['url']}")
            if final_result.get("notes"):
                report.append(f"備註: {final_result['notes']}")
        else:
            report.append("解析結果: 未完成")

        report.append("-" * 50)

        # URL提取嘗試
        extraction_attempts = data.get("extraction_attempts", [])
        if extraction_attempts:
            report.append("URL提取嘗試:")
            for i, attempt in enumerate(extraction_attempts, 1):
                status = "成功" if attempt.get("success", False) else "失敗"
                method = attempt.get("method", "未知方法")
                report.append(f"{i}. {method}: {status}")
                if attempt.get("extracted_url"):
                    report.append(f"   URL: {attempt['extracted_url']}")
        else:
            report.append("URL提取嘗試: 無")

        report.append("-" * 50)

        # 發現的模式
        patterns = data.get("html_patterns", {})
        if patterns:
            report.append("發現的模式:")
            for pattern_type, pattern_list in patterns.items():
                if pattern_list:
                    report.append(f"- {pattern_type}: {len(pattern_list)} 個匹配")
                    for pattern in pattern_list[:3]:  # 只顯示前3個
                        report.append(f"  * {pattern}")
                    if len(pattern_list) > 3:
                        report.append(f"  * ... 還有 {len(pattern_list) - 3} 個匹配")
                else:
                    report.append(f"- {pattern_type}: 無匹配")

        report.append("=" * 50)

        return "\n".join(report)

    @staticmethod
    def extract_failed_urls_from_log(log_path: str) -> List[str]:
        """
        從下載日誌中提取失敗的URL

        參數:
            log_path: 日誌檔案路徑

        返回:
            失敗URL列表
        """
        failed_urls = []

        if not os.path.exists(log_path):
            print(f"[診斷] 找不到日誌檔案: {log_path}")
            return failed_urls

        try:
            with open(log_path, encoding="utf-8") as f:
                for line in f:
                    if "下載失敗" in line and "URL:" in line:
                        url_part = line.split("URL:")[-1].strip()
                        failed_urls.append(url_part)
        except Exception as e:
            print(f"[診斷] 讀取日誌檔案時出錯: {str(e)}")

        return failed_urls
