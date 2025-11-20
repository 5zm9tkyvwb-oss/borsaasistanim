import streamlit as st
import yfinance as yf
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Global Balina Avcısı", layout="wide", page_icon="🐳")

# --- CSS TASARIMI (Sekmeler ve Kartlar) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    
    /* Sekme Tasarımı */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px;
        background-color: #1f2937;
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #38bdf8 !important;
        color: black !important;
    }

    /* Balina Kartı */
    .balina-karti {
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #374151;
    }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 5px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 5px solid #facc15; }
    
    .signal-box {
        padding: 8px 15px;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    .buy { background-color: #059669; color: white; box-shadow: 0 0 10px #059669; }
    .sell { background-color: #dc2626; color: white; box-shadow: 0 0 10px #dc2626; }
    </style>
""", unsafe_allow_html=True)

st.title("🐳 Global Balina Avcısı")
st.caption("Borsa İstanbul & Binance Hacim Tarayıcısı")

# --- HİSSE VE COIN LİSTELERİ ---
hisseler = [
    "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", 
    "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", 
    "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS",
    "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS"
]

kriptolar = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD",
    "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD",
    "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD",
    "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD"
]

# --- TARAMA FONKSİYONU ---
def tarama_yap(liste, piyasa_tipi):
    sinyaller = []
    progress_text = "BIST Taranıyor..." if piyasa_tipi == "BIST" else "Binance Taranıyor..."
    my_bar = st.progress(0, text=progress_text)
    
    adim = 1.0 / len(liste)
    suan = 0.0

    for symbol in liste:
        try:
            # Veri Çek (Kripto 7/24 olduğu için son 2 gün yeterli)
            period = "5d" if piyasa_tipi == "BIST" else "2d"
            df = yf.download(symbol, period=period, interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son = df.iloc[-1]
                
                # 1. Hacim Patlaması
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(24).mean().iloc[-1] # 24 saatlik ortalama
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                # 2. Fiyat Değişimi
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                # Sinyal Mantığı
                durum = None
                
                # Kriter: Hacim 2.5 katına çıkmışsa BALİNA VARDIR
                if kat > 2.5:
                    if degisim > 0.5:
                        durum = "WHALE BUY 🚀"
                        renk = "buy"
                    elif degisim < -0.5:
                        durum = "WHALE DUMP 🔻"
                        renk = "sell"
                
                if durum:
                    # Temiz isim (IS ve USD sil)
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
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO (BINANCE)"])

# --- SEKME 1: BORSA ---
with tab1:
    st.header("BIST 30 Balina Radarı")
    if st.button("BIST'i Tara 📡", key="btn_bist", type="primary"):
        sonuclar = tarama_yap(hisseler, "BIST")
        
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Hareketi Tespit Edildi!")
            for veri in sonuclar:
                st.markdown(f"""
                <div class="balina-karti bist-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h2 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h2>
                            <p style="margin:0; font-size:20px; color:white;">{veri['Fiyat']:.2f} TL 
                                <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">
                                (%{veri['Degisim']:.2f})
                                </span>
                            </p>
                        </div>
                        <div style="text-align:right;">
                            <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                            <p style="margin:5px 0 0 0; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f} Kat Arttı</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("BIST tarafı şu an sakin. Balinalar uyuyor.")

# --- SEKME 2: KRİPTO ---
with tab2:
    st.header("Binance Balina Radarı")
    st.caption("Bitcoin, Ethereum, Solana, PEPE ve popüler coinler taranıyor...")
    
    if st.button("Kripto Piyasasını Tara 📡", key="btn_kripto", type="primary"):
        sonuclar = tarama_yap(kriptolar, "KRIPTO")
        
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Hareketi Tespit Edildi!")
            for veri in sonuclar:
                st.markdown(f"""
                <div class="balina-karti crypto-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h2 style="margin:0; color:#fef08a;">{veri['Sembol']}</h2>
                            <p style="margin:0; font-size:20px; color:white;">${veri['Fiyat']:.4f} 
                                <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">
                                (%{veri['Degisim']:.2f})
                                </span>
                            </p>
                        </div>
                        <div style="text-align:right;">
                            <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                            <p style="margin:5px 0 0 0; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f} Kat Arttı</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Kripto tarafı şu an sakin. Hacimler normal seyrediyor.")

# --- BİLGİ NOTU ---
st.divider()
with st.expander("ℹ️ Balina Avcısı Nasıl Çalışır?"):
    st.markdown("""
    Bu algoritma, piyasadaki **anormal hacim hareketlerini** tespit eder.
    * **Hacim Patlaması:** Bir coinin veya hissenin o saatlik hacmi, son 24 saatin ortalamasının **2.5 katına** çıkarsa radar öter.
    * **Whale Buy:** Hacim artarken fiyat da artıyorsa, büyük bir oyuncu alım yapıyor demektir.
    * **Whale Dump:** Hacim artarken fiyat sert düşüyorsa, panik satış veya yüklü çıkış var demektir.
    """)
