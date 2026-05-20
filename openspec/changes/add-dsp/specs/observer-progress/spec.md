## ADDED Requirements

### Requirement: ScraperObserver 抽象介面
系統 SHALL 定義 `ScraperObserver` ABC，宣告爬取流程的三個生命週期事件方法。

宣告的抽象方法（MUST 全部實作）：
- `on_fetch_start(keyword: str) -> None`：爬取請求發出前觸發
- `on_fetch_done() -> None`：HTTP 回應接收完畢後觸發
- `on_parse_done(count: int) -> None`：XML 解析完成並取得結果筆數後觸發

- 所有具體 observer 類別 MUST 繼承 `ScraperObserver`。
- `ScraperFacade` MUST 在執行各流程步驟前後，依序通知所有已訂閱的 observers。

#### Scenario: Observer 介面不可直接實例化
- **WHEN** 程式碼嘗試直接實例化 `ScraperObserver()`
- **THEN** Python 拋出 `TypeError`

#### Scenario: 多個 Observer 均被通知
- **WHEN** `ScraperFacade` 訂閱了 2 個 observer，執行 `run()`
- **THEN** 兩個 observer 的 `on_fetch_start`、`on_fetch_done`、`on_parse_done` 各被呼叫一次

---

### Requirement: ScraperFacade 支援 Observer 訂閱
系統 SHALL 在 `ScraperFacade` 中提供 `attach(observer: ScraperObserver)` 方法，允許外部在執行前訂閱事件。

- `attach()` MUST 將 observer 加入內部 `_observers: list[ScraperObserver]` 清單。
- `ScraperFacade.run()` MUST 在 `NewsFetcher.fetch()` 呼叫前觸發 `on_fetch_start(keyword)`。
- `ScraperFacade.run()` MUST 在 `NewsFetcher.fetch()` 回傳後觸發 `on_fetch_done()`。
- `ScraperFacade.run()` MUST 在 `NewsParser.parse()` 回傳後觸發 `on_parse_done(len(results))`。
- 若任一 observer 的事件方法拋出例外，`ScraperFacade` MUST 靜默吞掉例外（`try/except Exception: pass`），不影響主流程。

#### Scenario: attach 後 observer 接收通知
- **WHEN** 建立 `facade = ScraperFacade("台積電")` 並 `facade.attach(my_observer)` 後呼叫 `run()`
- **THEN** `my_observer.on_fetch_start("台積電")`、`on_fetch_done()`、`on_parse_done(N)` 依序被呼叫

#### Scenario: Observer 拋出例外不影響爬取流程
- **WHEN** observer 的 `on_fetch_start()` 內部拋出 `RuntimeError`
- **THEN** `ScraperFacade.run()` 繼續正常執行並回傳 DataFrame

---

### Requirement: StreamlitProgressObserver 具體實作
系統 SHALL 提供 `StreamlitProgressObserver` 類別，透過 `st.session_state` 向 Streamlit UI 回報爬取進度。

- `on_fetch_start(keyword)` MUST 設定 `st.session_state["scrape_status"] = "fetching"`。
- `on_fetch_done()` MUST 設定 `st.session_state["scrape_status"] = "parsing"`。
- `on_parse_done(count)` MUST 設定 `st.session_state["scrape_status"] = "done"`，並將 `count` 存入 `st.session_state["scrape_count"]`。
- 所有方法 MUST 包裝在 `try/except Exception` 中（因 `st.session_state` 在測試環境可能不存在）。

#### Scenario: Streamlit 環境中狀態正確更新
- **WHEN** Streamlit app 執行 `facade.run()`，且已 attach `StreamlitProgressObserver`
- **THEN** `st.session_state["scrape_status"]` 最終值為 `"done"`，`st.session_state["scrape_count"]` 為實際結果筆數

#### Scenario: 非 Streamlit 環境中不拋出例外
- **WHEN** 在純 Python 環境（無 Streamlit context）中執行帶有 `StreamlitProgressObserver` 的 facade
- **THEN** `run()` 正常完成，不拋出例外
