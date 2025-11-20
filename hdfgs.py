import streamlit as st
import yfinance as yf
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HDFGS Patron Ekranı", layout="wide", page_icon="🦅")

# Özel Tasarım
st.markdown("""
    <style>
    .metric-card { background-color: #0e1117; border: 1px solid #303030; padding: 15px; border-radius: 10px; text-align: center; }
    .kap-button { background-color: #FFD700; color: black; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; font-size: 18px; }
    .kap-button:hover { background-color: #E5C100; color: black; }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 HDFGS: Kişisel Servet Yönetimi")

# --- YAN MENÜ (Senin Rakamların) ---
with st.sidebar:
    st.header("💼 Cüzdan Ayarları")
    st.info("Rakamlar senin portföyüne göre ayarlandı.")
    
    st.divider()
    # Varsayılan değerleri senin verdiğin rakamlar yaptık
    maliyet = st.number_input("Maliyetin (TL)", value=2.63, step=0.01, format="%.2f")
    adet = st.number_input("Lot Sayısı", value=194028, step=1)

# --- AKILLI YORUM MOTORU ---
def akilli_yorum_yap(fiyat, maliyet, rsi, direnc, destek):
    yorumlar = []
    
    # 1. Maliyet Analizi
    kar_durumu = fiyat - maliyet
    if kar_durumu > 0:
        fark_yuzde = (kar_durumu / maliyet) * 100
        yorumlar.append(f"✅ **GÜZEL KAZANÇ:** Maliyetin (2.63) harika bir yerde. Şu an %{fark_yuzde:.1f} kardasın.")
    else:
        yorumlar.append(f"🔻 **ZARAR DURUMU:** Şu an maliyetinin biraz altındayız. Sakin kalıp destek seviyelerini takip etmelisin.")

    # 2. RSI (Ucuzluk/Pahalılık)
    if rsi < 30:
        yorumlar.append("💎 **FIRSAT:** Hisse teknik olarak çok ucuzladı (Aşırı Satım). Tepki gelebilir.")
    elif rsi > 70:
        yorumlar.append("🔥 **DİKKAT:** Hisse çok ısındı (Aşırı Alım). Kar satışı gelebilir.")
    else:
        yorumlar.append("⏸️ **NÖTR:** Fiyat dengeli gidiyor.")

    return yorumlar

# --- VERİ ÇEKME ---
symbol = "HDFGS.IS"
try:
    df = yf.download(symbol, period="6mo", progress=False)
    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
    if not df.empty:
        # --- HASSAS MATEMATİK HESABI ---
        son_fiyat = float(df['Close'].iloc[-1])
        
        # 1. Ana Para (Cebinden Çıkan)
        ana_para = maliyet * adet
        
        # 2. Güncel Değer (Şu anki Toplam Parası)
        guncel_deger = son_fiyat * adet
        
        # 3. Net Kar (Cebine Giren Fazlalık)
        net_kar = guncel_deger - ana_para
        
        # Teknik Veriler
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        ust_bant = sma20 + (2 * std)
        alt_bant = sma20 - (2 * std)
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])

        # --- EKRAN 1: DETAYLI CÜZDAN TABLOSU ---
        st.subheader("💰 Net Varlık Durumu")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("HDFGS Fiyatı", f"{son_fiyat:.2f} TL")
        c2.metric("Ana Paran (Maliyet)", f"{ana_para:,.0f} TL")
        c3.metric("Şu Anki Paran", f"{guncel_deger:,.0f} TL")
        c4.metric("NET KARIN", f"{net_kar:,.0f} TL", delta_color="normal" if net_kar > 0 else "inverse")

        st.divider()

        # --- EKRAN 2: HABER VE KAP ---
        st.markdown(f"""
            <a href="https://www.kap.org.tr/tr/sirket-bilgileri/ozet/1686-hedef-girisim-sermayesi-yatirim-ortakligi-a-s" target="_blank" class="kap-button">
                🔔 HDFGS KAP BİLDİRİMLERİ (RESMİ SİTE)
            </a>
        """, unsafe_allow_html=True)
        
        st.write("") 
        
        # --- EKRAN 3: GRAFİK VE ANALİZ ---
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Teknik Grafik")
            st.line_chart(df['Close'])
            
        with col2:
            st.subheader("🧠 Yapay Zeka Analizi")
            
            analizler = akilli_yorum_yap(son_fiyat, maliyet, rsi, ust_bant, alt_bant)
            
            for yorum in analizler:
                if "KAZANÇ" in yorum or "FIRSAT" in yorum:
                    st.success(yorum)
                elif "DİKKAT" in yorum or "ZARAR" in yorum:
                    st.error(yorum)
                else:
                    st.info(yorum)
            
            st.write("---")
            st.metric("Güçlü Destek", f"{alt_bant:.2f} TL")
            st.metric("Güçlü Direnç", f"{ust_bant:.2f} TL")

    else:
        st.error("Veri alınamadı.")
except Exception as e:
    st.error(f"Hata: {e}")
