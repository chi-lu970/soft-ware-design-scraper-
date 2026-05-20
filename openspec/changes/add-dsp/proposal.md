## Why

本專案為學術課程作業，教授要求在現有爬蟲程式碼中融入至少三種設計模式（Design Patterns），以展示物件導向設計原則的實際應用。現有 `scraper.py` 的 `Scraper` 類別承擔了「HTTP 爬取」、「XML 解析」、「文字萃取」三項職責，且各職責的替換性與可擴展性不足，是注入設計模式的最佳切入點。

## What Changes

- **新增** `Strategy Pattern（策略模式）`：將 `_extract_snippet()` 的多段式句子選取邏輯，抽取為獨立的 `SnippetStrategy` 介面與兩個實作類（`KeywordFirstStrategy`、`LengthFirstStrategy`），使摘取策略可在執行期替換。
- **新增** `Facade Pattern（外觀模式）`：將 `Scraper` 的內部子職責（HTTP 爬取、XML 解析）拆分為 `NewsFetcher` 與 `NewsParser` 兩個具體類別，並以 `ScraperFacade` 作為統一對外介面，隱藏子系統複雜度；`app.py` 只需與 `ScraperFacade` 溝通。
- **新增** `Observer Pattern（觀察者模式）`：在 `ScraperFacade` 的爬取流程中加入事件通知機制（`ScraperObserver` 介面），讓 Streamlit UI 層可訂閱進度事件，即時反映「開始爬取」→「解析中」→「完成」等狀態。
- **新增** `design_patterns_reference.md`：一份設計模式整理文件，說明所有 23 種 GoF 模式的使用時機與目的，作為後續選擇的參考依據。
- **新增** `design_patterns_usage.md`：說明本專案在哪個位置、以哪種方式應用了哪三種設計模式。
- 現有 `scraper.py` 與 `app.py` 的外部行為（輸入、輸出、UI 畫面）保持完全不變，不引入 **BREAKING** 變更。

## Capabilities

### New Capabilities

- `strategy-snippet`: 定義 `SnippetStrategy` 抽象介面及 `KeywordFirstStrategy`、`LengthFirstStrategy` 兩個具體策略類別，負責關鍵句子萃取邏輯
- `facade-scraper`: 定義 `NewsFetcher`、`NewsParser` 子系統類別及 `ScraperFacade` 外觀類別，統一對外 API
- `observer-progress`: 定義 `ScraperObserver` 介面及 `StreamlitProgressObserver` 具體實作，處理爬取進度通知
- `dp-reference-doc`: 生成 `design_patterns_reference.md` 與 `design_patterns_usage.md` 兩份說明文件

### Modified Capabilities

- `scraper-core`: `scraper.py` 的 `Scraper` 類別重構為 `ScraperFacade`，`_extract_snippet()` 改委派給 Strategy 物件；對 `app.py` 的介面保持向下相容

## Impact

- **修改檔案**：`scraper.py`（核心重構）、`app.py`（替換 `Scraper` 為 `ScraperFacade`，加入 Observer 訂閱）
- **新增檔案**：`design_patterns_reference.md`、`design_patterns_usage.md`
- **依賴變更**：無新增套件，僅使用 Python 標準 ABC（`abc` 模組）定義介面
- **測試影響**：功能行為不變，現有 Streamlit 操作流程與輸出格式不受影響
