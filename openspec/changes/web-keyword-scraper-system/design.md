## Context

本系統為全新開發的教學用 Web 爬蟲專案，無既有程式碼需遷移。主要限制為：
- 不使用非同步技術（asyncio/aiohttp），維持程式碼易讀性
- 不使用深度學習或 AI 摘要，關鍵句子提取採純字串匹配
- 需能產出 Class Diagram 與 Sequence Diagram，故強制 OOP 設計

**利害關係人**: 軟體設計課程學生、教師（教學報告審閱者）

## Goals / Non-Goals

**Goals:**
- 實作 MVC 三層架構，View/Controller 與 Model 明確分離
- `Scraper` 類別封裝所有爬取與解析邏輯，可直接對應 Class Diagram
- Streamlit 前端提供即時互動體驗（輸入 → 爬取 → 顯示）
- 程式碼含繁體中文詳細註解，供教學報告引用

**Non-Goals:**
- 不實作使用者登入/權限管理
- 不實作資料持久化（不儲存至資料庫）
- 不實作非同步爬取或多執行緒
- 不實作 AI 語意摘要或 NLP 處理
- 不支援動態 JavaScript 渲染頁面（不使用 Selenium）

## Decisions

### 1. 前端框架：Streamlit（而非 Flask/FastAPI）
**選擇**: Streamlit
**理由**: 無需手寫 HTML/CSS，單一 Python 檔案即可完成 UI，適合教學情境。Flask/FastAPI 需額外的前端模板，增加不必要複雜度。

### 2. 爬取目標：Google News RSS Feed
**選擇**: `https://news.google.com/rss/search?q=<keyword>&hl=zh-TW`
**理由**: RSS XML 結構穩定、不依賴 JavaScript 渲染、無需登入、格式標準化，適合 BeautifulSoup 解析。相比直接爬取一般新聞網站，RSS 更不易因網站改版而失效。

### 3. 檔案結構：雙檔分離
```
project/
├── app.py          # View + Controller（Streamlit UI 與流程控制）
├── scraper.py      # Model（Scraper 類別，爬取與解析邏輯）
└── requirements.txt
```
**理由**: 最小化檔案數量，同時維持 MVC 分離原則。可直接對應 Class Diagram 中的兩個主要類別。

### 4. 關鍵句子擷取：字串匹配（±50 字）
**選擇**: 在 `description` 欄位中搜尋關鍵字，擷取前後 50 個字元
**理由**: 符合需求文件「非 AI 邏輯，單純字串匹配」的明確要求。

### 5. URL 顯示：HTML `<a>` 標籤 via `st.markdown`
**選擇**: 使用 `st.markdown` 搭配 unsafe_allow_html 渲染可點擊連結
**理由**: Streamlit 原生 DataFrame 不支援 HTML 連結，此為官方建議的替代方案。

## Risks / Trade-offs

| 風險 | 緩解措施 |
|---|---|
| Google News RSS 結構未來可能改變 | 在 `Scraper` 類別中集中解析邏輯，改版時只需修改一處 |
| 網路請求超時或被封鎖 | 設定 `timeout=10`，加入 try/except，回傳友善錯誤訊息 |
| `time.sleep()` 導致 UI 卡頓 | 爬取時顯示 `st.spinner`，告知使用者正在載入 |
| 無結果時 DataFrame 為空 | 明確檢查空結果並顯示提示訊息，而非顯示空表格 |

## Migration Plan

本系統為全新建置，無需遷移。部署步驟：
1. `pip install -r requirements.txt`
2. `streamlit run app.py`

## Open Questions

- 目標爬取筆數上限：預設 10 筆（可在 `Scraper` 類別中設定 `max_results` 參數）
- 是否需要支援多語系關鍵字：現階段支援中英文（RSS hl=zh-TW）
