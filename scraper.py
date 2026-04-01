"""
scraper.py — 爬蟲引擎模組（Model 層）

此模組定義 Scraper 類別，負責所有網路請求與資料解析邏輯。
UI 層不應包含任何爬取或解析邏輯，所有爬蟲行為皆封裝於此。

架構角色：MVC 中的 Model
"""

import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class Scraper:
    """
    Web 關鍵字爬蟲類別。

    負責向 Google News RSS Feed 發出 HTTP 請求，
    解析 XML 回應，並提取結構化資料。

    屬性：
        keyword (str): 使用者輸入的搜尋關鍵字
        max_results (int): 最多回傳的結果筆數（預設 10）
        _raw_xml (str | None): 原始 XML 回應內容（fetch 後才有值）
    """

    # Google News RSS Feed 搜尋網址模板
    RSS_URL_TEMPLATE = "https://news.google.com/rss/search?q={keyword}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"

    def __init__(self, keyword: str, max_results: int = 10):
        """
        初始化 Scraper 物件。

        Args:
            keyword: 搜尋關鍵字（中文或英文均可）
            max_results: 最多回傳筆數，預設為 10
        """
        self.keyword = keyword.strip()
        self.max_results = max_results
        self._raw_xml: str | None = None

    def fetch(self) -> None:
        """
        向 Google News RSS 發出 HTTP GET 請求，取得 XML 原始內容。

        加入 timeout=10 秒避免無限等待，
        加入 time.sleep(1) 符合爬蟲禮儀，避免對伺服器造成負擔。

        Raises:
            requests.exceptions.ConnectionError: 無法連線至目標伺服器
            requests.exceptions.Timeout: 請求超過 10 秒未收到回應
            requests.exceptions.HTTPError: 伺服器回傳 4xx/5xx 狀態碼
        """
        url = self.RSS_URL_TEMPLATE.format(keyword=requests.utils.quote(self.keyword))

        # 設定 User-Agent 模擬瀏覽器，部分伺服器會拒絕空 User-Agent
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

        # 發出 GET 請求，設定 10 秒 timeout
        response = requests.get(url, headers=headers, timeout=10)

        # 若伺服器回傳錯誤狀態碼，拋出例外
        response.raise_for_status()

        # 儲存原始 XML 內容
        self._raw_xml = response.text

        # 爬蟲禮儀：請求完成後等待 1 秒
        time.sleep(1)

    def _extract_snippet(self, description: str) -> str:
        """
        從文章描述中擷取包含關鍵字的片段（字串匹配，非 AI 邏輯）。

        搜尋關鍵字在描述文字中的位置，擷取前後各 50 個字元。
        若關鍵字不存在，則回傳描述的前 100 個字元。

        Args:
            description: 文章描述文字

        Returns:
            包含關鍵字前後文的字串片段
        """
        if not description:
            return ""

        # 不分大小寫搜尋關鍵字位置
        lower_desc = description.lower()
        lower_keyword = self.keyword.lower()
        pos = lower_desc.find(lower_keyword)

        if pos == -1:
            # 關鍵字不在描述中，回傳前 100 個字元
            return description[:100] + ("..." if len(description) > 100 else "")

        # 計算擷取範圍（前後各 50 字元，不超出字串邊界）
        start = max(0, pos - 50)
        end = min(len(description), pos + len(self.keyword) + 50)

        snippet = description[start:end]

        # 若非從頭開始，加上省略號表示有前文
        if start > 0:
            snippet = "..." + snippet
        if end < len(description):
            snippet = snippet + "..."

        return snippet

    def _extract_source(self, item: BeautifulSoup, link: str) -> str:
        """
        從 RSS item 中提取來源名稱。

        優先使用 <source> 標籤，若不存在則從 URL 解析網域名稱。

        Args:
            item: BeautifulSoup 解析後的單一 RSS item 元素
            link: 文章連結 URL

        Returns:
            來源名稱字串
        """
        # 嘗試從 <source> 標籤取得來源名稱
        source_tag = item.find("source")
        if source_tag and source_tag.get_text(strip=True):
            return source_tag.get_text(strip=True)

        # 若無 <source> 標籤，從 URL 解析網域名稱
        if link:
            try:
                parsed = urlparse(link)
                return parsed.netloc  # 例如：news.example.com
            except Exception:
                pass

        return "（未知來源）"

    def parse(self) -> list[dict]:
        """
        解析 fetch() 取得的 XML 內容，提取結構化資料。

        使用 BeautifulSoup 解析 RSS XML，
        對每個 <item> 提取標題、來源、關鍵句子、原網址。

        Returns:
            包含每筆文章資料的字典列表，每筆包含：
            - title (str): 文章標題
            - source (str): 來源網站名稱
            - snippet (str): 包含關鍵字的文字片段
            - url (str): 原始文章網址

        Raises:
            ValueError: 尚未執行 fetch() 或 XML 解析失敗
        """
        if self._raw_xml is None:
            raise ValueError("請先呼叫 fetch() 取得資料後再進行解析。")

        # 使用 lxml-xml 解析器解析 RSS XML
        soup = BeautifulSoup(self._raw_xml, "lxml-xml")

        # 取得所有文章項目，限制在 max_results 筆以內
        items = soup.find_all("item")[: self.max_results]

        results = []
        for item in items:
            # 提取標題
            title_tag = item.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "（無標題）"

            # 提取原網址
            link_tag = item.find("link")
            # BeautifulSoup 對 <link> 的處理方式視解析器而異
            if link_tag:
                url = link_tag.get_text(strip=True) or link_tag.get("href", "")
            else:
                url = ""

            # 提取來源
            source = self._extract_source(item, url)

            # 提取描述並生成關鍵句子
            desc_tag = item.find("description")
            if desc_tag:
                # 描述欄位可能含有 HTML 標籤，先去除
                desc_soup = BeautifulSoup(desc_tag.get_text(), "html.parser")
                description = desc_soup.get_text(strip=True)
            else:
                description = ""

            snippet = self._extract_snippet(description)

            results.append({
                "標題": title,
                "來源": source,
                "關鍵句子": snippet,
                "網址": url,
            })

        return results

    def run(self) -> pd.DataFrame:
        """
        執行完整的爬取流程：fetch → parse → 回傳 DataFrame。

        此為外部呼叫的主要入口，整合所有爬取與解析步驟。

        Returns:
            包含所有爬取結果的 Pandas DataFrame，
            欄位為：標題、來源、關鍵句子、網址

        Raises:
            requests.exceptions.ConnectionError: 網路連線失敗
            requests.exceptions.Timeout: 請求超時
            requests.exceptions.HTTPError: HTTP 錯誤狀態碼
            ValueError: XML 解析失敗
        """
        self.fetch()
        results = self.parse()
        return pd.DataFrame(results)
