## ADDED Requirements

### Requirement: SnippetStrategy 抽象介面
系統 SHALL 定義 `SnippetStrategy` 抽象基底類別（ABC），宣告 `extract(sentences: list[str], keyword: str) -> str` 抽象方法，作為所有摘要萃取策略的共同介面。

- 所有具體策略類別 MUST 繼承 `SnippetStrategy` 並實作 `extract()`。
- `extract()` 的回傳值 MUST 為字串（含句子或空字串），長度 MUST <= 50 字（超出時截斷並加 `...`）。
- 若 `sentences` 為空列表，`extract()` MUST 回傳空字串 `""`。

#### Scenario: 介面不可直接實例化
- **WHEN** 程式碼嘗試直接實例化 `SnippetStrategy()`
- **THEN** Python 拋出 `TypeError`（因 ABC abstractmethod 約束）

#### Scenario: 子類別未實作 extract 時不可實例化
- **WHEN** 定義一個繼承 `SnippetStrategy` 但未實作 `extract()` 的類別並嘗試實例化
- **THEN** Python 拋出 `TypeError`

---

### Requirement: KeywordFirstStrategy 具體實作
系統 SHALL 提供 `KeywordFirstStrategy` 類別，實作「關鍵字優先」句子選取邏輯。

選取優先序（MUST 依序執行）：
1. 不含噪音 + 含關鍵字 + 長度 >= 20 字 → 回傳第一個符合的句子（截斷至 50 字）
2. 不含噪音 + 長度 >= 50 字 → 回傳第一個符合的句子（截斷至 50 字）
3. 不含噪音 + 長度 >= 20 字 → 回傳第一個符合的句子（截斷至 50 字）
4. 無符合句子 → 回傳 `""`

- 「噪音句子」判斷 MUST 委派給 `_NOISE_PATTERNS` 清單（繼承自 `NewsParser`）。
- `keyword` 為空字串時，MUST 跳過步驟 1，直接從步驟 2 開始。

#### Scenario: 含關鍵字句子優先回傳
- **WHEN** `sentences = ["今天天氣很好。", "人工智慧改變了世界的發展方向，深刻影響各行各業。"]`，`keyword = "人工智慧"`
- **THEN** `extract()` 回傳 `"人工智慧改變了世界的發展方向，深刻影響各行各業。"` （長度 = 21，含關鍵字）

#### Scenario: 無關鍵字時依長度選句
- **WHEN** `sentences = ["短句。", "這是一個超過五十個字的長句子，用來測試長度優先的選取邏輯是否正確運作，應該會被截斷。"]`，`keyword = ""`
- **THEN** 回傳前 50 字 + `"..."`

#### Scenario: 所有句子均為噪音時回傳空字串
- **WHEN** `sentences = ["設為首選來源", "訂閱電子報"]`，`keyword = "任意"`
- **THEN** `extract()` 回傳 `""`

---

### Requirement: LengthFirstStrategy 具體實作
系統 SHALL 提供 `LengthFirstStrategy` 類別，實作「純長度優先」句子選取邏輯（不考慮關鍵字）。

選取優先序（MUST 依序執行）：
1. 不含噪音 + 長度 >= 50 字 → 回傳第一個符合的句子（截斷至 50 字）
2. 不含噪音 + 長度 >= 20 字 → 回傳第一個符合的句子（截斷至 50 字）
3. 無符合句子 → 回傳 `""`

- 此策略 MUST 完全忽略 `keyword` 參數。

#### Scenario: 忽略關鍵字，依長度選句
- **WHEN** `sentences = ["人工智慧短句。", "這是一個超過五十個字的長句子，與關鍵字無關，但長度超過標準，應被優先選取。"]`，`keyword = "人工智慧"`
- **THEN** 回傳第二句（截斷至 50 字 + `...`），而非含關鍵字的第一句
