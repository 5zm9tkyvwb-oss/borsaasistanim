import streamlit as st
import yfinance as yf
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Borsa Strateji", layout="centered")
st.title("📈 Otomatik Borsa Stratejisi")
st.caption("Yapay Zeka Yok, Saf Matematik Var. (Ücretsiz Versiyon)")

# --- YAN MENÜ ---
with st.sidebar:
    st.header("Ayarlar")
    st.info("Bu modül tamamen ücretsizdir. OpenAI anahtarı gerektirmez.")

# --- HESAPLAMA MOTORU ---
def teknik_analiz_yap(df):
    # Veriler (Float'a çevirerek garantiye alıyoruz)
    son_fiyat = float(df['Close'].iloc[-1])
    
    # 1. Hareketli Ortalamalar (SMA)
    sma20_seri = df['Close'].rolling(window=20).mean()
    sma50_seri = df['Close'].rolling(window=50).mean()
    
    # Sadece son günün değerini alıyoruz
    sma20 = float(sma20_seri.iloc[-1])
    sma50 = float(sma50_seri.iloc[-1])

    # 2. Bollinger Bantları
    std_seri = df['Close'].rolling(window=20).std()
    std = float(std_seri.iloc[-1]) # Son standart sapma
    
    ust_bant = sma20 + (2 * std)
    alt_bant = sma20 - (2 * std)
    
    # 3. RSI Hesaplama
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi_seri = 100 - (100 / (1 + rs))
    rsi = float(rsi_seri.iloc[-1]) # Son RSI değeri

    return son_fiyat, rsi, alt_bant, ust_bant, sma50

def karar_ver(fiyat, rsi, alt_bant, ust_bant, sma50):
    puan = 0
    yorumlar = []

    # --- STRATEJİ KURALLARI ---
    
    # Kural 1: RSI Stratejisi
    if rsi < 35:
        puan += 2
        yorumlar.append("✅ RSI aşırı satım bölgesinde (Ucuz).")
    elif rsi > 65:
        puan -= 2
        yorumlar.append("⚠️ RSI aşırı alım bölgesinde (Pahalı).")
    else:
        yorumlar.append("ℹ️ RSI nötr bölgede.")

    # Kural 2: Bollinger Stratejisi
    if fiyat < alt_bant * 1.02: 
        puan += 1
        yorumlar.append("✅ Fiyat destek seviyesine yakın.")
    elif fiyat > ust_bant * 0.98:
        puan -= 1
        yorumlar.append("⚠️ Fiyat direnç seviyesine yakın.")

    # Kural 3: Trend (SMA 50)
    if fiyat > sma50:
        puan += 1
        yorumlar.append("✅ Trend Pozitif (50 günlüğün üzerinde).")
    else:
        puan -= 1
        yorumlar.append("🔻 Trend Negatif (50 günlüğün altında).")

    # --- SONUÇ ---
    karar = "NÖTR / BEKLE"
    renk = "gray"
    
    if puan >= 3:
        karar = "GÜÇLÜ AL 🚀"
        renk = "green"
    elif puan >= 1:
        karar = "ALIM ADAYI 🌱"
        renk = "green"
    elif puan <= -3:
        karar = "GÜÇLÜ SAT 🚨"
        renk = "red"
    elif puan <= -1:
        karar = "SATIŞ BASKISI 🔻"
        renk = "red"

    return karar, renk, yorumlar

# --- ARAYÜZ ---
symbol_input = st.text_input("Hisse Kodu Girin", "THYAO")
if ".IS" not in symbol_input.upper():
    symbol = f"{symbol_input.upper()}.IS"
else:
    symbol = symbol_input.upper()

period = st.selectbox("Zaman Dilimi", ["3mo", "6mo", "1y"], index=1)

if st.button("Analiz Et (Ücretsiz)", type="primary"):
    with st.spinner('Hesaplanıyor...'):
        try:
            df = yf.download(symbol, period=period)
            
            # Sütun düzeltme
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if not df.empty:
                # Hesapla
                fiyat, rsi, alt, ust, sma50 = teknik_analiz_yap(df)
                karar, renk, yorumlar = karar_ver(fiyat, rsi, alt, ust, sma50)

                # Grafiği Çiz
                st.line_chart(df['Close'])

                # Temel Veriler
                c1, c2, c3 = st.columns(3)
                c1.metric("Fiyat", f"{fiyat:.2f} TL")
                c2.metric("RSI", f"{rsi:.1f}")
                c3.metric("Puan", f"{len(yorumlar)}")

                st.divider()

                # --- STRATEJİ SONUCU ---
                st.subheader("📢 Sinyal Durumu")
                
                if renk == "green":
                    st.success(f"### {karar}")
                elif renk == "red":
                    st.error(f"### {karar}")
                else:
                    st.warning(f"### {karar}")

                st.write("---")
                st.write("**Neden Böyle Düşünüyor?**")
                for yorum in yorumlar:
                    st.write(yorum)
            else:
                st.error("Veri çekilemedi.")
        except Exception as e:
            st.error(f"Hata oluştu: {e}")
