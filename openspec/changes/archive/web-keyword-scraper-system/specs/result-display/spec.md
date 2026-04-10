## ADDED Requirements

### Requirement: 結果以表格呈現
系統 SHALL 將爬取結果以 Pandas DataFrame 為基礎的表格顯示，包含欄位：**標題、刊登時間、來源、關鍵句子、網址**（共五欄）。

> ⚠️ 實作版本新增「刊登時間」欄位，與原規格（四欄）不同，以實作為準。

#### Scenario: 有結果時顯示表格
- **WHEN** 爬蟲成功回傳至少一筆結果
- **THEN** 系統顯示含有「標題」「刊登時間」「來源」「關鍵句子」「網址」五欄的表格，並在上方顯示成功訊息

#### Scenario: 無結果時不顯示空表格
- **WHEN** 爬蟲回傳空 DataFrame
- **THEN** 系統顯示提示訊息「⚠️ 未找到「{keyword}」的相關結果，請嘗試其他關鍵字。」，不顯示空表格

### Requirement: 各欄位寬度固定
系統 SHALL 透過 `st.column_config` 為每個欄位設定固定顯示寬度，以確保視覺一致性。

| 欄位 | 類型 | 顯示寬度 |
|---|---|---|
| 標題 | TextColumn | 260px |
| 刊登時間 | TextColumn | 60px |
| 來源 | TextColumn | 60px |
| 關鍵句子 | TextColumn | 600px |
| 網址 | LinkColumn | 60px |

### Requirement: URL 為可點擊連結
系統 SHALL 使用 `st.column_config.LinkColumn` 將網址欄位渲染為可點擊的超連結，顯示文字為「開啟連結」。

#### Scenario: 點擊網址連結
- **WHEN** 使用者點擊表格中的網址欄位
- **THEN** 瀏覽器開啟對應的原始文章網址

### Requirement: 結果數量標示
系統 SHALL 在表格上方顯示找到的結果總數與搜尋關鍵字。

#### Scenario: 顯示結果數量
- **WHEN** 表格顯示時
- **THEN** 系統在表格上方以綠色成功訊息顯示「共找到 **N** 筆結果（關鍵字：{keyword}）」

### Requirement: 依刊登時間排序
系統 SHALL 將結果依「刊登時間」由新到舊排序，時間為空的項目排在最後。

#### Scenario: 結果排序
- **WHEN** 爬蟲回傳多筆結果且含有刊登時間資料
- **THEN** 系統以刊登時間降序排列，確保最新消息顯示在最前面
