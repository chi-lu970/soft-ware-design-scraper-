## ADDED Requirements

### Requirement: 網路連線失敗處理
系統 SHALL 在 HTTP 請求失敗時顯示友善的錯誤訊息，不得讓原始例外訊息直接暴露給使用者。

#### Scenario: 網路無法連線
- **WHEN** `requests` 拋出 `ConnectionError`
- **THEN** 系統顯示錯誤訊息「網路連線失敗，請確認您的網路設定後再試」

#### Scenario: 請求超時
- **WHEN** `requests` 拋出 `Timeout`
- **THEN** 系統顯示錯誤訊息「請求逾時（超過 10 秒），請稍後再試」

### Requirement: HTTP 錯誤狀態碼處理
系統 SHALL 在收到非 200 HTTP 狀態碼時顯示對應錯誤訊息。

#### Scenario: 收到 4xx/5xx 狀態碼
- **WHEN** 伺服器回傳 HTTP 狀態碼 >= 400
- **THEN** 系統顯示「伺服器回應錯誤（狀態碼：{code}），請稍後再試」

### Requirement: 解析失敗處理
系統 SHALL 在 HTML/XML 解析發生非預期錯誤時顯示友善訊息。

#### Scenario: 解析過程拋出例外
- **WHEN** BeautifulSoup 解析過程中拋出任何例外
- **THEN** 系統顯示「資料解析失敗，目標網站格式可能已變更」

### Requirement: 空關鍵字驗證
系統 SHALL 在使用者未輸入關鍵字時阻止爬蟲執行。

#### Scenario: 空字串輸入
- **WHEN** 使用者點擊搜尋但輸入框為空或僅含空白字元
- **THEN** 系統顯示「請輸入關鍵字」，不執行任何 HTTP 請求
