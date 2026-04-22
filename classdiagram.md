# 關鍵字爬蟲整合系統 — UML 領域模型類別圖

## PlantUML 原始碼

貼到 [PlantUML Online](https://www.plantuml.com/plantuml/uml/) 即可產生圖形。

@startuml 關鍵字爬蟲整合系統_DomainModel_Professional

' ════════════ 核心配置 ════════════
title 關鍵字爬蟲整合系統 - 領域模型 (精簡版)

' 強制由左至右展開，避免垂直堆疊產生的混亂
left to right direction
skinparam shadowing false
skinparam roundcorner 8
skinparam dpi 150

' 隱藏所有方法，只保留屬性
hide methods
skinparam classAttributeIconSize 0

' 樣式精調
skinparam class {
    BackgroundColor White
    BorderColor #E67E22
    BorderThickness 2
    ArrowColor #2C3E50
    HeaderBackgroundColor #FAD7A0
}
skinparam actorStyle awesome

' ════════════ 實體定義 ════════════

class "使用者" as User <<actor>> #F2F4F4 {
    + 搜尋關鍵字
}

rectangle "核心流程" #FDFEFE {
    class "搜尋請求" as Request {
        + keyword
        + max_results
    }

    class "爬蟲引擎" as Scraper <<Engine>> #FEF9E7 {
        + RSS_URL_TEMPLATE
        - _raw_xml
    }
}

class "搜尋結果" as Result {
    + 文章列表
    + 總筆數
}

class "新聞文章" as Article {
    + 標題
    + 刊登時間
    + 來源
    + 摘要句子
    + 網址
}

' ════════════ 佈局與連線 ════════════

' 使用多重橫槓 (---) 增加間距，讓線路更長更清晰
User "1" -right- "1..*" Request : 發起 >
Request "1" -right- "1" Scraper : 驅動 >
Scraper "1" -right- "1" Result : 產出 >

' 垂直佈局文章細節，與主流程垂直交會，增加美感
Result "1" *-- "0..*" Article : 包含 >

' 輔助虛線，避免實線過多導致交疊
User ..> Result : 查閱結果

@enduml