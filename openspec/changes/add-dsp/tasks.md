## 1. 前置作業：理解與規劃

- [x] 1.1 閱讀現有 `scraper.py` 全文，確認所有私有方法的輸入/輸出簽名（`_is_noise`、`_split_sentences`、`_extract_snippet`、`_extract_url`、`_extract_source`、`_extract_pubdate`）
- [x] 1.2 閱讀現有 `app.py` 全文，確認 `Scraper` 的使用方式（實例化參數、呼叫的方法）
- [x] 1.3 確認 Python 版本支援 `from abc import ABC, abstractmethod`（Python >= 3.4 均支援）

## 2. Strategy Pattern：SnippetStrategy 介面與具體策略

- [x] 2.1 在 `scraper.py` 尾端新增 `from abc import ABC, abstractmethod` import（若尚未存在）
- [x] 2.2 定義 `SnippetStrategy(ABC)` 抽象類別，宣告 `extract(sentences: list[str], keyword: str) -> str` 抽象方法
- [x] 2.3 定義 `KeywordFirstStrategy(SnippetStrategy)` 具體類別，實作「關鍵字優先」邏輯（移植原 `_extract_snippet()` 的三段式選取邏輯）
- [x] 2.4 定義 `LengthFirstStrategy(SnippetStrategy)` 具體類別，實作「純長度優先」邏輯（忽略 keyword 參數，只看長度）
- [x] 2.5 確認 `KeywordFirstStrategy` 與原 `Scraper._extract_snippet()` 在相同輸入下回傳相同結果

## 3. Facade Pattern：NewsFetcher、NewsParser、ScraperFacade

- [x] 3.1 定義 `NewsFetcher` 類別，將 `Scraper.fetch()` 的 HTTP 邏輯遷移進來，方法簽名改為 `fetch(keyword: str) -> str`
- [x] 3.2 定義 `NewsParser` 類別，將 `Scraper.parse()` 及所有輔助私有方法（`_is_noise`、`_split_sentences`、`_extract_url`、`_extract_source`、`_extract_pubdate`）遷移進來
- [x] 3.3 `NewsParser.__init__` 接受 `strategy: SnippetStrategy = None`，若 None 則預設使用 `KeywordFirstStrategy()`
- [x] 3.4 `NewsParser.parse(raw_xml, keyword, max_results)` 內的 snippet 邏輯改為呼叫 `self.strategy.extract(sentences, keyword)`，刪除原本的 if/else 選取邏輯
- [x] 3.5 定義 `ScraperFacade` 類別，`__init__(keyword, max_results=10)` 建立 `self._fetcher = NewsFetcher()` 與 `self._parser = NewsParser()`
- [x] 3.6 `ScraperFacade.run()` 實作：呼叫 `_fetcher.fetch()` → 呼叫 `_parser.parse()` → 轉 DataFrame → 依刊登時間排序 → 回傳
- [x] 3.7 在 `scraper.py` 尾端新增 `Scraper = ScraperFacade`（向下相容別名）

## 4. Observer Pattern：ScraperObserver 介面與 StreamlitProgressObserver

- [x] 4.1 定義 `ScraperObserver(ABC)` 抽象類別，宣告三個抽象方法：`on_fetch_start(keyword: str)`、`on_fetch_done()`、`on_parse_done(count: int)`
- [x] 4.2 在 `ScraperFacade` 新增 `self._observers: list[ScraperObserver] = []`
- [x] 4.3 在 `ScraperFacade` 新增 `attach(observer: ScraperObserver) -> None` 方法，將 observer 加入 `self._observers`
- [x] 4.4 在 `ScraperFacade.run()` 的對應位置插入 observer 通知邏輯（fetch 前呼叫 `on_fetch_start`、fetch 後呼叫 `on_fetch_done`、parse 後呼叫 `on_parse_done`），每個通知包裝在 `try/except Exception: pass` 中
- [x] 4.5 定義 `StreamlitProgressObserver(ScraperObserver)` 具體類別，實作三個方法（每個方法以 `try/except Exception: pass` 包裹 `st.session_state` 的寫入）

## 5. 修改 app.py 整合新架構

- [x] 5.1 將 `from scraper import Scraper` 改為 `from scraper import ScraperFacade, StreamlitProgressObserver`
- [x] 5.2 將 `scraper = Scraper(keyword=keyword, max_results=10)` 改為 `scraper = ScraperFacade(keyword=keyword, max_results=10)`
- [x] 5.3 在建立 `ScraperFacade` 後插入 `scraper.attach(StreamlitProgressObserver())` 訂閱進度事件
- [x] 5.4 確認 `scraper.run()` 呼叫方式不變，回傳 DataFrame 格式與原版相同

## 6. 功能驗證

- [x] 6.1 執行 `streamlit run app.py`，輸入關鍵字（例如「台積電」），確認搜尋結果正常顯示
- [x] 6.2 確認 DataFrame 欄位（`標題`、`刊登時間`、`來源`、`關鍵句子`、`網址`）與重構前完全一致
- [x] 6.3 確認按刊登時間降冪排序仍正確運作
- [x] 6.4 確認空關鍵字輸入仍顯示警告訊息，不執行爬蟲

## 7. 生成說明文件

- [x] 7.1 在專案根目錄新增 `design_patterns_reference.md`，包含全部 23 種 GoF 設計模式的整理（分類、一句話定義、使用時機、核心角色）
- [x] 7.2 在專案根目錄新增 `design_patterns_usage.md`，包含本專案三個 pattern 的套用說明（位置、前後對比、效益、Mermaid UML 圖）
- [x] 7.3 確認 `design_patterns_usage.md` 的最後一節包含「三個模式如何協同運作」的整體說明
