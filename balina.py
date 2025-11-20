import streamlit as st
import yfinance as yf
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Global Balina Avcısı", layout="wide", page_icon="🐳")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 10px; background-color: #1f2937; color: white; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: black !important; }
    .balina-karti { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 5px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 5px solid #facc15; }
    .signal-box { padding: 5px 10px; border-radius: 6px; font-weight: bold; text-align: center; display: inline-block; font-size: 14px; }
    .buy { background-color: #059669; color: white; box-shadow: 0 0 10px #059669; }
    .sell { background-color: #dc2626; color: white; box-shadow: 0 0 10px #dc2626; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; } /* HDFGS'ye özel altın çerçeve */
    </style>
""", unsafe_allow_html=True)

st.title("🐳 ULTRA BALİNA AVCISI")
st.caption("HDFGS • BIST 100 • KRİPTO")

# --- LİSTELER (HDFGS EN BAŞTA!) ---

hisseler = [
    "HDFGS.IS", # <--- SENİN HİSSEN (1 NUMARA)
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", 
    "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", 
    "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", 
    "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "TCELL.IS", "ENKAI.IS", "VESTL.IS", 
    "ARCLK.IS", "TOASO.IS", "PGSUS.IS", "KOZAL.IS", "KOZAA.IS", "IPEKE.IS", 
    "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS", "ALARK.IS", "TAVHL.IS", 
    "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS", "AKSEN.IS", 
    "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS",
    "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"
]

kriptolar = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", 
    "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", 
    "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", 
    "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", 
    "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", 
    "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD",
    "MANA-USD", "AXS-USD", "EOS-USD", "XTZ-USD", "THETA-USD", "FTM-USD",
    "WIF-USD", "BONK-USD", "BOME-USD" # Yeni popüler meme coinler
]

# --- TARAMA FONKSİYONU ---
def tarama_yap(liste, piyasa_tipi):
    sinyaller = []
    text = "HDFGS ve Borsa Taranıyor..." if piyasa_tipi == "BIST" else "Kripto Piyasası Taranıyor..."
    my_bar = st.progress(0, text=text)
    
    adim = 1.0 / len(liste)
    suan = 0.0

    for symbol in liste:
        try:
            period = "5d" if piyasa_tipi == "BIST" else "2d"
            df = yf.download(symbol, period=period, interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son = df.iloc[-1]
                
                # 1. Hacim Patlaması
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(24).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                # 2. Fiyat Değişimi
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                # Sinyal Mantığı (HDFGS için her durumu gösterelim, diğerleri için filtreli)
                durum = None
                renk = "gray"
                
                if "HDFGS" in symbol: # HDFGS ise küçük harekette bile haber ver
                    if kat > 1.5:
                        durum = "HDFGS HAREKETLİ 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                
                # Diğer hisseler için katı kural (2.2 kat hacim)
                elif kat > 2.2:
                    if degisim > 0.5:
                        durum = "WHALE BUY 🚀"
                        renk = "buy"
                    elif degisim < -0.5:
                        durum = "WHALE DUMP 🔻"
                        renk = "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    sinyaller.append({
                        "Sembol": isim,
                        "Fiyat": fiyat,
                        "Degisim": degisim,
                        "HacimKat": kat,
                        "Sinyal": durum,
                        "Renk": renk
                    })
        except:
            pass
        
        suan += adim
        my_bar.progress(min(suan, 1.0), text=f"{symbol} taranıyor...")
    
    my_bar.empty()
    return sinyaller

# --- SEKMELER ---
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO"])

# --- SEKME 1: BORSA ---
with tab1:
    st.header(f"BIST {len(hisseler)} Hisse Taranıyor")
    if st.button("BIST RADARI 📡", key="btn_bist", type="primary"):
        sonuclar = tarama_yap(hisseler, "BIST")
        
        if sonuclar:
            st.success(f"{len(sonuclar)} Sinyal Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    # HDFGS ise özel altın çerçeveli kart yap
                    ozel_class = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    
                    st.markdown(f"""
                    <div class="balina-karti bist-card {ozel_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px; color:white;">{veri['Fiyat']:.2f} TL 
                                    <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">
                                    (%{veri['Degisim']:.2f})
                                    </span>
                                </p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Piyasa sakin. HDFGS veya Balinalarda ani hareket yok.")

# --- SEKME 2: KRİPTO ---
with tab2:
    st.header(f"Binance {len(kriptolar)} Coin Taranıyor")
    if st.button("KRİPTO RADARI 📡", key="btn_kripto", type="primary"):
        sonuclar = tarama_yap(kriptolar, "KRIPTO")
        
        if sonuclar:
            st.success(f"{len(sonuclar)} Sinyal Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="balina-karti crypto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#fef08a;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px; color:white;">${veri['Fiyat']:.4f} 
                                    <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">
                                    (%{veri['Degisim']:.2f})
                                    </span>
                                </p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Kripto tarafı sakin.")
