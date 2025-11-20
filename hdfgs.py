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

st.title("🦅 HDFGS: Sınırsız Patron Paneli")

# --- YAN MENÜ ---
with st.sidebar:
    st.header("💼 Cüzdan Ayarları")
    st.info("Bu modül tamamen ücretsizdir. Sınırsız analiz yapabilirsin.")
    
    st.divider()
    maliyet = st.number_input("Maliyetin (TL)", value=2.63, step=0.01)
    adet = st.number_input("Lot Sayısı", value=1000, step=100)

# --- AKILLI YORUM MOTORU (Ücretsiz Yapay Zeka) ---
def akilli_yorum_yap(fiyat, maliyet, rsi, direnc, destek):
    yorumlar = []
    
    # 1. Maliyet Analizi
    kar_durumu = fiyat - maliyet
    if kar_durumu > 0:
        fark_yuzde = (kar_durumu / maliyet) * 100
        if fark_yuzde > 50:
            yorumlar.append(f"🚀 **MÜKEMMEL KAZANÇ:** Maliyetin ({maliyet} TL) harika bir yerde kalmış. Şu an %{fark_yuzde:.1f} kardasın. Keyfini sür.")
        else:
            yorumlar.append(f"✅ **KARDASIN:** İşler yolunda. Maliyetinin üzerindesin, panik yapacak bir durum yok.")
    else:
        yorumlar.append(f"🔻 **ZARARDASIN:** Şu an maliyetinin biraz altındayız. Sakin kalıp destek seviyelerini takip etmelisin.")

    # 2. RSI (Ucuzluk/Pahalılık)
    if rsi < 30:
        yorumlar.append("💎 **FIRSAT OLABİLİR:** Hisse teknik olarak 'Bedava' denecek kadar ucuzlamış (Aşırı Satım). Tepki yükselişi yakındır.")
    elif rsi > 70:
        yorumlar.append("🔥 **DİKKAT:** Hisse çok ısındı (Aşırı Alım). Kar satışı gelebilir, dikkatli ol.")
    elif 50 <= rsi <= 70:
        yorumlar.append("📈 **GÜÇLÜ:** Alıcılar hala istekli görünüyor, trend yukarı yönlü olabilir.")
    else:
        yorumlar.append("⏸️ **NÖTR:** Fiyat dengeli gidiyor. Ani bir hareket öncesi sessizlik olabilir.")

    # 3. Destek/Direnç Stratejisi
    if fiyat >= direnc * 0.98:
        yorumlar.append(f"⚠️ **DİRENCE GELDİK:** Fiyat {direnc:.2f} TL seviyesine dayandı. Burayı geçemezse biraz geri çekilebilir.")
    elif fiyat <= destek * 1.02:
        yorumlar.append(f"🛡️ **DESTEKTEYİZ:** Fiyat {destek:.2f} TL desteğine tutunmaya çalışıyor. Buradan güç alıp dönebilir.")

    return yorumlar

# --- VERİ ÇEKME ---
symbol = "HDFGS.IS"
try:
    df = yf.download(symbol, period="6mo", progress=False)
    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
    if not df.empty:
        # Hesaplamalar
        son_fiyat = float(df['Close'].iloc[-1])
        toplam_deger = son_fiyat * adet
        net_kar = (son_fiyat - maliyet) * adet
        yuzde_kar = ((son_fiyat - maliyet) / maliyet) * 100
        
        # Teknik
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

        # --- EKRAN 1: PARA DURUMU ---
        st.subheader("💰 Cüzdan Durumu")
        k1, k2, k3 = st.columns(3)
        k1.metric("Anlık Fiyat", f"{son_fiyat:.2f} TL")
        k2.metric("Net Karın", f"{net_kar:,.2f} TL", delta_color="normal" if net_kar > 0 else "inverse")
        k3.metric("Toplam Paran", f"{toplam_deger:,.2f} TL")

        st.divider()

        # --- EKRAN 2: HABER MERKEZİ (KAP) ---
        st.markdown(f"""
            <a href="https://www.kap.org.tr/tr/sirket-bilgileri/ozet/1686-hedef-girisim-sermayesi-yatirim-ortakligi-a-s" target="_blank" class="kap-button">
                🔔 HDFGS KAP BİLDİRİMLERİ (RESMİ SİTE)
            </a>
        """, unsafe_allow_html=True)
        
        st.write("") # Boşluk
        
        # --- EKRAN 3: SINIRSIZ ANALİST ---
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📈 Teknik Grafik")
            st.line_chart(df['Close'])
            
        with c2:
            st.subheader("🧠 Sınırsız Analiz")
            
            # Butona gerek yok, otomatik analiz etsin
            analizler = akilli_yorum_yap(son_fiyat, maliyet, rsi, ust_bant, alt_bant)
            
            for yorum in analizler:
                if "MÜKEMMEL" in yorum or "FIRSAT" in yorum:
                    st.success(yorum)
                elif "DİKKAT" in yorum or "ZARARDASIN" in yorum:
                    st.error(yorum)
                else:
                    st.info(yorum)
            
            st.write("---")
            st.metric("RSI Gücü", f"{rsi:.1f}")
            st.metric("Direnç Hedefi", f"{ust_bant:.2f} TL")

    else:
        st.error("Veri alınamadı.")
except Exception as e:
    st.error(f"Hata: {e}")
