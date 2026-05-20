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
from email.utils import parsedate_to_datetime


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

    # 已知的廣告／媒體自介樣板詞
    # 句子中只要命中任一，整句視為垃圾並跳過
    _NOISE_PATTERNS = [
        # Yahoo / Google 推廣語
        "設為首選來源",
        "查看更多我們的精彩報導",
        "在 Google 上查看",
        "在 Yahoo 上查看",
        # 媒體自我介紹
        "致力為全球華文受眾",
        "提供獨立、可信、中立",
        "擁有國際視角、深度、廣度和維度",
        # 其他常見樣板
        "訂閱電子報",
        "加入會員",
    ]

    def _is_noise(self, sentence: str) -> bool:
        """句子中含有任一噪音樣板，則整句視為垃圾。"""
        return any(pattern in sentence for pattern in self._NOISE_PATTERNS)

    def _split_sentences(self, text: str) -> list[str]:
        """
        將描述文字切成句子列表。
        只按句號、問號、驚嘆號拆分，保留完整句子（含句末標點）。
        """
        sentences = []
        for line in text.splitlines():
            for seg in (
                line.replace("。", "。\n")
                    .replace("！", "！\n")
                    .replace("？", "？\n")
                    .splitlines()
            ):
                seg = seg.strip()
                if seg:
                    sentences.append(seg)
        return sentences

    def _extract_snippet(self, description: str, keyword: str = "") -> str:
        """
        取得文章描述中最相關的句子，截取前 50 字並加上「...」。

        流程：切句 → 整句含噪音就跳過 → 依優先序選取乾淨句子。

        優先序：
        1. 不是垃圾 + 含關鍵字 + >= 20 字
        2. 不是垃圾 + >= 50 字
        3. 不是垃圾 + >= 20 字
        4. 找不到乾淨句子 → 回傳空字串

        Args:
            description: RSS description 欄位文字（已去除 HTML 標籤）
            keyword: 搜尋關鍵字，用於優先匹配含關鍵字的句子

        Returns:
            完整句子（<= 50 字）或截斷前 50 字加「...」；無乾淨內容時為空字串
        """
        if not description:
            return ""

        sentences = self._split_sentences(description)
        clean = [s for s in sentences if not self._is_noise(s)]

        def fmt(s: str) -> str:
            return s if len(s) <= 50 else s[:50] + "..."

        # 1. 含關鍵字 + >= 20 字
        if keyword:
            for s in clean:
                if len(s) >= 20 and keyword in s:
                    return fmt(s)

        # 2. >= 50 字
        for s in clean:
            if len(s) >= 50:
                return fmt(s)

        # 3. >= 20 字
        for s in clean:
            if len(s) >= 20:
                return fmt(s)

        # 找不到乾淨句子
        return ""

    def _extract_pubdate(self, item: BeautifulSoup) -> str:
        """
        從 RSS item 的 <pubDate> 標籤提取刊登時間。

        RSS pubDate 格式為 RFC 2822（如 Tue, 01 Apr 2026 08:00:00 GMT），
        解析後格式化為 YYYY/MM/DD HH:MM。

        Args:
            item: BeautifulSoup 解析後的單一 RSS item 元素

        Returns:
            格式化後的時間字串，解析失敗時回傳空字串
        """
        pubdate_tag = item.find("pubDate")
        if not pubdate_tag:
            return ""
        try:
            dt = parsedate_to_datetime(pubdate_tag.get_text(strip=True))
            return dt.strftime("%Y/%m/%d %H:%M")
        except Exception:
            return ""

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
            snippet = self._extract_snippet(description, keyword=self.keyword)

            # 提取刊登時間（RSS pubDate 欄位）
            pubdate = self._extract_pubdate(item)

            results.append({
                "標題": title,
                "刊登時間": pubdate,
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
        df = pd.DataFrame(results)

        # 依刊登時間由近到遠排序（空值排最後）
        if "刊登時間" in df.columns and not df.empty:
            df = df.sort_values("刊登時間", ascending=False, na_position="last").reset_index(drop=True)

        return df


# ══════════════════════════════════════════════════════════════════════════════
# Design Patterns Implementation
# ══════════════════════════════════════════════════════════════════════════════
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────────────────────
# Strategy Pattern（策略模式）
# Context: NewsParser
# Strategy Interface: SnippetStrategy
# Concrete Strategies: KeywordFirstStrategy, LengthFirstStrategy
#
# 效益：snippet 萃取邏輯可在不修改 NewsParser 的情況下替換或擴展，
#       符合開放封閉原則（OCP）。
# ─────────────────────────────────────────────────────────────────────────────

class SnippetStrategy(ABC):
    """摘要萃取策略介面（Strategy Pattern）。"""

    _NOISE_PATTERNS = [
        "設為首選來源", "查看更多我們的精彩報導",
        "在 Google 上查看", "在 Yahoo 上查看",
        "致力為全球華文受眾", "提供獨立、可信、中立",
        "擁有國際視角、深度、廣度和維度",
        "訂閱電子報", "加入會員",
    ]

    @abstractmethod
    def extract(self, sentences: list[str], keyword: str) -> str:
        """從句子列表中萃取最相關的一句，超過 50 字則截斷並加「...」。"""
        ...

    def _is_noise(self, sentence: str) -> bool:
        return any(p in sentence for p in self._NOISE_PATTERNS)

    @staticmethod
    def _fmt(s: str) -> str:
        return s if len(s) <= 50 else s[:50] + "..."


class KeywordFirstStrategy(SnippetStrategy):
    """關鍵字優先策略：優先回傳含關鍵字的乾淨句子，再依長度 fallback。"""

    def extract(self, sentences: list[str], keyword: str) -> str:
        clean = [s for s in sentences if not self._is_noise(s)]

        if keyword:
            for s in clean:
                if len(s) >= 20 and keyword in s:
                    return self._fmt(s)

        for s in clean:
            if len(s) >= 50:
                return self._fmt(s)

        for s in clean:
            if len(s) >= 20:
                return self._fmt(s)

        return ""


class LengthFirstStrategy(SnippetStrategy):
    """長度優先策略：忽略關鍵字，純依句子長度選取最長的乾淨句子。"""

    def extract(self, sentences: list[str], keyword: str) -> str:
        clean = [s for s in sentences if not self._is_noise(s)]

        for s in clean:
            if len(s) >= 50:
                return self._fmt(s)

        for s in clean:
            if len(s) >= 20:
                return self._fmt(s)

        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Observer Pattern（觀察者模式）
# Subject: ScraperFacade
# Observer Interface: ScraperObserver
# Concrete Observer: StreamlitProgressObserver
#
# 效益：爬蟲核心邏輯與 UI 進度顯示完全解耦，
#       可在不修改 ScraperFacade 的情況下新增或替換觀察者。
# ─────────────────────────────────────────────────────────────────────────────

class ScraperObserver(ABC):
    """爬蟲觀察者介面（Observer Pattern）。"""

    @abstractmethod
    def on_fetch_start(self, keyword: str) -> None:
        """HTTP 爬取請求發出前觸發。"""
        ...

    @abstractmethod
    def on_fetch_done(self) -> None:
        """HTTP 回應接收完畢後觸發。"""
        ...

    @abstractmethod
    def on_parse_done(self, count: int) -> None:
        """XML 解析完成、取得結果筆數後觸發。"""
        ...


class StreamlitProgressObserver(ScraperObserver):
    """透過 st.session_state 向 Streamlit UI 回報爬取進度。"""

    def on_fetch_start(self, keyword: str) -> None:
        try:
            import streamlit as st
            st.session_state["scrape_status"] = "fetching"
        except Exception:
            pass

    def on_fetch_done(self) -> None:
        try:
            import streamlit as st
            st.session_state["scrape_status"] = "parsing"
        except Exception:
            pass

    def on_parse_done(self, count: int) -> None:
        try:
            import streamlit as st
            st.session_state["scrape_status"] = "done"
            st.session_state["scrape_count"] = count
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
# Facade Pattern（外觀模式）
# Facade: ScraperFacade
# Subsystem A: NewsFetcher（HTTP 爬取子系統）
# Subsystem B: NewsParser（XML 解析子系統）
#
# 效益：外部呼叫者（app.py）只需呼叫 facade.run()，
#       不需了解子系統內部細節，降低模組間耦合度。
# ─────────────────────────────────────────────────────────────────────────────

class NewsFetcher:
    """HTTP 爬取子系統：封裝所有網路請求與爬蟲禮儀細節。"""

    RSS_URL_TEMPLATE = "https://www.bing.com/news/search?q={keyword}&format=RSS"

    def fetch(self, keyword: str) -> str:
        url = self.RSS_URL_TEMPLATE.format(keyword=requests.utils.quote(keyword))
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        raw_xml = response.text
        time.sleep(1)
        return raw_xml


class NewsParser:
    """XML 解析子系統：封裝 BeautifulSoup 解析、欄位提取，並委派 snippet 策略。"""

    _NOISE_PATTERNS = [
        "設為首選來源", "查看更多我們的精彩報導",
        "在 Google 上查看", "在 Yahoo 上查看",
        "致力為全球華文受眾", "提供獨立、可信、中立",
        "擁有國際視角、深度、廣度和維度",
        "訂閱電子報", "加入會員",
    ]

    def __init__(self, strategy: SnippetStrategy = None):
        self.strategy: SnippetStrategy = strategy if strategy is not None else KeywordFirstStrategy()

    def _is_noise(self, sentence: str) -> bool:
        return any(p in sentence for p in self._NOISE_PATTERNS)

    def _split_sentences(self, text: str) -> list[str]:
        sentences = []
        for line in text.splitlines():
            for seg in (
                line.replace("。", "。\n")
                    .replace("！", "！\n")
                    .replace("？", "？\n")
                    .splitlines()
            ):
                seg = seg.strip()
                if seg:
                    sentences.append(seg)
        return sentences

    def _extract_url(self, item) -> str:
        link_tag = item.find("link")
        if not link_tag:
            return ""
        bing_url = link_tag.get_text(strip=True)
        try:
            parsed = urlparse(bing_url)
            params = parse_qs(parsed.query)
            if "url" in params:
                return params["url"][0]
        except Exception:
            pass
        return bing_url

    def _extract_source(self, item) -> str:
        news_source = item.find("News:Source")
        if news_source and news_source.get_text(strip=True):
            return news_source.get_text(strip=True)
        return "（未知來源）"

    def _extract_pubdate(self, item) -> str:
        pubdate_tag = item.find("pubDate")
        if not pubdate_tag:
            return ""
        try:
            dt = parsedate_to_datetime(pubdate_tag.get_text(strip=True))
            return dt.strftime("%Y/%m/%d %H:%M")
        except Exception:
            return ""

    def parse(self, raw_xml: str, keyword: str, max_results: int) -> list[dict]:
        soup = BeautifulSoup(raw_xml, "lxml-xml")
        items = soup.find_all("item")[:max_results]
        results = []
        for item in items:
            title_tag = item.find("title")
            title = title_tag.get_text(strip=True) if title_tag else "（無標題）"
            url = self._extract_url(item)
            source = self._extract_source(item)
            desc_tag = item.find("description")
            if desc_tag:
                desc_soup = BeautifulSoup(desc_tag.get_text(), "html.parser")
                description = desc_soup.get_text(strip=True)
            else:
                description = ""
            sentences = self._split_sentences(description)
            snippet = self.strategy.extract(sentences, keyword)
            pubdate = self._extract_pubdate(item)
            results.append({
                "標題": title,
                "刊登時間": pubdate,
                "來源": source,
                "關鍵句子": snippet,
                "網址": url,
            })
        return results


class ScraperFacade:
    """爬蟲外觀類別（Facade Pattern）：對外統一介面，隱藏子系統複雜度。

    同時作為 Observer Pattern 的 Subject，在各爬取階段通知已訂閱的觀察者。
    """

    def __init__(self, keyword: str, max_results: int = 10):
        self.keyword = keyword.strip()
        self.max_results = max_results
        self._fetcher = NewsFetcher()
        self._parser = NewsParser()
        self._observers: list[ScraperObserver] = []

    def attach(self, observer: ScraperObserver) -> None:
        """訂閱爬取進度事件。"""
        self._observers.append(observer)

    def _notify(self, event: str, **kwargs) -> None:
        for obs in self._observers:
            try:
                getattr(obs, event)(**kwargs)
            except Exception:
                pass

    def run(self) -> pd.DataFrame:
        """執行完整爬取流程：fetch → parse → sort → DataFrame。"""
        self._notify("on_fetch_start", keyword=self.keyword)
        raw_xml = self._fetcher.fetch(self.keyword)
        self._notify("on_fetch_done")
        results = self._parser.parse(raw_xml, self.keyword, self.max_results)
        self._notify("on_parse_done", count=len(results))
        df = pd.DataFrame(results)
        if "刊登時間" in df.columns and not df.empty:
            df = df.sort_values("刊登時間", ascending=False, na_position="last").reset_index(drop=True)
        return df


# 向下相容別名：讓既有的 `from scraper import Scraper` 繼續正常運作
Scraper = ScraperFacade
