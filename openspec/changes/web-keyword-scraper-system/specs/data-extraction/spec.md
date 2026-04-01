## ADDED Requirements

### Requirement: 標題擷取
系統 SHALL 從 RSS 每個 `<item>` 元素中擷取 `<title>` 標籤的文字內容作為標題欄位。

#### Scenario: 標題存在
- **WHEN** RSS item 包含 `<title>` 標籤
- **THEN** 系統擷取並儲存標題文字（去除前後空白）

#### Scenario: 標題不存在
- **WHEN** RSS item 缺少 `<title>` 標籤
- **THEN** 系統使用「（無標題）」作為預設值

### Requirement: 來源擷取
系統 SHALL 從 `<source>` 標籤或網址的網域名稱中擷取來源資訊。

#### Scenario: source 標籤存在
- **WHEN** RSS item 包含 `<source>` 標籤
- **THEN** 系統擷取 source 標籤的文字作為來源欄位

#### Scenario: source 標籤不存在
- **WHEN** RSS item 缺少 `<source>` 標籤
- **THEN** 系統從 `<link>` URL 解析網域名稱（例如 `news.example.com`）作為來源

### Requirement: 關鍵句子擷取（字串匹配）
系統 SHALL 在 `<description>` 欄位中搜尋關鍵字，並擷取關鍵字前後各 50 個字元作為 Snippet。此邏輯 MUST 使用純字串匹配，不得使用 AI 或 NLP 技術。

#### Scenario: 關鍵字出現在描述中
- **WHEN** `<description>` 文字包含搜尋關鍵字（不分大小寫）
- **THEN** 系統擷取關鍵字位置前後各 50 字元，格式為「...前文【關鍵字】後文...」

#### Scenario: 關鍵字未出現在描述中
- **WHEN** `<description>` 文字不包含搜尋關鍵字
- **THEN** 系統回傳 `<description>` 的前 100 個字元作為 Snippet

#### Scenario: 描述欄位不存在
- **WHEN** RSS item 缺少 `<description>` 標籤
- **THEN** 系統回傳空字串作為 Snippet

### Requirement: 原網址擷取
系統 SHALL 從 `<link>` 標籤擷取原始文章 URL。

#### Scenario: link 存在
- **WHEN** RSS item 包含 `<link>` 標籤
- **THEN** 系統擷取完整 URL 字串

#### Scenario: link 不存在
- **WHEN** RSS item 缺少 `<link>` 標籤
- **THEN** 系統使用空字串作為 URL 值
