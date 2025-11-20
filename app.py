import streamlit as st
import yfinance as yf
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Borsa Strateji", layout="centered")
st.title("📉 Destek & Direnç Analizi")
st.caption("Otomatik Seviye Tespit Sistemi")

# --- YAN MENÜ ---
with st.sidebar:
    st.header("Ayarlar")
    st.info("Bu modül ücretsizdir. Destek ve Direnç noktalarını matematiksel olarak hesaplar.")

# --- HESAPLAMA MOTORU ---
def teknik_analiz_yap(df):
    # Veriler (Float'a çevirerek garantiye alıyoruz)
    son_fiyat = float(df['Close'].iloc[-1])
    
    # 1. Hareketli Ortalamalar (SMA)
    sma20_seri = df['Close'].rolling(window=20).mean()
    sma50_seri = df['Close'].rolling(window=50).mean()
    
    sma20 = float(sma20_seri.iloc[-1])
    sma50 = float(sma50_seri.iloc[-1])

    # 2. Bollinger Bantları (Destek ve Direnç için)
    std_seri = df['Close'].rolling(window=20).std()
    std = float(std_seri.iloc[-1])
    
    ust_bant = sma20 + (2 * std) # DİRENÇ
    alt_bant = sma20 - (2 * std) # DESTEK
    
    # 3. RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_seri = 100 - (100 / (1 + rs))
    rsi = float(rsi_seri.iloc[-1])

    return son_fiyat, rsi, alt_bant, ust_bant, sma50

def karar_ver(fiyat, rsi, alt_bant, ust_bant, sma50):
    puan = 0
    yorumlar = []

    # Kural 1: RSI
    if rsi < 35:
        puan += 2
        yorumlar.append("✅ RSI 'Ucuz' bölgede (35 altı).")
    elif rsi > 65:
        puan -= 2
        yorumlar.append("⚠️ RSI 'Pahalı' bölgede (65 üstü).")

    # Kural 2: Destek/Direnç Yakınlığı
    if fiyat <= alt_bant * 1.02: 
        puan += 1
        yorumlar.append("✅ Fiyat DESTEK seviyesine çok yakın (Tepki verebilir).")
    elif fiyat >= ust_bant * 0.98:
        puan -= 1
        yorumlar.append("⚠️ Fiyat DİRENÇ seviyesine dayandı (Satış yiyebilir).")

    # Kural 3: Trend
    if fiyat > sma50:
        puan += 1
        yorumlar.append("✅ Yükseliş Trendi (Fiyat ortalamanın üzerinde).")
    else:
        puan -= 1
        yorumlar.append("🔻 Düşüş Trendi (Fiyat ortalamanın altında).")

    # Karar Mekanizması
    karar = "NÖTR / İZLE"
    renk = "gray"
    
    if puan >= 3:
        karar = "GÜÇLÜ AL 🚀"
        renk = "green"
    elif puan >= 1:
        karar = "ALIM ADAYI 🌱"
        renk = "green"
    elif puan <= -3:
        karar = "GÜÇLÜ SAT 🚨"
