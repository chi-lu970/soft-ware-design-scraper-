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
系統 SHALL 從 Bing News RSS 的 `<News:Source>` 標籤擷取來源媒體名稱。

#### Scenario: News:Source 標籤存在
- **WHEN** RSS item 包含 `<News:Source>` 標籤且有文字內容
- **THEN** 系統擷取其文字作為來源欄位

#### Scenario: News:Source 標籤不存在
- **WHEN** RSS item 缺少 `<News:Source>` 標籤
- **THEN** 系統回傳「（未知來源）」作為預設值

### Requirement: 關鍵句子擷取（句子級過濾 + 優先序選取）
系統 SHALL 從 `<description>` 欄位中以句子為單位過濾廣告噪音，並依優先序選取最相關的乾淨句子作為 Snippet。此邏輯 MUST 使用規則式字串匹配，不得使用 AI 或 NLP 技術。

**擷取流程**:
1. 從 `<description>` 取得純文字（去除 HTML 標籤）
2. 依 `。！？` 與換行符切成句子列表
3. 對每個句子執行噪音判斷：句子中含任一黑名單樣板詞 → 整句跳過
4. 在乾淨句子中依優先序選取

**噪音黑名單（整句跳過條件）**:
- `設為首選來源`
- `查看更多我們的精彩報導`
- `在 Google 上查看`
- `在 Yahoo 上查看`
- `致力為全球華文受眾`
- `提供獨立、可信、中立`
- `擁有國際視角、深度、廣度和維度`
- `訂閱電子報`
- `加入會員`

**選取優先序**（在乾淨句子上執行）:

| 優先 | 條件 | 說明 |
|---|---|---|
| 1 | 含關鍵字 + >= 20 字 | 最相關且乾淨的句子 |
| 2 | >= 50 字 | 夠長代表有實質內容 |
| 3 | >= 20 字 | 放寬長度限制，取第一個有意義片段 |
| 4 | 無乾淨句子 | 回傳空字串，不顯示廣告 |

**輸出格式**: 句子 <= 50 字時完整保留（含句末標點）；> 50 字時截斷前 50 字並加上「...」

#### Scenario: 存在含關鍵字的乾淨句子
- **WHEN** description 中有不含噪音、長度 >= 20 字、且包含搜尋關鍵字的句子
- **THEN** 系統回傳第一個符合條件的句子（最多 50 字）

#### Scenario: 無含關鍵字句子但有乾淨長句
- **WHEN** description 中無含關鍵字的乾淨句子，但有不含噪音且長度 >= 50 字的句子
- **THEN** 系統回傳第一個符合條件的句子（截斷至 50 字 + "..."）

#### Scenario: 僅有短的乾淨句子
- **WHEN** description 中的乾淨句子長度皆 < 50 字，但有長度 >= 20 字者
- **THEN** 系統回傳第一個 >= 20 字的乾淨句子

#### Scenario: 所有句子皆含噪音
- **WHEN** description 中所有句子均命中噪音黑名單
- **THEN** 系統回傳空字串，不強制顯示廣告內容

#### Scenario: 描述欄位不存在
- **WHEN** RSS item 缺少 `<description>` 標籤
- **THEN** 系統回傳空字串作為 Snippet

### Requirement: 原網址擷取
系統 SHALL 從 Bing News RSS 的 `<link>` 標籤解析真實文章 URL。

#### Scenario: link 為 Bing redirect URL
- **WHEN** RSS item 的 `<link>` 含 `url=` 查詢參數
- **THEN** 系統解析 `url` 參數值，回傳原始文章網址

#### Scenario: link 不含 url 參數或標籤不存在
- **WHEN** RSS item 缺少 `<link>` 或 link 不含 `url=` 參數
- **THEN** 系統回傳 link 原始值或空字串
