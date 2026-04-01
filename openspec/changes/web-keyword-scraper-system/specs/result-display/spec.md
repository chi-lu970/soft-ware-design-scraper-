## ADDED Requirements

### Requirement: 結果以表格呈現
系統 SHALL 將爬取結果以 Pandas DataFrame 為基礎的表格顯示，包含欄位：標題、來源、關鍵句子、網址。

#### Scenario: 有結果時顯示表格
- **WHEN** 爬蟲成功回傳至少一筆結果
- **THEN** 系統顯示含有「標題」「來源」「關鍵句子」「網址」四欄的表格

#### Scenario: 無結果時不顯示空表格
- **WHEN** 爬蟲回傳空列表
- **THEN** 系統顯示提示訊息「未找到相關結果，請嘗試其他關鍵字」，不顯示空表格

### Requirement: URL 為可點擊連結
系統 SHALL 將網址欄位渲染為 HTML 超連結，點擊後在新分頁開啟。

#### Scenario: 點擊網址連結
- **WHEN** 使用者點擊表格中的網址欄位連結
- **THEN** 瀏覽器在新分頁（`target="_blank"`）開啟該網址

#### Scenario: URL 為空時
- **WHEN** 某筆資料的 URL 為空字串
- **THEN** 系統顯示「（無連結）」文字，不渲染超連結

### Requirement: 結果數量標示
系統 SHALL 在表格上方顯示找到的結果總數。

#### Scenario: 顯示結果數量
- **WHEN** 表格顯示時
- **THEN** 系統在表格上方顯示「共找到 N 筆結果」
