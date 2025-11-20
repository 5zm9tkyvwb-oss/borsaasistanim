import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from openai import OpenAI

# Sayfa Ayarı
st.set_page_config(page_title="Borsa Asistanım", layout="mobile")
st.title("🤖 AI Borsa Asistanı")

# Ayarlar Menüsü
with st.sidebar:
    st.header("Ayarlar")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.info("API Anahtarını platform.openai.com adresinden alabilirsin.")

# Ana Ekran
symbol_input = st.text_input("Hisse Kodu (Örn: THYAO)", "THYAO")
if ".IS" not in symbol_input.upper():
    symbol = f"{symbol_input.upper()}.IS"
else:
    symbol = symbol_input.upper()

period = st.selectbox("Süre", ["1mo", "3mo", "6mo", "1y"], index=2)

# Analiz Butonu
if st.button("Analiz Et 🚀", type="primary"):
    if not openai_api_key:
        st.error("Lütfen önce sol menüden OpenAI API Key girin!")
    else:
        with st.spinner('Yapay Zeka Verileri İnceliyor...'):
            try:
                # Veri Çekme
                df = yf.download(symbol, period=period)
                if len(df) > 0:
                    # İndikatör Hesapla
                    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    df['SMA50'] = ta.sma(df['Close'], length=50)
                    bb = ta.bbands(df['Close'], length=20)
                    df['Alt_Bant'] = bb['BBL_20_2.0']
                    
                    son = df.iloc[-1]
                    
                    # Grafik ve Veriler
                    st.line_chart(df['Close'])
                    col1, col2 = st.columns(2)
                    col1.metric("Fiyat", f"{son['Close']:.2f} TL")
                    col2.metric("RSI", f"{son['RSI']:.1f}")
                    
                    # Yapay Zeka Yorumu
                    client = OpenAI(api_key=openai_api_key)
                    prompt = f"Borsa uzmanı gibi davran. {symbol} hissesi fiyatı: {son['Close']:.2f}, RSI: {son['RSI']:.2f}, Destek: {son['Alt_Bant']:.2f}. Bu verilere göre kısa bir yatırımcı tavsiyesi ver."
                    
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                    st.success(res.choices[0].message.content)
                else:
                    st.error("Veri bulunamadı.")
            except Exception as e:
                st.error(f"Hata: {e}")
