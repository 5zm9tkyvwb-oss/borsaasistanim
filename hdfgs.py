import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI
import webbrowser

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HDFGS Patron Ekranı", layout="wide", page_icon="🦅")

# Özel CSS (KAP Bildirimi ve Kartlar için)
st.markdown("""
    <style>
    .metric-card {
        background-color: #0e1117;
        border: 1px solid #303030;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .kap-button {
        background-color: #FFD700;
        color: black;
        padding: 10px;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        display: block;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 HDFGS Özel Yönetim Paneli")

# --- YAN MENÜ: PORTFÖY AYARLARI ---
with st.sidebar:
    st.header("💼 Portföy Bilgilerin")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    st.divider()
    
    # Senin Maliyetin (Varsayılan 2.63)
    maliyet = st.number_input("Maliyetin (TL)", value=2.63, step=0.01)
    adet = st.number_input("Elindeki Lot Sayısı", value=1000, step=100)
    
    st.info(f"Hesaplamalar **{maliyet} TL** maliyete göre yapılacaktır.")

# --- VERİLERİ ÇEK ---
symbol = "HDFGS.IS"

try:
    # Son 6 aylık veri
    df = yf.download(symbol, period="6mo", progress=False)
    
    # Sütun temizliği
    if hasattr(df.columns, 'levels'):
        df.columns = df.columns.get_level_values(0)
        
    if not df.empty:
        # --- HESAPLAMALAR ---
        son_fiyat = float(df['Close'].iloc[-1])
        onceki_fiyat = float(df['Close'].iloc[-2])
        degisim = ((son_fiyat - onceki_fiyat) / onceki_fiyat) * 100
        
        # Kar/Zarar Hesabı
        toplam_deger = son_fiyat * adet
        yatirilan_tutar = maliyet * adet
        net_kar = toplam_deger - yatirilan_tutar
        kar_yuzdesi = ((son_fiyat - maliyet) / maliyet) * 100
        
        # Teknik Veriler
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        ust_bant = sma20 + (2 * std) # Direnç
        alt_bant = sma20 - (2 * std) # Destek
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])

        # --- EKRAN DÜZENİ (Üst Kısım: Para Durumu) ---
        st.subheader("💰 Canlı Kazanç Durumu")
        
        k1, k2, k3, k4 = st.columns(4)
        
        k1.metric("HDFGS Fiyatı", f"{son_fiyat:.2f} TL", f"%{degisim:.2f}")
        
        # Kar durumuna göre renkli gösterim
        k2.metric("Net Karın (TL)", f"{net_kar:,.2f} TL", delta_color="normal" if net_kar > 0 else "inverse")
        k3.metric("Kar Oranın", f"%{kar_yuzdesi:.2f}", delta_color="normal" if kar_yuzdesi > 0 else "inverse")
        k4.metric("Toplam Portföy Değeri", f"{toplam_deger:,.2f} TL")

        st.divider()
        
        # --- GRAFİK VE ANALİZ ---
        col_grafik, col_analiz = st.columns([2, 1])
        
        with col_grafik:
            st.subheader("📈 Fiyat Grafiği")
            st.line_chart(df['Close'])
            
        with col_analiz:
            st.subheader("🎯 Destek & Direnç")
            st.info(f"**DİRENÇ (Satış Bölgesi):**\n# {ust_bant:.2f} TL")
            st.success(f"**DESTEK (Alım Bölgesi):**\n# {alt_bant:.2f} TL")
            
            st.write("---")
            st.metric("RSI İndikatörü", f"{rsi:.1f}")
            if rsi > 70:
                st.warning("Hisse çok ısındı (Pahalı).")
            elif rsi < 30:
                st.success("Hisse çok ucuzladı.")
            else:
                st.info("Normal seyirde.")

        # --- HABERLER VE KAP ---
        st.divider()
        st.subheader("📰 Haberler ve KAP Bildirimleri")
        
        # KAP Link Butonu (En garanti yöntem)
        st.markdown(f"""
            <a href="https://www.kap.org.tr/tr/sirket-bilgileri/ozet/1686-hedef-girisim-sermayesi-yatirim-ortakligi-a-s" target="_blank" class="kap-button">
                🔔 RESMİ KAP BİLDİRİMLERİ İÇİN TIKLA (HDFGS)
            </a>
        """, unsafe_allow_html=True)
        st.write("")

        # Yfinance Haberleri
        try:
            haberler = yf.Ticker("HDFGS.IS").news
            if haberler:
                for haber in haberler[:3]: # Son 3 haberi getir
                    baslik = haber.get('title', 'Başlık Yok')
                    link = haber.get('link', '#')
                    zaman = pd.to_datetime(haber.get('providerPublishTime', 0), unit='s')
                    st.write(f"🗓️ **{zaman.strftime('%d-%m-%Y')}** | [{baslik}]({link})")
            else:
                st.write("Güncel global haber akışı yok.")
        except:
            st.write("Haber akışı şu an çekilemedi.")

        # --- YAPAY ZEKA YORUMU ---
        st.divider()
        if st.button("🤖 Yapay Zeka: 'Maliyetim 2.63, Ne Yapayım?'"):
            if not openai_api_key:
                st.error("Lütfen sol menüden API anahtarını gir.")
            else:
                client = OpenAI(api_key=openai_api_key)
                prompt = f"""
                Benim HDFGS hissem var. Maliyetim: {maliyet} TL.
                Şu anki Fiyat: {son_fiyat} TL.
                RSI: {rsi:.2f}.
                Direnç: {ust_bant:.2f}. Destek: {alt_bant:.2f}.
                
                Bana kişisel bir yatırım danışmanı gibi tavsiye ver.
                1. Karımı realize etmeli miyim yoksa beklemeli miyim?
                2. Teknik olarak risk var mı?
                3. Uzun vade için bu maliyet avantajlı mı?
                Cevabı Türkçe, samimi ve kısa maddelerle ver.
                """
                with st.spinner("Yapay zeka portföyünü inceliyor..."):
                    res = client.chat.completions.create(model="gpt-4o", messages=[{"role":"user", "content":prompt}])
                    st.success("### 🧠 AI Portföy Koçu")
                    st.write(res.choices[0].message.content)

    else:
        st.error("Veri alınamadı.")
except Exception as e:
    st.error(f"Hata: {e}")
