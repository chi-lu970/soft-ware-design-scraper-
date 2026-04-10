## ADDED Requirements

### Requirement: 關鍵字輸入框
系統 SHALL 提供一個文字輸入框，允許使用者輸入任意關鍵字（中文或英文）。

#### Scenario: 使用者輸入關鍵字
- **WHEN** 使用者在輸入框中輸入任意文字
- **THEN** 系統保留該輸入值並等待使用者觸發搜尋

#### Scenario: 輸入框為空時按下搜尋
- **WHEN** 使用者未輸入任何文字即點擊搜尋按鈕（含純空白字元）
- **THEN** 系統顯示警告訊息「⚠️ 請輸入關鍵字後再搜尋。」，不啟動爬蟲

### Requirement: 搜尋按鈕
系統 SHALL 提供一個搜尋按鈕，點擊後觸發爬蟲流程。

#### Scenario: 點擊搜尋按鈕
- **WHEN** 使用者輸入關鍵字後點擊搜尋按鈕
- **THEN** 系統顯示載入指示器（spinner）並啟動爬蟲引擎

### Requirement: 載入狀態指示
系統 SHALL 在爬蟲執行期間顯示載入指示器，告知使用者正在處理中。

#### Scenario: 爬蟲執行中
- **WHEN** 爬蟲引擎正在執行 HTTP 請求與解析
- **THEN** 系統顯示 spinner 並標示「正在爬取「{keyword}」的相關新聞，請稍候...」（動態帶入關鍵字）

#### Scenario: 爬蟲完成
- **WHEN** 爬蟲引擎回傳結果
- **THEN** 系統隱藏 spinner 並顯示結果表格

### Requirement: 搜尋結果跨重新渲染保留（session_state）
系統 SHALL 將搜尋結果與對應關鍵字存入 `st.session_state`，確保使用者與輸入框互動時不會清空已顯示的結果。

#### Scenario: 輸入框內容改變後畫面不清空
- **WHEN** 使用者點擊輸入框或對輸入框進行操作，觸發 Streamlit 重新渲染
- **THEN** 系統從 `st.session_state.result_df` 讀取並重新顯示先前的搜尋結果，不重新執行爬蟲

#### Scenario: 首次載入頁面
- **WHEN** 使用者首次開啟頁面，`session_state` 中尚無結果
- **THEN** 系統不顯示結果區塊，僅顯示搜尋介面
