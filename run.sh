#!/bin/bash
if [ ! -d ".venv" ]; then
    echo "建立虛擬環境..."
    python3 -m venv .venv
fi
if [ ! -d ".venv/lib" ]; then
    echo "安裝套件..."
    .venv/bin/pip install -r requirements.txt
fi
echo "啟動應用程式..."
.venv/bin/streamlit run app.py
