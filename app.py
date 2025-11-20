import streamlit as st
import yfinance as yf
import pandas as pd

# 1. SAYFA BAŞLIĞI
st.set_page_config(page_title="Borsa Analiz", layout="centered")
st.title("📉 Destek & Direnç Analizi")
st.caption("Basit, Hızlı ve Net Analiz")

# 2. YAN MENÜ
with st.sidebar:
    st.header("Bilgi")
    st.info("Bu uygulama ücretsizdir.")

# 3. GİRİŞ KISMI (Burada kutucuklar kesin görünür)
symbol_input = st.text_input("Hisse Kodu", "THYAO").upper()

# Kod düzeltme (.IS ekleme)
if ".IS" not in symbol_input and "USD" not in symbol_input:
    symbol = f"{symbol_input}.IS"
else:
    symbol = symbol_input

period = st.selectbox("Süre", ["3mo", "6mo", "1y"], index=1)

# 4. BUTON VE HESAPLAMA
if st.button("Analiz Et", type="primary"):
    with st.spinner('Veriler çekiliyor...'):
        try:
            # Veriyi indir
            df = yf.download(symbol, period=period)
            
            # Tablo başlıklarını düzelt
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            if not df.empty:
                # --- HESAPLAMALAR (Tek tek yapıyoruz) ---
                son_fiyat = float(df['Close'].iloc[-1])
                
                # Bollinger (Destek/Direnç)
                sma20 = df['Close'].rolling(20).mean().iloc[-1]
                std = df['Close'].rolling(20).std().iloc[-1]
                
                ust_direnc = sma20 + (2 * std)
                alt_destek = sma20 - (2 * std)
                
                # Trend (50 Günlük Ort)
                sma50 = float(df['Close'].rolling(50).mean().iloc[-1])
                
                # RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi_ham = 100 - (100 / (1 + rs))
                rsi = float(rsi_ham.iloc[-1])
                
                # --- EKRANA YAZDIRMA ---
                
                # 1. Grafik
                st.line_chart(df['Close'])
                
                # 2. Kritik Rakamlar
                st.subheader(f"{symbol_input} Kritik Seviyeler")
                c1, c2, c3 = st.columns(3)
                c1.metric("FİYAT", f"{son_fiyat:.2f} TL")
                c2.metric("DESTEK (Alım)", f"{alt_destek:.2f} TL", delta_color="normal")
                c3.metric("DİRENÇ (Satım)", f"{ust
