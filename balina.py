import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Global Balina Avcısı", layout="wide", page_icon="🐳")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .balina-karti { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 5px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 5px solid #facc15; }
    .signal-box { padding: 5px 10px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 14px; }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; }
    </style>
""", unsafe_allow_html=True)

st.title("🐳 ULTRA BALİNA AVCISI PRO")
st.caption("HDFGS • BIST 100 • KRİPTO SEKTÖRLERİ")

# --- VERİ HAVUZLARI ---

# BIST LİSTESİ
bist_listesi = [
    "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", 
    "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", 
    "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS",
    "SAHOL.IS", "TCELL.IS", "ENKAI.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "PGSUS.IS",
    "KOZAL.IS", "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS",
    "ALARK.IS", "TAVHL.IS", "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS",
    "AKSEN.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS",
    "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"
]

# KRİPTO KATEGORİLERİ
crypto_sectors = {
    "🏆 Top 30 (Major)": [
        "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "AVAX-USD", 
        "DOGE-USD", "DOT-USD", "TRX-USD", "LINK-USD", "MATIC-USD", "LTC-USD", "BCH-USD",
        "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "FIL-USD", "HBAR-USD", "APT-USD",
        "NEAR-USD", "VET-USD", "ICP-USD", "ARB-USD", "OP-USD", "INJ-USD", "RNDR-USD"
    ],
    "🐸 Meme Coinler": [
        "DOGE-USD", "SHIB-USD", "PEPE-USD", "FLOKI-USD", "BONK-USD", "WIF-USD", 
        "BOME-USD", "MEME-USD", "DOGE2-USD", "BabyDoge-USD"
    ],
    "🤖 Yapay Zeka (AI)": [
        "FET-USD", "RNDR-USD", "AGIX-USD", "OCEAN-USD", "GRT-USD", "WLD-USD", 
        "NEAR-USD", "INJ-USD", "ROSE-USD", "AKT-USD"
    ],
    "🎮 Metaverse & Game": [
        "SAND-USD", "MANA-USD", "AXS-USD", "GALA-USD", "ENJ-USD", "APE-USD", 
        "IMX-USD", "FLOW-USD", "CHZ-USD", "GMT-USD"
    ],
    "🏦 DeFi & Layer 2": [
        "UNI-USD", "AAVE-USD", "MKR-USD", "SNX-USD", "CRV-USD", "LDO-USD", 
        "COMP-USD", "1INCH-USD", "DYDX-USD", "SUSHI-USD", "CAKE-USD"
    ]
}

# --- TARAMA FONKSİYONU ---
def tarama_yap(liste, piyasa_tipi):
    sinyaller = []
    text = "BIST Piyasası Taranıyor..." if piyasa_tipi == "BIST" else "Seçilen Kripto Sektörü Taranıyor..."
    my_bar = st.progress(0, text=text)
    
    adim = 1.0 / len(liste)
    suan = 0.0

    for symbol in liste:
        try:
            time.sleep(0.05) # Hızlandırdım ama güvenli sınırda
            period = "5d" if piyasa_tipi == "BIST" else "2d"
            df = yf.download(symbol, period=period, interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son = df.iloc[-1]
                
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(24).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                durum = None
                renk = "gray"
                
                # HDFGS Kuralı
                if "HDFGS" in symbol:
                    if kat > 1.5:
                        durum = "HDFGS HAREKETLİ 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                
                # Genel Kural
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
                        "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim,
                        "HacimKat": kat, "Sinyal": durum, "Renk": renk
                    })
        except:
            pass
        
        suan += adim
        my_bar.progress(min(suan, 1.0), text=f"{symbol} taranıyor...")
    
    my_bar.empty()
    return sinyaller

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO (SEKTÖREL)"])

# --- SEKME 1: BORSA ---
with tab1:
    st.header("BIST 100 Balina Radarı")
    st.caption(f"Listedeki {len(bist_listesi)} hisse taranıyor.")
    
    if st.button("BIST'i BAŞLAT 📡", key="btn_bist", type="primary"):
        sonuclar = tarama_yap(bist_listesi, "BIST")
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    st.markdown(f"""
                    <div class="balina-karti bist-card {ozel}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("BIST sakin.")

# --- SEKME 2: KRİPTO ---
with tab2:
    st.header("Kripto Sektör Tarayıcısı")
    
    # Kategori Seçimi
    secilen_sektor = st.selectbox("Hangi Sektörü Tarayalım?", list(crypto_sectors.keys()))
    
    # Seçilen listeyi al
    tarama_listesi = crypto_sectors[secilen_sektor]
    
    st.caption(f"Seçilen sektördeki {len(tarama_listesi)} coin taranacak.")
    
    if st.button("KRİPTOYU TARA 📡", key="btn_kripto", type="primary"):
        sonuclar = tarama_yap(tarama_listesi, "KRIPTO")
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="balina-karti crypto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#fef08a;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Bu sektörde şu an balina hareketi yok.")
