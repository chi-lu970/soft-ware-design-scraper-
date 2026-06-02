@echo off
if not exist ".venv" (
    echo 建立虛擬環境...
    python -m venv .venv
)
if not exist ".venv\Lib\site-packages\streamlit" (
    echo 安裝套件...
    .venv\Scripts\pip install -r requirements.txt
)
echo 啟動應用程式...
.venv\Scripts\streamlit run app.py
