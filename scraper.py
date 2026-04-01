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
from urllib.parse import urlparse, parse_qs


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

    # Bing News RSS Feed 搜尋網址模板（description 欄位包含真正的文章摘要）
    RSS_URL_TEMPLATE = "https://www.bing.com/news/search?q={keyword}&format=RSS"

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
        取得文章描述的第一段文字（>= 20 字），超過 50 字則截斷並加上「...」。

        Args:
            description: RSS description 欄位文字（已去除 HTML 標籤）

        Returns:
            最多 50 字的第一段摘要
        """
        if not description:
            return ""

        # 取第一個長度 >= 20 的非空段落
        for line in description.splitlines():
            line = line.strip()
            if len(line) >= 20:
                return line[:50] + ("..." if len(line) > 50 else "")

        # 所有段落都太短，直接取前 50 字
        text = description.strip()
        return text[:50] + ("..." if len(text) > 50 else "")

    def _extract_source(self, item: BeautifulSoup) -> str:
        """
        從 Bing News RSS item 中提取來源名稱。

        Bing News 使用 <News:Source> 標籤存放來源名稱。

        Args:
            item: BeautifulSoup 解析後的單一 RSS item 元素

        Returns:
            來源名稱字串
        """
        # Bing News 的來源在 <News:Source> 標籤
        news_source = item.find("News:Source")
        if news_source and news_source.get_text(strip=True):
            return news_source.get_text(strip=True)

        return "（未知來源）"

    def _extract_url(self, item: BeautifulSoup) -> str:
        """
        從 Bing News RSS item 中提取真正的文章 URL。

        Bing News 的 <link> 是重導向連結，真正的文章 URL
        藏在其 url= 查詢參數中。

        Args:
            item: BeautifulSoup 解析後的單一 RSS item 元素

        Returns:
            文章原始 URL 字串
        """
        link_tag = item.find("link")
        if not link_tag:
            return ""

        bing_url = link_tag.get_text(strip=True)
        try:
            # 從 Bing redirect URL 解析 url= 參數取得真正文章網址
            parsed = urlparse(bing_url)
            params = parse_qs(parsed.query)
            if "url" in params:
                return params["url"][0]
        except Exception:
            pass

        return bing_url

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

            # 提取真正的文章網址（從 Bing redirect URL 解析）
            url = self._extract_url(item)

            # 提取來源（Bing News 用 <News:Source> 標籤）
            source = self._extract_source(item)

            # 從 RSS description 欄位擷取第一段文字
            desc_tag = item.find("description")
            if desc_tag:
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
