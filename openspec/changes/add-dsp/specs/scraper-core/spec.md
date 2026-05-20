## MODIFIED Requirements

### Requirement: Scraper 類別重構為 ScraperFacade
原 `Scraper` 類別 MUST 被重構為 `ScraperFacade`，職責分離至 `NewsFetcher`、`NewsParser`、`ScraperFacade` 三個類別。

完整更新後的行為定義：
- `ScraperFacade.__init__(keyword: str, max_results: int = 10)` MUST 建立內部的 `NewsFetcher` 與 `NewsParser(strategy=KeywordFirstStrategy())` 實例。
- `ScraperFacade.run()` MUST 執行以下步驟：
  1. 通知所有 observers：`on_fetch_start(keyword)`
  2. 呼叫 `self._fetcher.fetch(self.keyword)` 取得原始 XML
  3. 通知所有 observers：`on_fetch_done()`
  4. 呼叫 `self._parser.parse(raw_xml, self.keyword, self.max_results)` 取得結果列表
  5. 通知所有 observers：`on_parse_done(len(results))`
  6. 轉換為 DataFrame，依 `刊登時間` 降冪排序
  7. 回傳 DataFrame
- 原 `Scraper` 名稱 MUST 保留為 `ScraperFacade` 的別名（`Scraper = ScraperFacade`）。
- 原 `Scraper.fetch()`、`Scraper.parse()` 等公開方法 MUST 保留在各自的子系統類別中，但不再暴露於 `ScraperFacade`。

#### Scenario: app.py 使用 ScraperFacade 替換原 Scraper
- **WHEN** `app.py` 執行 `from scraper import ScraperFacade; facade = ScraperFacade(keyword=keyword, max_results=10); df = facade.run()`
- **THEN** 回傳與原 `Scraper.run()` 格式完全相同的 DataFrame

#### Scenario: 舊程式碼使用 Scraper 名稱仍可運作
- **WHEN** 執行 `from scraper import Scraper; s = Scraper("台積電"); df = s.run()`
- **THEN** 正常回傳 DataFrame（通過別名 `Scraper = ScraperFacade`）

#### Scenario: 原始爬取行為不變
- **WHEN** 以相同關鍵字執行重構前後的爬蟲
- **THEN** 回傳的 DataFrame 欄位名稱、排序方向、最大筆數限制與重構前完全相同
