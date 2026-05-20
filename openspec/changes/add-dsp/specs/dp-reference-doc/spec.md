## ADDED Requirements

### Requirement: Design Pattern 參考整理文件
系統 SHALL 在專案根目錄生成 `design_patterns_reference.md`，包含 GoF 23 種設計模式的整理說明。

文件 MUST 涵蓋以下資訊（每個 pattern 一個章節）：
- **模式名稱**（中英文對照）
- **分類**（創建型 / 結構型 / 行為型）
- **一句話定義**：用一句話說明這個模式「解決什麼問題」
- **使用時機**：列出 2-3 個適合使用的具體情境
- **核心概念**：說明關鍵角色（如 Context、Strategy、ConcreteStrategy）

文件 MUST 涵蓋的 23 種模式（依原始需求列表）：
1. Flyweight（享元）
2. Simple Factory（簡單工廠）
3. State（狀態）
4. Facade（外觀）
5. Observer（觀察者）
6. Composite（合成）
7. Prototype（原型）
8. Abstract Factory（抽象工廠）
9. Builder（建造者）
10. Factory Method（工廠方法）
11. Decorator（裝飾者）
12. Memento（備忘錄）
13. Adapter（轉接器）
14. Singleton（單例）
15. Strategy（策略）
16. Command（命令）
17. Template Method（樣版方法）
18. Proxy（代理）
19. Chain of Responsibility（責任鏈）
20. Iterator（走訪器）
21. Interpreter（解譯器）
22. Mediator（中介者）
23. Bridge（橋梁）

#### Scenario: 文件包含全部 23 種模式
- **WHEN** 開啟 `design_patterns_reference.md`
- **THEN** 文件中包含全部 23 種模式的章節標題，每個章節均有「使用時機」說明

#### Scenario: 分類結構清晰
- **WHEN** 閱讀文件
- **THEN** 所有模式依「創建型」、「結構型」、「行為型」三大分類分組呈現

---

### Requirement: Design Pattern 使用說明文件
系統 SHALL 在專案根目錄生成 `design_patterns_usage.md`，說明本專案中三個 Design Pattern 的實際使用位置與理由。

文件 MUST 包含以下區塊（每個 pattern 一個區塊）：
- **Pattern 名稱與分類**
- **套用位置**：指明具體的檔案名稱、類別名稱、方法名稱
- **套用前的程式碼結構（問題）**：說明套用前存在什麼設計問題
- **套用後的程式碼結構（解法）**：說明新結構如何解決問題
- **效益說明**：說明這個模式帶來的具體好處（可擴展性、可測試性、解耦等）
- **UML 類別圖（Mermaid）**：用 Mermaid classDiagram 表示該 pattern 的參與者與關係

文件 MUST 在結尾包含「三個模式如何協同運作」的整體說明，解釋 Strategy + Facade + Observer 如何在同一個爬蟲流程中互補。

#### Scenario: 文件涵蓋三個 pattern 的完整說明
- **WHEN** 開啟 `design_patterns_usage.md`
- **THEN** 文件包含 Strategy、Facade、Observer 三個章節，每個章節均有套用位置、UML 圖、效益說明

#### Scenario: 套用位置精確到類別與方法
- **WHEN** 閱讀任一 pattern 的「套用位置」段落
- **THEN** 能識別具體的類別名稱（如 `NewsParser`）與方法名稱（如 `parse()`），而非泛指「scraper.py 中」
