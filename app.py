"""
app.py — Streamlit 前端應用程式（View / Controller 層）

此模組負責使用者介面的呈現與流程控制。
所有爬取與解析邏輯由 scraper.py 的 Scraper 類別負責，
本模組不包含任何爬蟲邏輯。

架構角色：MVC 中的 View + Controller
執行方式：streamlit run app.py
"""

import requests
import streamlit as st
import pandas as pd

# 從 Model 層匯入 Scraper 類別
from scraper import Scraper


# ── 頁面基本設定 ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="關鍵字爬蟲整合系統",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stDataFrameResizable"] th {
    font-size: 16px !important;
    font-weight: 600 !important;
}
[data-testid="stBaseButton-primary"] {
    background-color: #1a73e8 !important;
    border-color: #1a73e8 !important;
    color: white !important;
}
[data-testid="stBaseButton-primary"]:hover {
    background-color: #1558b0 !important;
    border-color: #1558b0 !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextInput"] input:active,
[data-testid="stTextInput"] input:focus-visible {
    border-color: #1a73e8 !important;
    box-shadow: none !important;
    outline: none !important;
}
[data-testid="stTextInput"]:focus-within {
    border-color: #1a73e8 !important;
    box-shadow: none !important;
}
/* 工具列常駐顯示、靠左 */
[data-testid="stElementToolbar"] {
    opacity: 1 !important;
    visibility: visible !important;
    left: 0 !important;
    right: auto !important;
}
/* 工具列按鈕放大 */
[data-testid="stBaseButton-elementToolbar"] {
    width: 34px !important;
    height: 34px !important;
}
[data-testid="stBaseButton-elementToolbar"] svg {
    width: 18px !important;
    height: 18px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("關鍵字爬蟲整合系統")
st.markdown(
    "輸入關鍵字後點擊搜尋，系統將自動從 **Google News RSS** 爬取相關新聞，"
    "並以表格形式呈現結果。"
)
st.divider()


# ── 搜尋介面（View） ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])

with col1:
    # 關鍵字輸入框
    keyword = st.text_input(
        label="搜尋關鍵字",
        placeholder="請輸入關鍵字（中文或英文均可），例如：人工智慧",
        label_visibility="collapsed",
    )

with col2:
    # 搜尋按鈕
    search_clicked = st.button("搜尋", use_container_width=True, type="primary")


# ── session_state 初始化（保存搜尋結果，避免輸入框變動時畫面清空） ──────────────────
if "result_df" not in st.session_state:
    st.session_state.result_df = None
if "result_keyword" not in st.session_state:
    st.session_state.result_keyword = ""

# ── 控制流程（Controller） ────────────────────────────────────────────────────────
if search_clicked:

    # 驗證：空白關鍵字不執行爬蟲
    if not keyword or not keyword.strip():
        st.warning("⚠️ 請輸入關鍵字後再搜尋。")
        st.stop()

    # 執行爬蟲，顯示載入狀態
    with st.spinner(f'正在爬取「{keyword}」的相關新聞，請稍候...'):
        try:
            scraper = Scraper(keyword=keyword, max_results=10)
            df = scraper.run()

        except requests.exceptions.ConnectionError:
            st.error("❌ 網路連線失敗，請確認您的網路設定後再試。")
            st.stop()

        except requests.exceptions.Timeout:
            st.error("❌ 請求逾時（超過 10 秒），請稍後再試。")
            st.stop()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else "未知"
            st.error(f"❌ 伺服器回應錯誤（狀態碼：{status_code}），請稍後再試。")
            st.stop()

        except Exception as e:
            st.error(f"❌ 資料解析失敗，目標網站格式可能已變更。（詳情：{e}）")
            st.stop()

    # 將結果存入 session_state，跨重新渲染保留
    st.session_state.result_df = df
    st.session_state.result_keyword = keyword

# ── 結果顯示（View）：從 session_state 讀取，不依賴按鈕是否剛被點擊 ────────────────
if st.session_state.result_df is not None:
    df = st.session_state.result_df
    saved_keyword = st.session_state.result_keyword

    st.divider()

    if df.empty:
        st.info(f"⚠️ 未找到「{saved_keyword}」的相關結果，請嘗試其他關鍵字。")
    else:
        st.success(f"共找到 **{len(df)}** 筆結果（關鍵字：{saved_keyword}）")
        st.dataframe(
            df.reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
            column_config={
                "標題": st.column_config.TextColumn("標題", width=260),
                "刊登時間": st.column_config.TextColumn("刊登時間", width=60),
                "來源": st.column_config.TextColumn("來源", width=60),
                "關鍵句子": st.column_config.TextColumn("關鍵句子", width=600),
                "網址": st.column_config.LinkColumn(
                    "網址",
                    display_text="開啟連結",
                    width=60,
                ),
            },
        )


# ── 頁面底部說明 ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "📌 資料來源：Google News RSS Feed｜"
    "本系統僅供學術教學使用，請遵守目標網站的使用條款。"
)
