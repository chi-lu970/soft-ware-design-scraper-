# 關鍵字爬蟲整合系統 — Design Patterns 實作報告

---

## Slide 1｜三種 Design Pattern 簡介

| Pattern | 核心概念 | 一句話說明 |
|---------|---------|-----------|
| **Strategy（策略模式）** | 將演算法封裝成獨立類別，可在執行期替換 | 「同一件事，做法可以抽換」 |
| **Facade（外觀模式）** | 提供一個簡單介面，隱藏子系統的複雜度 | 「對外只露一個入口」 |
| **Observer（觀察者模式）** | 當事件發生時，自動通知所有訂閱者 | 「發生了什麼，關心的人都會知道」 |

> 三種皆屬 **GoF（Gang of Four）** 設計模式，解決物件導向設計中常見的耦合與擴展問題。

### 本專案套用前的三個問題

```python
# ❌ 重構前：Scraper 一個類別包辦所有事

class Scraper:
    def fetch(self): ...        # 職責1：HTTP 爬取
    def _extract_snippet(self): # 職責2：選句邏輯全硬寫在這
        if keyword:
            for s in clean:
                if len(s) >= 20 and keyword in s:  # 策略寫死
                    return fmt(s)
        for s in clean:
            if len(s) >= 50: ...                   # 策略寫死
    def parse(self): ...        # 職責3：XML 解析
    def run(self): ...          # 全部混在一起
```

問題：職責混亂、策略無法替換、UI 進度只能硬寫在 `st.spinner`

---

## Slide 2｜在本系統中的應用（實際程式碼）

### Strategy — 套用於「關鍵句子選取」

```python
# scraper.py

class SnippetStrategy(ABC):              # 定義共同介面
    @abstractmethod
    def extract(self, sentences: list[str], keyword: str) -> str: ...

class KeywordFirstStrategy(SnippetStrategy):   # 具體策略 A（預設）
    def extract(self, sentences, keyword):
        clean = [s for s in sentences if not self._is_noise(s)]
        if keyword:
            for s in clean:
                if len(s) >= 20 and keyword in s:   # 關鍵字優先
                    return self._fmt(s)
        for s in clean:
            if len(s) >= 50: return self._fmt(s)    # fallback：長度
        return ""

class LengthFirstStrategy(SnippetStrategy):    # 具體策略 B
    def extract(self, sentences, keyword):      # 完全忽略 keyword
        clean = [s for s in sentences if not self._is_noise(s)]
        for s in clean:
            if len(s) >= 50: return self._fmt(s)
        return ""

class NewsParser:                        # Context：使用策略的人
    def __init__(self, strategy: SnippetStrategy = None):
        self.strategy = strategy or KeywordFirstStrategy()

    def parse(self, raw_xml, keyword, max_results):
        ...
        snippet = self.strategy.extract(sentences, keyword)  # ← 委派，不含任何 if/else
```

---

### Facade — 套用於「爬蟲入口」

```python
# scraper.py

class NewsFetcher:                       # 子系統 A：只管 HTTP
    def fetch(self, keyword: str) -> str:
        url = self.RSS_URL_TEMPLATE.format(keyword=requests.utils.quote(keyword))
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        time.sleep(1)
        return response.text             # 回傳原始 XML，不做解析

class NewsParser:                        # 子系統 B：只管解析
    def parse(self, raw_xml, keyword, max_results) -> list[dict]:
        soup = BeautifulSoup(raw_xml, "lxml-xml")
        ...                              # 只做解析，不碰 HTTP

class ScraperFacade:                     # Facade：統一對外介面
    def __init__(self, keyword, max_results=10):
        self._fetcher = NewsFetcher()    # 組合子系統
        self._parser  = NewsParser()

    def run(self) -> pd.DataFrame:       # app.py 唯一的呼叫點
        raw_xml = self._fetcher.fetch(self.keyword)
        results = self._parser.parse(raw_xml, self.keyword, self.max_results)
        df = pd.DataFrame(results)
        return df.sort_values("刊登時間", ascending=False)

# app.py 只需這兩行，不知道子系統的存在
scraper = ScraperFacade(keyword=keyword, max_results=10)
df = scraper.run()
```

---

### Observer — 套用於「爬取進度通知」

```python
# scraper.py

class ScraperObserver(ABC):              # Observer 介面
    @abstractmethod
    def on_fetch_start(self, keyword: str): ...
    @abstractmethod
    def on_fetch_done(self): ...
    @abstractmethod
    def on_parse_done(self, count: int): ...

class StreamlitProgressObserver(ScraperObserver):   # 具體 Observer
    def on_fetch_start(self, keyword):
        try:
            st.session_state["scrape_status"] = "fetching"
        except Exception: pass

    def on_fetch_done(self):
        try:
            st.session_state["scrape_status"] = "parsing"
        except Exception: pass

    def on_parse_done(self, count):
        try:
            st.session_state["scrape_status"] = "done"
            st.session_state["scrape_count"] = count
        except Exception: pass

class ScraperFacade:                     # Subject：事件發布者
    def run(self):
        self._notify("on_fetch_start", keyword=self.keyword)  # 通知
        raw_xml = self._fetcher.fetch(self.keyword)
        self._notify("on_fetch_done")                          # 通知
        results = self._parser.parse(raw_xml, ...)
        self._notify("on_parse_done", count=len(results))      # 通知
        ...

# app.py 訂閱 observer，一行搞定
scraper.attach(StreamlitProgressObserver())
```

---

## Slide 3｜為何這樣應用？帶來哪些優點？

| Pattern | 套用前的問題 | 套用後的優點 |
|---------|------------|------------|
| **Strategy** | 要改選句邏輯就要動 `Scraper` 原始碼，容易改壞 | 新增策略只加一個類別，`NewsParser` 完全不用改（**OCP**） |
| **Facade** | `Scraper` 職責過重，HTTP 出錯與解析出錯全混在一起 | 職責分離，`NewsFetcher` 可獨立替換，互不影響 |
| **Observer** | 進度寫死在 UI，爬蟲與 Streamlit 強綁定，無法單獨測試 | `ScraperFacade` 不依賴 Streamlit，可同時掛多個 Observer |

### 三個 Pattern 如何協同（實際執行流程）

```
app.py
  └─▶ scraper = ScraperFacade(keyword, max_results=10)   # Facade
      scraper.attach(StreamlitProgressObserver())         # Observer 訂閱
      df = scraper.run()
              │
              ├─ _notify("on_fetch_start") ──▶ UI 顯示「爬取中」  [Observer]
              ├─ NewsFetcher.fetch()                               [Facade 子系統 A]
              ├─ _notify("on_fetch_done")  ──▶ UI 顯示「解析中」  [Observer]
              ├─ NewsParser.parse()                                [Facade 子系統 B]
              │       └─ self.strategy.extract()                   [Strategy 委派]
              ├─ _notify("on_parse_done")  ──▶ UI 顯示「完成」    [Observer]
              └─ return DataFrame
```

> **結論**：Facade 管「入口整潔」、Strategy 管「邏輯可換」、Observer 管「狀態通知」。
> 三個模式各司其職，讓系統在不改變外部行為的前提下，大幅提升可維護性與擴展性。
