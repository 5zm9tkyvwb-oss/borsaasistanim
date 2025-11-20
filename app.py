import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from openai import OpenAI

# Sayfa Ayarları
st.set_page_config(page_title="Borsa Asistanım", layout="centered")
st.title("🤖 AI Borsa Asistanı")

# Yan Menü
with st.sidebar:
    st.header("Ayarlar")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.info("API Anahtarı: platform.openai.com")

# Ana Ekran
symbol = st.text_input("Hisse Kodu", "THYAO").upper()
if ".IS" not in symbol:
    symbol += ".IS"

period = st.selectbox("Süre", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.button("Analiz Et 🚀", type="primary"):
    if not openai_api_key:
        st.error("Lütfen önce API Key girin!")
    else:
        with st.spinner('İnceleniyor...'):
            try:
                # Veri Çek
                df = yf.download(symbol, period=period)
                
                # HATA VEREN KISMI GÜVENLİ HALE GETİRDİK:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                if not df.empty:
                    # Hesaplamalar
                    df['SMA20'] = df['Close'].rolling(20).mean()
                    df['STD'] = df['Close'].rolling(20).std()
                    df['Alt'] = df['SMA20'] - (2 * df['STD'])
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    
                    son = df.iloc[-1]
                    
                    # Ekrana Yaz
                    st.line_chart(df['Close'])
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Fiyat", f"{son['Close']:.2f}")
                    c2.metric("RSI", f"{son['RSI']:.1f}")
                    c3.metric("Destek", f"{son['Alt']:.2f}")
                    
                    # AI Yorumu
                    client = OpenAI(api_key=openai_api_key)
                    prompt = f"Hisse: {symbol}, Fiyat: {son['Close']:.2f}, RSI: {son['RSI']:.2f}, Destek: {son['Alt']:.2f}. Teknik analiz ve yorum yap."
                    
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                    st.success("Yapay Zeka Yorumu:")
                    st.write(res.choices[0].message.content)
                else:
                    st.error("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
