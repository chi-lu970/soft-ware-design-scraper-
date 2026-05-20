## Context

本專案為 Python/Streamlit 新聞爬蟲，現有兩個核心檔案：
- `scraper.py`：`Scraper` 類別，單一類別承擔 HTTP 爬取、XML 解析、文字清洗、摘要萃取四項職責。
- `app.py`：Streamlit UI，直接實例化 `Scraper` 並呼叫 `run()`。

現有問題：
1. `_extract_snippet()` 將「含關鍵字優先」、「長度 >= 50 優先」、「長度 >= 20 fallback」三種策略硬寫在同一個方法裡，無法在不改程式的情況下替換策略。
2. `Scraper` 混合了低階 HTTP 邏輯與高階 orchestration 邏輯，外部呼叫者必須了解內部步驟（`fetch()` → `parse()` → `run()`）。
3. Streamlit 的進度顯示（`st.spinner`）完全由 UI 層控制，爬蟲層無法主動通知進度。

課程要求：連續使用三種 GoF 設計模式並說明其位置與理由。

---

## Goals / Non-Goals

**Goals:**
- 在現有程式碼中正確、清晰地套用三種設計模式（Strategy、Facade、Observer）
- 保持對外行為不變：UI 仍顯示相同欄位與操作流程
- 生成兩份說明文件（設計模式參考整理、本專案使用說明）
- 每個模式的套用位置、意圖、效益須清楚可辨識，方便教授評分

**Non-Goals:**
- 不新增爬取來源（不支援 Google News、Reuters 等）
- 不改動 Streamlit 頁面佈局或欄位定義
- 不引入新的 Python 第三方套件
- 不處理多執行緒或非同步爬取

---

## Decisions

### Decision 1：Strategy Pattern 套用於摘要萃取

**選擇**：定義 `SnippetStrategy` ABC（抽象基底類別），提供兩個具體實作：
- `KeywordFirstStrategy`：優先回傳含關鍵字的句子（現有預設行為）
- `LengthFirstStrategy`：純依長度選句，不考慮關鍵字

`NewsParser`（原 `Scraper` 的解析職責）接受一個 `strategy: SnippetStrategy` 參數，`_extract_snippet()` 改為委派給策略物件的 `extract()` 方法。

**為什麼不直接用 if/else flag？**
Strategy 模式讓新策略只需新增類別，不需修改 `NewsParser`（符合開放封閉原則 OCP）。教授可明確看到多型替換（polymorphic substitution）的使用。

**替代方案考慮**：`functools.partial` 或 lambda 也能注入行為，但無法形成明確的介面契約，學術示範效果較差。

---

### Decision 2：Facade Pattern 套用於爬蟲入口

**選擇**：將 `Scraper` 拆分為：
- `NewsFetcher`：封裝 HTTP GET、headers、timeout、retry 等低階細節；提供 `fetch(keyword) -> str` 方法回傳原始 XML
- `NewsParser`：封裝 BeautifulSoup 解析、欄位提取、snippet 策略委派；提供 `parse(raw_xml, keyword) -> list[dict]`
- `ScraperFacade`：組合 `NewsFetcher` + `NewsParser` + 排序邏輯，提供與原 `Scraper` 相同的 `run() -> DataFrame` 介面

`app.py` 改用 `ScraperFacade`，只需一行 `facade.run()` 即可完成全流程，不需知道內部有幾個子系統。

**為什麼選 Facade 而非 Service Locator？**
Facade 語意最清晰，且在 GoF 書中有明確定義，適合學術報告引用。

---

### Decision 3：Observer Pattern 套用於爬取進度

**選擇**：定義 `ScraperObserver` ABC，包含三個事件方法：
- `on_fetch_start(keyword: str)`
- `on_fetch_done()`
- `on_parse_done(count: int)`

`ScraperFacade` 持有一個 `observers: list[ScraperObserver]`，在 `run()` 的各階段呼叫對應事件。

具體實作 `StreamlitProgressObserver`：
- `on_fetch_start`：設定 `st.session_state.scrape_status = "fetching"`
- `on_fetch_done`：設定 `st.session_state.scrape_status = "parsing"`
- `on_parse_done`：設定 `st.session_state.scrape_status = "done"`

`app.py` 在建立 `ScraperFacade` 時注入 observer，移除原有的 `st.spinner` 硬碼邏輯（改由 observer 驅動）。

**替代方案**：Python 內建 `logging` 模組也能達成類似效果，但 Observer 模式展示了發布-訂閱解耦的設計意圖，學術價值更高。

---

### Decision 4：檔案組織方式

所有新類別集中在 `scraper.py` 同一檔案（尾端追加），不拆多個模組。原因：
- 課程作業規模小，多檔案拆分反而增加閱讀摩擦
- 教授更容易在單一檔案中看到全部設計模式的位置
- `app.py` 的 import 路徑不需修改

---

## Risks / Trade-offs

| 風險 | 緩解措施 |
|------|---------|
| 重構破壞現有爬取行為 | 保留 `Scraper` 原始類別作為 alias（`Scraper = ScraperFacade`），確保向下相容 |
| Observer 在 Streamlit 的 session_state 外呼叫導致錯誤 | `StreamlitProgressObserver` 的所有方法加上 `try/except`，靜默失敗 |
| `ScraperFacade` 的介面與原 `Scraper` 不完全一致 | 確保 `run(keyword, max_results)` 簽名與原版相同 |
| ABC 的 `@abstractmethod` 在 Python 3.8 以下不支援 `|` 型別語法 | 使用 `Optional[str]` 替代 `str | None`（專案已用 `str | None`，確認 Python 版本 >= 3.10） |

---

## Migration Plan

1. 在 `scraper.py` 尾端追加新類別（`SnippetStrategy`、`NewsFetcher`、`NewsParser`、`ScraperFacade`）
2. 在 `app.py` 將 `from scraper import Scraper` 改為 `from scraper import ScraperFacade`，並替換實例化程式碼
3. 原 `Scraper` 類別保留不刪除（加上 `# deprecated: use ScraperFacade` 注解），確保向下相容
4. 新增 `design_patterns_reference.md` 與 `design_patterns_usage.md` 於專案根目錄
5. 手動執行 `streamlit run app.py` 驗證搜尋功能正常

**Rollback**：`app.py` 的修改只有兩行（import + 實例化），git revert 即可回到原版。

---

## Open Questions

- 無。所有技術決策已確定，依規格執行即可。
