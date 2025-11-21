import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="HDFGS & Balina Pro", layout="wide", page_icon="🦅")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    
    /* Para Giriş/Çıkış Barı */
    .para-bar-bg { width: 100%; height: 20px; background-color: #333; border-radius: 10px; overflow: hidden; margin-top: 5px; }
    .para-bar-fill { height: 100%; text-align: center; font-size: 12px; line-height: 20px; color: white; font-weight: bold; }
    
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 10px #FFD700; } 50% { box-shadow: 0 0 25px #FFA500; } 100% { box-shadow: 0 0 10px #FFD700; } }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 HDFGS & HİSSE RADARI (PARA AKIŞI)")

# --- TEK HİSSE DETAYLI ANALİZ (AKD SİMÜLASYONU) ---
st.sidebar.header("🔍 Detaylı Hisse Analizi")
secilen_hisse = st.sidebar.text_input("Hisse Kodu Gir (Örn: HDFGS)", "HDFGS").upper()
if ".IS" not in secilen_hisse: secilen_hisse += ".IS"

if st.sidebar.button("DETAYLI ANALİZ ET 🚀"):
    try:
        with st.spinner(f'{secilen_hisse} Para Akışı Hesaplanıyor...'):
            his_df = yf.download(secilen_hisse, period="1mo", interval="60m", progress=False)
            
            if hasattr(his_df.columns, 'levels'): his_df.columns = his_df.columns.get_level_values(0)
            
            if not his_df.empty:
                son_mum = his_df.iloc[-1]
                fiyat = son_mum['Close']
                
                # 1. PARA AKIŞI (MFI - Money Flow Index Hesabı)
                # Basitleştirilmiş mantık: Hacim * Fiyat değişimi
                typical_price = (his_df['High'] + his_df['Low'] + his_df['Close']) / 3
                money_flow = typical_price * his_df['Volume']
                
                # Son 14 periyotta pozitif ve negatif akışı ayır
                delta = typical_price.diff()
                positive_flow = money_flow.where(delta > 0, 0).rolling(14).sum().iloc[-1]
                negative_flow = money_flow.where(delta < 0, 0).rolling(14).sum().iloc[-1]
                
                mfi_ratio = positive_flow / negative_flow if negative_flow != 0 else 1
                mfi_index = 100 - (100 / (1 + mfi_ratio))
                
                # 2. SANAL DERİNLİK (Pivot Noktaları)
                pivot = (his_df['High'].iloc[-2] + his_df['Low'].iloc[-2] + his_df['Close'].iloc[-2]) / 3
                r1 = (2 * pivot) - his_df['Low'].iloc[-2]
                s1 = (2 * pivot) - his_df['High'].iloc[-2]
                
                # EKRANA YAZDIR
                st.sidebar.markdown("---")
                st.sidebar.subheader(f"📊 {secilen_hisse.replace('.IS','')} Raporu")
                st.sidebar.metric("Anlık Fiyat", f"{fiyat:.2f} TL")
                
                # Para Giriş/Çıkış Görseli
                if mfi_index > 50:
                    renk = "#059669" # Yeşil
                    durum = "PARA GİRİŞİ VAR 🟢"
                    genislik = mfi_index
                else:
                    renk = "#dc2626" # Kırmızı
                    durum = "PARA ÇIKIŞI VAR 🔴"
                    genislik = 100 - mfi_index
                
                st.sidebar.write(f"**Para Akışı:** {durum}")
                st.sidebar.markdown(f"""
                    <div class="para-bar-bg">
                        <div class="para-bar-fill" style="width: {mfi_index}%; background-color: {renk};">
                            MFI: {mfi_index:.0f}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.sidebar.markdown("---")
                st.sidebar.write("**Sanal Derinlik (Tahmini Emir Bölgeleri):**")
                st.sidebar.info(f"🧱 **DİRENÇ (Satıcı Bloğu):** {r1:.2f} TL")
                st.sidebar.warning(f"⚖️ **PİVOT (Denge):** {pivot:.2f} TL")
                st.sidebar.success(f"🛡️ **DESTEK (Alıcı Bloğu):** {s1:.2f} TL")
                
    except Exception as e:
        st.sidebar.error(f"Veri alınamadı: {e}")


# --- ANA EKRAN: HIZLI BALİNA TARAYICI ---
st.subheader("Genel Piyasa Taraması")

# LİSTE (HDFGS EN BAŞTA)
bist_listesi = [
    "HDFGS.IS", # 1 NUMARA
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", 
    "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", 
    "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS",
    "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS",
    "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS",
    "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"
]

@st.cache_data(ttl=60, show_spinner=False) # 1 Dakikada bir yenile (Çok hızlı olsun)
def verileri_getir():
    sinyaller = []
    toplam = len(bist_listesi)
    bar = st.progress(0, text="Piyasa Taranıyor...")
    
    for i, symbol in enumerate(bist_listesi):
        try:
            # Sadece bugünün verisini çek (En hızlı yöntem)
            df = yf.download(symbol, period="1d", interval="30m", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 5:
                son = df.iloc[-1]
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(10).mean().iloc[-1] # Son 10 mumun ortalaması
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
                
                durum = None
                renk = "gray"
                
                # --- HDFGS ÖZEL HASSAS AYAR (1.05 KAT) ---
                # Eğer HDFGS hacmi %5 bile artsa haber ver!
                if "HDFGS" in symbol:
                    if kat > 1.05: 
                        durum = "HDFGS CANLANDI! 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                    else:
                        # HDFGS sakin olsa bile listede görünsün
                        durum = "Takipte (Sakin)"
                        renk = "gray"
                
                # --- DİĞERLERİ (2 KAT) ---
                elif kat > 2.0:
                    if degisim > 0: durum = "ALIM GELİYOR 🚀"; renk = "buy"
                    else: durum = "SATIŞ BASKISI 🔻"; renk = "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "")
                    sinyaller.append({
                        "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim,
                        "HacimKat": kat, "Sinyal": durum, "Renk": renk
                    })
            
            time.sleep(0.01)
            bar.progress((i + 1) / toplam)

        except:
            continue
            
    bar.empty()
    return sinyaller

# Taramayı Çalıştır
zaman = datetime.now().strftime("%H:%M:%S")
st.caption(f"Son Tarama: {zaman}")

if st.button("YENİLE 🔄"):
    st.cache_data.clear()
    st.rerun()

sonuclar = verileri_getir()

if sonuclar:
    cols = st.columns(2)
    for i, veri in enumerate(sonuclar):
        with cols[i % 2]:
            ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
            
            st.markdown(f"""
            <div class="balina-karti bist-card {ozel}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4>
                        <p style="margin:0; font-size:15px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p>
                    </div>
                    <div style="text-align:right;">
                        <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                        <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
else:
    st.info("Veri alınamadı.")
