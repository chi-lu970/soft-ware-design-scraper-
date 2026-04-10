## 1. 專案環境設置

- [x] 1.1 建立 `requirements.txt`，列出所有依賴套件
- [x] 1.2 建立專案根目錄結構（`app.py`、`scraper.py`）

## 2. Scraper 類別實作（Model 層）

- [x] 2.1 定義 `Scraper` 類別，建構子接受 `keyword` 與 `max_results` 參數
- [x] 2.2 實作 `fetch()` 方法：向 Google News RSS 發出 GET 請求，設定 timeout=10，加入 time.sleep(1)
- [x] 2.3 實作 `_extract_snippet()` 私有方法：字串匹配關鍵字，擷取前後 50 字元
- [x] 2.4 實作 `parse()` 方法：用 BeautifulSoup 解析 XML，提取 title、source、snippet、url
- [x] 2.5 實作 `run()` 方法：整合 fetch() 與 parse()，回傳 Pandas DataFrame
- [x] 2.6 加入完整的例外處理（ConnectionError、Timeout、HTTPError）

## 3. Streamlit 前端實作（View/Controller 層）

- [x] 3.1 建立 `app.py`，設定頁面標題與說明文字
- [x] 3.2 實作關鍵字輸入框與搜尋按鈕
- [x] 3.3 加入空白關鍵字驗證，顯示友善提示訊息
- [x] 3.4 整合 Scraper 類別，以 `st.spinner` 顯示載入狀態
- [x] 3.5 實作結果顯示：顯示結果數量，並將 URL 欄位渲染為可點擊 HTML 連結
- [x] 3.6 加入錯誤訊息顯示區塊（`st.error`）

## 4. 驗證與完善

- [x] 4.1 確認程式碼含繁體中文詳細註解
- [x] 4.2 確認 UI 邏輯（app.py）與爬蟲邏輯（scraper.py）完全分離
- [ ] 4.3 測試正常搜尋流程（輸入關鍵字 → 顯示結果）
- [ ] 4.4 測試錯誤情境（空關鍵字、網路失敗）
