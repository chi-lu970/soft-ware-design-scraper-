## ADDED Requirements

### Requirement: NewsFetcher 子系統類別
系統 SHALL 定義 `NewsFetcher` 類別，封裝所有 HTTP 爬取的低階細節。

- `NewsFetcher` MUST 提供 `fetch(keyword: str) -> str` 方法，回傳原始 XML 字串。
- `fetch()` MUST 使用 `RSS_URL_TEMPLATE` 組建 URL，加入 User-Agent header，設定 10 秒 timeout。
- `fetch()` MUST 在請求完成後呼叫 `time.sleep(1)` 符合爬蟲禮儀。
- `fetch()` MUST 呼叫 `response.raise_for_status()` 確保 HTTP 錯誤被拋出。
- `NewsFetcher` 不 SHALL 包含任何 HTML/XML 解析邏輯。

#### Scenario: 成功爬取回傳原始 XML
- **WHEN** 使用關鍵字 `"人工智慧"` 呼叫 `fetch()`，且伺服器正常回應
- **THEN** 回傳非空的 XML 字串，字串包含 `<rss` 或 `<channel` 標籤

#### Scenario: 網路超時拋出例外
- **WHEN** 目標伺服器超過 10 秒未回應
- **THEN** 拋出 `requests.exceptions.Timeout`

#### Scenario: HTTP 錯誤狀態碼拋出例外
- **WHEN** 伺服器回應 403 或 5xx 狀態碼
- **THEN** 拋出 `requests.exceptions.HTTPError`

---

### Requirement: NewsParser 子系統類別
系統 SHALL 定義 `NewsParser` 類別，封裝所有 XML 解析與資料提取邏輯。

- `NewsParser` MUST 在建構時接受 `strategy: SnippetStrategy` 參數，預設為 `KeywordFirstStrategy()`。
- `NewsParser` MUST 提供 `parse(raw_xml: str, keyword: str, max_results: int) -> list[dict]` 方法。
- `parse()` MUST 使用 BeautifulSoup `lxml-xml` 解析器解析 XML。
- `parse()` MUST 對每個 `<item>` 提取：`標題`、`刊登時間`、`來源`、`關鍵句子`、`網址`。
- `parse()` MUST 將 snippet 萃取委派給 `self.strategy.extract()`，不 SHALL 包含任何 if/else 句子選取邏輯。
- `NewsParser` MUST 保留 `_is_noise()`、`_split_sentences()`、`_extract_url()`、`_extract_source()`、`_extract_pubdate()` 等輔助方法。

#### Scenario: 策略委派正確執行
- **WHEN** 以 `LengthFirstStrategy()` 建立 `NewsParser`，並呼叫 `parse()`
- **THEN** snippet 欄位依長度優先策略填入，而非關鍵字優先

#### Scenario: 解析空 XML 回傳空列表
- **WHEN** `raw_xml` 為不含 `<item>` 的最小 RSS 結構
- **THEN** `parse()` 回傳空列表 `[]`

#### Scenario: 超過 max_results 的項目被截斷
- **WHEN** XML 包含 15 個 `<item>`，`max_results = 10`
- **THEN** `parse()` 回傳恰好 10 筆記錄

---

### Requirement: ScraperFacade 外觀類別
系統 SHALL 定義 `ScraperFacade` 類別，作為外部呼叫者與爬蟲子系統之間的唯一介面。

- `ScraperFacade.__init__(keyword, max_results=10)` MUST 接受與原 `Scraper` 相同的參數簽名。
- `ScraperFacade` MUST 在 `__init__` 中建立 `NewsFetcher` 與 `NewsParser` 實例（組合關係）。
- `ScraperFacade` MUST 提供 `run() -> pd.DataFrame` 方法，執行完整的 fetch → parse → sort 流程。
- `run()` 的回傳格式（DataFrame 欄位名稱、排序方向）MUST 與原 `Scraper.run()` 完全相同。
- 外部呼叫者 MUST NOT 需要直接與 `NewsFetcher` 或 `NewsParser` 互動。

#### Scenario: app.py 透過 ScraperFacade 取得結果
- **WHEN** `app.py` 實例化 `ScraperFacade(keyword="台積電", max_results=10)` 並呼叫 `run()`
- **THEN** 回傳 DataFrame，欄位包含 `標題`、`刊登時間`、`來源`、`關鍵句子`、`網址`，依刊登時間降冪排序

#### Scenario: ScraperFacade 對外隱藏子系統
- **WHEN** 閱讀 `app.py` 的程式碼
- **THEN** 不可見任何 `NewsFetcher`、`NewsParser` 的直接實例化或方法呼叫

---

### Requirement: 向下相容別名
系統 SHALL 在 `scraper.py` 尾端保留 `Scraper = ScraperFacade` 別名，確保任何仍使用原 `Scraper` 名稱的程式碼不會因重構而中斷。

#### Scenario: 以舊名稱 Scraper 呼叫仍可運作
- **WHEN** 程式碼執行 `from scraper import Scraper; s = Scraper("test"); df = s.run()`
- **THEN** 正常回傳 DataFrame，不拋出 ImportError 或 AttributeError
