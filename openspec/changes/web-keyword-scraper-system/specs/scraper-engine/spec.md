## ADDED Requirements

### Requirement: Scraper 類別定義
系統 SHALL 定義一個 `Scraper` 類別，封裝所有爬取與解析邏輯，不得將爬取邏輯散落於 UI 層。

#### Scenario: 類別實例化
- **WHEN** 以關鍵字字串初始化 `Scraper` 物件（例如 `Scraper("Python")`）
- **THEN** 物件儲存關鍵字並準備執行爬取，不立即發出 HTTP 請求

### Requirement: HTTP 請求執行
系統 SHALL 使用 `requests` 函式庫對 Google News RSS Feed 發出 GET 請求。

#### Scenario: 成功發出請求
- **WHEN** 呼叫 `scraper.fetch()` 方法
- **THEN** 系統向 `https://news.google.com/rss/search?q=<keyword>&hl=zh-TW` 發出 GET 請求，並設定 timeout=10 秒

#### Scenario: 請求超時
- **WHEN** HTTP 請求超過 10 秒未收到回應
- **THEN** 系統拋出包含友善訊息的例外，由錯誤處理層捕獲

### Requirement: 爬蟲禮儀延遲
系統 SHALL 在每次 HTTP 請求後執行 `time.sleep(1)`，避免對目標伺服器造成負擔。

#### Scenario: 請求完成後延遲
- **WHEN** HTTP 請求成功收到回應
- **THEN** 系統等待至少 1 秒後才繼續處理

### Requirement: 最大結果數量限制
系統 SHALL 預設最多回傳 10 筆結果，可透過 `max_results` 參數調整。

#### Scenario: 爬取結果超過上限
- **WHEN** RSS Feed 回傳超過 10 筆項目
- **THEN** 系統只處理前 10 筆，忽略其餘項目

#### Scenario: 爬取結果少於上限
- **WHEN** RSS Feed 回傳不足 10 筆項目
- **THEN** 系統處理所有回傳項目
