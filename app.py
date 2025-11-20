import streamlit as st
import yfinance as yf

# --- AYARLAR ---
st.set_page_config(page_title="Piyasa Uzmanı", layout="centered")
st.title("🌍 Tüm Piyasa Analizi")
st.caption("Borsa • Kripto • Döviz • Altın")

# --- KATEGORİ SEÇİMİ ---
st.sidebar.header("Ne Analiz Edeceğiz?")
kategori = st.sidebar.radio("Seçiniz:", ["Borsa İstanbul (Hisse)", "Kripto Para (Coin)", "Döviz & Altın"])

# --- KOD BELİRLEME MANTIĞI ---
symbol = ""

if kategori == "Borsa İstanbul (Hisse)":
    giris = st.text_input("Hisse Kodu", "THYAO").upper()
    symbol = f"{giris}.IS"
    
elif kategori == "Kripto Para (Coin)":
    giris = st.text_input("Coin Kodu (Örn: BTC, ETH, SOL)", "BTC").upper()
    symbol = f"{giris}-USD"

else: # Döviz ve Altın
    secim = st.selectbox("Parite Seçin", ["Dolar (USD/TRY)", "Euro (EUR/TRY)", "Ons Altın ($)", "Gümüş ($)"])
    # Kod Eşleştirme
    if secim == "Dolar (USD/TRY)": symbol = "TRY=X"
    elif secim == "Euro (EUR/TRY)": symbol = "EURTRY=X"
    elif secim == "Ons Altın ($)": symbol = "GC=F"
    elif secim == "Gümüş ($)": symbol = "SI=F"

# --- ANALİZ BUTONU ---
if st.button(f"{kategori} Analiz Et 🚀"):
    try:
        with st.spinner('Piyasa verileri çekiliyor...'):
            # Veri İndir
            df = yf.download(symbol, period="6mo")
            
            # Veri Temizliği (Hata Önleyici)
            if hasattr(df.columns, 'levels'): 
                df.columns = df.columns.get_level_values(0)
                
            if not df.empty:
                # --- MATEMATİKSEL HESAPLAMALAR ---
                son_fiyat = df['Close'].iloc[-1]
                
                # Bollinger Bantları (Destek/Direnç)
                ort = df['Close'].rolling(20).mean().iloc[-1]
                sapma = df['Close'].rolling(20).std().iloc[-1]
                destek = ort - (2 * sapma)
                direnc = ort + (2 * sapma)
                
                # --- EKRAN TASARIMI ---
                st.subheader(f"📊 {symbol} Analizi")
                
                c1, c2, c3 = st.columns(3)
                
                # Kripto ve Altın için Dolar işareti, TR piyasası için TL
                para_birimi = "TL" if "TRY" in symbol or ".IS" in symbol else "$"
                
                c1.metric("GÜNCEL FİYAT", f"{son_fiyat:.2f} {para_birimi}")
                c2.metric("ALIM YERİ (Destek)", f"{destek:.2f} {para_birimi}", delta_color="normal")
                c3.metric("SATIM YERİ (Direnç)", f"{direnc:.2f} {para_birimi}", delta_color="inverse")
                
                # Grafik
                st.line_chart(df['Close'])
                
                # YORUM MOTORU
                st.write("---")
                if son_fiyat < destek * 1.02:
                    st.success(f"✅ FİYAT ÇOK UCUZLADI! Desteğe ({destek:.2f}) yakın. Tepki verebilir.")
                elif son_fiyat > direnc * 0.98:
                    st.error(f"🔻 FİYAT ÇOK YÜKSELDİ! Dirence ({direnc:.2f}) dayandı. Satış yiyebilir.")
                else:
                    st.info("⏸️ Fiyat orta bantta, yatay seyrediyor. Kırılım beklenmeli.")
                    
            else:
                st.error("Veri bulunamadı! Kodu kontrol edin.")
                
    except Exception as e:
        st.error(f"Hata oluştu: {e}")
