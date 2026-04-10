## Context

本系統為全新開發的教學用 Web 爬蟲專案，無既有程式碼需遷移。主要限制為：
- 不使用非同步技術（asyncio/aiohttp），維持程式碼易讀性
- 不使用深度學習或 AI 摘要，關鍵句子提取採規則式字串邏輯
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

### 2. 爬取目標：Bing News RSS Feed（而非 Google News）
**選擇**: `https://www.bing.com/news/search?q=<keyword>&format=RSS`
**理由**: Bing News RSS 的 `<description>` 欄位包含真正的文章摘要文字，適合關鍵句子擷取。Google News RSS 的 description 欄位僅含 HTML 圖片標籤，無法提取有意義的摘要。

**Bing News RSS 格式說明**:
```xml
<item>
  <title>文章標題</title>
  <link>https://www.bing.com/news/apiclick.aspx?...&url=https://原始文章網址...</link>
  <description>文章摘要文字（可能混有平台推廣語）</description>
  <pubDate>發布時間</pubDate>
  <News:Source>來源媒體名稱</News:Source>
</item>
```

**Bing 搜尋行為（語意匹配）**:
Bing News 搜尋並非單純的關鍵字完全比對，而是混合以下機制：
- **倒排索引 + TF-IDF**：傳統關鍵字匹配，速度快、找候選集
- **語意模型（BERT 類）**：理解查詢語意，將「人工智慧」與「AI」視為等義
- **知識圖譜**：預建概念關聯，例如「人工智慧」→「機器學習」、「深度學習」
- **新聞熱度加權**：發布時間、來源可信度、社群媒體熱度

因此搜尋「人工智慧」可能出現標題含「AI」或「智慧城市」的結果，屬正常行為。若需嚴格比對，需在程式端加額外過濾。

### 3. 檔案結構：雙檔分離
```
project/
├── app.py          # View + Controller（Streamlit UI 與流程控制）
├── scraper.py      # Model（Scraper 類別，爬取與解析邏輯）
└── requirements.txt
```
**理由**: 最小化檔案數量，同時維持 MVC 分離原則。可直接對應 Class Diagram 中的兩個主要類別。

### 4. 關鍵句子擷取：句子級過濾 + 優先序選取

**選擇**: 切句 → 整句噪音判斷 → 依優先序選取
**理由**: RSS description 欄位常混有平台推廣語或媒體自介樣板（如「將 Yahoo 設為首選來源」、「BBC News 中文 致力為全球華文受眾」），純截字無法有效過濾。以句子為單位判斷，比詞語刪除更乾淨。

**擷取流程**:
```
RSS description 原文
    ↓
切句（依 。！？ 與換行符）
    ↓
噪音過濾（句子含黑名單詞 → 整句跳過）
    ↓
優先序選取：
  1. 含關鍵字 + 不是噪音 + >= 20 字
  2. 不是噪音 + >= 50 字
  3. 不是噪音 + >= 20 字
  4. 找不到乾淨句子 → 回傳空字串
    ↓
輸出：完整句子（<= 50 字）或截斷前 50 字 + "..."
```

**噪音黑名單（_NOISE_PATTERNS）**:
句子中命中任一樣板詞，整句視為垃圾並跳過：
- Yahoo/Google 推廣語：`設為首選來源`、`查看更多我們的精彩報導`、`在 Google 上查看`
- 媒體自介樣板：`致力為全球華文受眾`、`提供獨立、可信、中立`
- 其他：`訂閱電子報`、`加入會員`

### 5. URL 顯示：`st.column_config.LinkColumn`（實作版本修正）
**選擇**: 使用 `st.column_config.LinkColumn`，設定 `display_text="開啟連結"`
**理由**: Streamlit 1.32+ 提供原生 `LinkColumn`，比 `unsafe_allow_html` 更安全且無 XSS 風險，同時維持可點擊連結體驗。原規格採用 `st.markdown` + `unsafe_allow_html`，實作時改為 LinkColumn 以符合安全最佳實踐。

### 6. Bing URL 解析：從重導向連結提取原始網址
**選擇**: 解析 Bing redirect URL 中的 `url=` 查詢參數
**理由**: Bing News RSS 的 `<link>` 欄位為 Bing 自身的重導向連結（`apiclick.aspx?...&url=原始網址`），需解析 `url` 參數才能取得真正的文章網址。使用 `urllib.parse.urlparse` + `parse_qs` 標準庫實作，無需額外依賴。

### 7. 刊登時間欄位與排序（實作版本新增）
**選擇**: 新增「刊登時間」欄位（YYYY/MM/DD HH:MM），並依此欄位降序排列
**理由**: RSS `<pubDate>` 欄位提供了 RFC 2822 格式的發布時間。加入此欄位讓使用者可判斷資訊新鮮度；依時間排序確保最新消息優先顯示，符合新聞查詢的使用習慣。使用標準庫 `email.utils.parsedate_to_datetime` 解析，不增加外部依賴。

### 8. Session State 結果保留（實作版本新增）
**選擇**: 將搜尋結果（DataFrame）與關鍵字存入 `st.session_state`
**理由**: Streamlit 每次互動均會重新執行整個 `app.py`。若不使用 session_state，使用者點擊輸入框後畫面即清空，體驗極差。透過 `st.session_state.result_df` 與 `st.session_state.result_keyword` 保留上一次搜尋結果，使結果顯示不依賴「搜尋按鈕是否剛被點擊」。

## Risks / Trade-offs

| 風險 | 緩解措施 |
|---|---|
| Bing News RSS 結構未來可能改變 | 在 `Scraper` 類別中集中解析邏輯，改版時只需修改一處 |
| 網路請求超時或被封鎖 | 設定 `timeout=10`，加入 try/except，回傳友善錯誤訊息 |
| `time.sleep()` 導致 UI 卡頓 | 爬取時顯示 `st.spinner`，告知使用者正在載入 |
| 無結果時 DataFrame 為空 | 明確檢查空結果並顯示提示訊息，而非顯示空表格 |
| Bing 語意匹配導致部分結果與關鍵字不直接相關 | 說明此為 Bing 搜尋引擎行為，非程式錯誤；可在程式端加標題過濾 |
| RSS description 混有廣告樣板語 | 黑名單句子級過濾，命中噪音詞整句跳過，找下一句 |
| 所有句子皆為噪音時關鍵句子欄位為空 | 回傳空字串，讓使用者知道該篇無有效摘要，優於顯示廣告 |

## Migration Plan

本系統為全新建置，無需遷移。部署步驟：
1. `pip install -r requirements.txt`
2. `streamlit run app.py`

## Open Questions

- 目標爬取筆數上限：預設 10 筆（可在 `Scraper` 類別中設定 `max_results` 參數）
- 是否需要支援多語系關鍵字：現階段支援中英文
- 是否需要在程式端加標題關鍵字過濾以排除 Bing 語意匹配的不相關結果：待確認
