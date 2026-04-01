## Why

本專案需要開發一個結構清晰、模組化的 Web 關鍵字爬蟲整合系統，讓使用者能輸入關鍵字後即時從目標網站爬取相關資訊，並以視覺化表格呈現結果。此系統以教學報告及 UML 圖表產出為核心目標，故強調架構整潔性與資料流清晰度。

## What Changes

- 新增關鍵字搜尋介面（輸入框 + 搜尋按鈕）
- 新增爬蟲引擎核心模組（`Scraper` 類別，支援 OOP 設計）
- 新增資料解析邏輯，提取標題、來源、關鍵句子（前後 50 字）、原網址
- 新增結果展示頁面，以可互動的 Data Table 呈現，URL 為可點擊連結（另開新分頁）
- 採用 MVC / 三層架構：Streamlit（View）、Controller 層、Scraper Engine（Model）
- 加入錯誤處理機制（網路失敗、找不到關鍵字時顯示友善訊息）
- 加入爬蟲禮儀控制（`time.sleep()` 防止對目標伺服器造成負擔）

## Capabilities

### New Capabilities

- `keyword-search-ui`: 使用者輸入關鍵字並觸發爬蟲的 Streamlit 前端介面
- `scraper-engine`: 核心爬蟲類別，負責 HTTP 請求（Requests）與 HTML 解析（BeautifulSoup4）
- `data-extraction`: 從爬取結果中提取標題、來源、關鍵句子（字串匹配前後 50 字）、原網址
- `result-display`: 以 Pandas DataFrame 為基礎的互動式表格，URL 欄位為可點擊連結
- `error-handling`: 網路失敗或無結果時的友善錯誤訊息處理機制

### Modified Capabilities

（無，本系統為全新開發，無既有規格需修改）

## Impact

- **語言 / 框架**: Python 3.x、Streamlit、Requests、BeautifulSoup4、Pandas
- **架構**: MVC 三層分離（`app.py` 為 View/Controller，`scraper.py` 為 Model）
- **依賴套件**: `streamlit`, `requests`, `beautifulsoup4`, `pandas`
- **程式碼結構**: UI 邏輯與爬蟲邏輯分開存放，所有模組需含詳細中文註解
- **教學用途**: 程式碼結構需易於產出 Class Diagram 與 Sequence Diagram（UML）
