import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from openai import OpenAI

# Sayfa Ayarı
st.set_page_config(page_title="Borsa Asistanım", layout="centered")
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
                    # Sütun isimlerini düzelt (MultiIndex sorunu için)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    
                    # --- GARANTİLİ HESAPLAMA (HATA VERMEZ) ---
                    # 1. RSI Hesapla
                    df['RSI'] = ta.rsi(df['Close'], length=14)
                    
                    # 2. Bollinger Bantları (Manuel Matematik)
                    sma20 = df['Close'].rolling(window=20).mean()
                    std = df['Close'].rolling(window=20).std()
                    df['Alt_Bant'] = sma20 - (2 * std) # Alt bant formülü
                    
                    # 3. SMA 50
                    df['SMA50'] = df['Close'].rolling(window=50).mean()
                    
                    # Son veriyi al
                    son = df.iloc[-1]
                    
                    # Grafik ve Veriler
                    st.line_chart(df['Close'])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Fiyat", f"{son['Close']:.2f} TL")
                    col2.metric("RSI", f"{son['RSI']:.1f}")
                    col3.metric("Destek (Alt Bant)", f"{son['Alt_Bant']:.2f} TL")
                    
                    # Yapay Zeka Yorumu
                    client = OpenAI(api_key=openai_api_key)
                    prompt = f"""
                    Sen uzman bir borsa analistisin. {symbol} hissesi için şu verilere bak:
                    - Fiyat: {son['Close']:.2f} TL
                    - RSI (14): {son['RSI']:.2f} (30 altı ucuz, 70 üstü pahalı)
                    - Bollinger Alt Bant (Güçlü Destek): {son['Alt_Bant']:.2f} TL
                    - 50 Günlük Ortalama: {son['SMA50']:.2f} TL
                    
                    Yorumun şu formatta olsun:
                    1. **Teknik Analiz:** (Destek neresi, indikatörler ne diyor?)
                    2. **Risk Durumu:** (Düşük/Orta/Yüksek)
                    3. **Yatırımcı Tavsiyesi:** (Kısa ve öz, ne yapmalı?)
                    """
                    
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                    st.success(res.choices[0].message.content)
                else:
                    st.error("Veri bulunamadı. Hisse kodunu kontrol et.")
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
