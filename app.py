import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from openai import OpenAI

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Borsa Asistanım", layout="centered")
st.title("🤖 AI Borsa Asistanı")

# --- YAN MENÜ (API KEY) ---
with st.sidebar:
    st.header("Ayarlar")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.info("API Anahtarını platform.openai.com adresinden alabilirsin.")

# --- ANA EKRAN ---
symbol_input = st.text_input("Hisse Kodu (Örn: THYAO, ASELS)", "THYAO")

# .IS Ekleme Kontrolü
if ".IS" not in symbol_input.upper():
    symbol = f"{symbol_input.upper()}.IS"
else:
    symbol = symbol_input.upper()

period = st.selectbox("Süre", ["1mo", "3mo", "6mo", "1y"], index=2)

# --- ANALİZ BUTONU ---
if st.button("Analiz Et 🚀", type="primary"):
    if not openai_api_key:
        st.error("Lütfen önce sol menüden OpenAI API Key girin!")
    else:
        with st.spinner('Veriler çekiliyor ve inceleniyor...'):
            try:
                # 1. Veriyi Çek
                df = yf.download(symbol, period=period)
                
                if len(df) > 0:
                    # Sütun isimlerini düzelt (MultiIndex sorunu varsa)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns =
