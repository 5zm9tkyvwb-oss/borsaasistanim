import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np

def get_ai_comment(symbol, change, rsi, volume_change):
    """
    Basit bir Karar Ağacı ile Yapay Zeka Yorumu Simülasyonu.
    Eğer gerçek OpenAI/Gemini API anahtarın varsa buraya o entegre edilir.
    """
    comment = f"🤖 **{symbol} Analizi:** "
    
    # Yükseliş Potansiyeli Analizi
    if change > 0 and volume_change > 20:
        comment += "Hissede ciddi bir **PARA GİRİŞİ** tespit edildi. Fiyat artışını hacim destekliyor. Yükseliş trendi güçlü görünüyor. "
    elif change > 0 and volume_change < 0:
        comment += "Fiyat yükseliyor ancak hacim zayıf. Bu bir tepki yükselişi olabilir, dikkatli olunmalı. "
    elif change < 0 and rsi < 30:
        comment += "Hisse aşırı satım bölgesinde (RSI < 30). Buradan bir tepki alımı ve dönüş potansiyeli yüksek olabilir. "
    elif change > 5:
        comment += "Günlük bazda çok sert bir yükseliş var. Kâr realizasyonu gelebilir. "
    else:
        comment += "Yatay ve kararsız bir seyir izliyor. Destek/Direnç takibi yapılmalı. "
        
    return comment

def fetch_market_data():
    # HDFGS senin favorin, diğerleri ise potansiyel hacimli hisseler (Örnek: THY, Aselsan, Miatek, Reedr)
    tickers = ['HDFGS.IS', 'THYAO.IS', 'ASELS.IS', 'MIATK.IS', 'REEDR.IS']
    
    data_list = []
    
    for ticker in tickers:
        try:
            # Son 5 günlük veriyi çekiyoruz ki hacim kıyaslayabilelim
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            
            if len(hist) > 0:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                current_vol = hist['Volume'].iloc[-1]
                prev_vol = hist['Volume'].iloc[-2]
                
                # Değişim Oranları
                price_change = ((current_price - prev_price) / prev_price) * 100
                vol_change = ((current_vol - prev_vol) / prev_vol) * 100 if prev_vol != 0 else 0
                
                # Basit RSI Hesabı (Son 5 gün için yaklaşık)
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=5).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=5).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]

                # Yapay Zeka Yorumunu Oluştur
                ai_analysis = get_ai_comment(ticker.replace('.IS', ''), price_change, rsi, vol_change)
                
                data_list.append({
                    "Hisse": ticker.replace('.IS', ''),
                    "Fiyat": round(current_price, 2),
                    "Değişim (%)": round(price_change, 2),
                    "Hacim Değişimi (%)": round(vol_change, 2),
                    "RSI": round(rsi, 2),
                    "AI Yorumu": ai_analysis
                })
        except Exception as e:
            st.error(f"Veri hatası: {ticker}")

    return pd.DataFrame(data_list)

# --- Uygulama Arayüzü ---
st.subheader("🚀 Öne Çıkanlar ve HDFGS Analizi")

# Veriyi Çek
df_analysis = fetch_market_data()

# Ekrana Bas
if not df_analysis.empty:
    # Tabloyu Göster
    st.dataframe(df_analysis[['Hisse', 'Fiyat', 'Değişim (%)', 'Hacim Değişimi (%)', 'RSI']])
    
    st.markdown("---")
    st.subheader("🤖 Yapay Zeka Piyasa Yorumları")
    
    # Yorumları Kartlar Halinde Göster
    for index, row in df_analysis.iterrows():
        with st.expander(f"{row['Hisse']} - Detaylı Yorum İçin Tıkla", expanded=True):
            if row['Hacim Değişimi (%)'] > 20 and row['Değişim (%)'] > 0:
                st.success(row['AI Yorumu']) # Pozitif durumlar için yeşil
            elif row['Değişim (%)'] < -2:
                st.error(row['AI Yorumu'])   # Negatif durumlar için kırmızı
            else:
                st.info(row['AI Yorumu'])    # Nötr durumlar için mavi
else:
    st.warning("Piyasa verileri şu an çekilemiyor.")
