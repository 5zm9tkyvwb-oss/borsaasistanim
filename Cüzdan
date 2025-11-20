import streamlit as st
import yfinance as yf

# --- AYARLAR ---
st.set_page_config(page_title="Sanal Trader", layout="centered")
st.title("💰 Sanal Borsa Simülasyonu")

# --- HAFIZA (SESSION STATE) ---
if 'bakiye' not in st.session_state:
    st.session_state.bakiye = 10000.0  # Başlangıç Parası 10.000 $

if 'portfoy' not in st.session_state:
    st.session_state.portfoy = {}  # Hisseler burada duracak

# --- YAN MENÜ ---
with st.sidebar:
    st.header("💼 CÜZDANIM")
    st.metric("Nakit Bakiye", f"${st.session_state.bakiye:,.2f}")
    
    st.write("---")
    st.subheader("Varlıklarım")
    if len(st.session_state.portfoy) > 0:
        for hisse, adet in st.session_state.portfoy.items():
            st.write(f"🔹 **{hisse}:** {adet:.2f} Adet")
    else:
        st.info("Henüz varlık yok.")

    if st.button("Cüzdanı Sıfırla"):
        st.session_state.bakiye = 10000.0
        st.session_state.portfoy = {}
        st.rerun()

# --- ANA EKRAN ---
st.subheader("Alım / Satım Ekranı")

col1, col2 = st.columns(2)
with col1:
    kategori = st.selectbox("Piyasa Seç", ["Kripto (USD)", "Borsa (TL)", "Altın/Döviz"])
with col2:
    kod_giris = st.text_input("Sembol (Örn: BTC, THYAO)", "BTC").upper()

# Sembol Ayarlama
symbol = ""
para_birimi = "$"
if kategori == "Kripto (USD)":
    symbol = f"{kod_giris}-USD"
elif kategori == "Borsa (TL)":
    symbol = f"{kod_giris}.IS"
    para_birimi = "TL (Sanal Kur $)"
else:
    if kod_giris == "ALTIN": symbol = "GC=F"
    elif kod_giris == "DOLAR": symbol = "TRY=X"
    else: symbol = f"{kod_giris}=X"

# --- İŞLEM MOTORU ---
if symbol:
    try:
        data = yf.download(symbol, period="1d", progress=False)
        if not data.empty:
            # Veri düzeltme
            if hasattr(data.columns, 'levels'): 
                data.columns = data.columns.get_level_values(0)
                
            guncel_fiyat = float(data['Close'].iloc[-1])
            
            st.info(f"📢 **{symbol}** Fiyat: **{guncel_fiyat:,.2f} {para_birimi}**")
            
            # Miktar Girişi
            miktar = st.number_input("Kaç Adet Alacaksın/Satacaksın?", min_value=0.01, value=1.0, step=0.1)
            tutar = guncel_fiyat * miktar
            
            st.write(f"💵 İşlem Tutarı: **${tutar:,.2f}**")
            
            btn1, btn2 = st.columns(2)
            
            # AL BUTONU
            if btn1.button("🟢 AL (BUY)"):
                if st.session_state.bakiye >= tutar:
                    st.session_state.bakiye -= tutar
                    if symbol in st.session_state.portfoy:
                        st.session_state.portfoy[symbol] += miktar
                    else:
                        st.session_state.portfoy[symbol] = miktar
                    st.success(f"{miktar} adet {symbol} alındı!")
                    st.rerun()
                else:
                    st.error("❌ Paran Yetmiyor!")

            # SAT BUTONU
            if btn2.button("🔴 SAT (SELL)"):
                if symbol in st.session_state.portfoy:
                    mevcut = st.session_state.portfoy[symbol]
                    if mevcut >= miktar:
                        st.session_state.bakiye += tutar
                        st.session_state.portfoy[symbol] -= miktar
                        if st.session_state.portfoy[symbol] <= 0.01:
                            del st.session_state.portfoy[symbol]
                        st.success(f"{miktar} adet {symbol} satıldı!")
                        st.rerun()
                    else:
                        st.error("❌ Elinde o kadar yok!")
                else:
                    st.error("❌ Cüzdanında bu varlık yok!")
                    
        else:
            st.warning("Veri gelmedi. Kodu kontrol et.")
    except Exception as e:
        st.error(f"Hata: {e}")
