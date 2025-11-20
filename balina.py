import streamlit as st
import yfinance as yf
import pandas as pd
import time # Nefes almak için kütüphane

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Global Balina Avcısı", layout="wide", page_icon="🐳")

# --- CSS ---
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

st.title("🐳 ULTRA BALİNA AVCISI (GENİŞLETİLMİŞ)")
st.caption("HDFGS • BIST 100+ • KRİPTO")

# --- DEV HİSSE LİSTESİ (120+ ADET) ---
# 600 hisse sistemi kitler, bu liste hacmin %90'ıdır.
hisseler = [
    "HDFGS.IS", # <--- 1 NUMARA
    # BIST 30
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
    "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", 
    "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", 
    "TCELL.IS", "ENKAI.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "PGSUS.IS", "KOZAL.IS", 
    "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS", "ALARK.IS", 
    "TAVHL.IS", 
    # POPÜLER BIST 100 & YILDIZ PAZAR
    "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS", "AKSEN.IS", "ASTOR.IS", 
    "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", 
    "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "BRSAN.IS", "CIMSA.IS", "DOHOL.IS", 
    "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS", "ISMEN.IS", "KLSER.IS", 
    "KORDS.IS", "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS", "SOKE.IS", "TRGYO.IS", 
    "TSPOR.IS", "ULKER.IS", "VESBE.IS", "YYLGD.IS", "ZOREN.IS", "AKFGY.IS", "ALBRK.IS",
    "ASGYO.IS", "AYDEM.IS", "BAGFS.IS", "BERA.IS", "BIOEN.IS", "BOBET.IS", "BRYAT.IS",
    "CCOLA.IS", "CEMTS.IS", "CWENE.IS", "ECZYT.IS", "GENIL.IS", "GSDHO.IS", "HALKS.IS",
    "HUNER.IS", "IHLAS.IS", "IMASM.IS", "IZMDC.IS", "KARSN.IS", "KMPUR.IS", "KONYA.IS",
    "KOPOL.IS", "MAGEN.IS", "MTRKS.IS", "NTHOL.IS", "PENTA.IS", "PSGYO.IS", "SDTTR.IS",
    "SELEC.IS", "SNGYO.IS", "TATGD.IS", "TUKAS.IS", "TURSG.IS", "VERUS.IS", "YEOTK.IS"
]

kriptolar = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", 
    "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", 
    "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", 
    "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", 
    "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", 
    "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"
]

# --- TARAMA FONKSİYONU ---
def tarama_yap(liste, piyasa_tipi):
    sinyaller = []
    text = "BIST Piyasası Taranıyor (Ort. 60-90 sn)..." if piyasa_tipi == "BIST" else "Kripto Taranıyor..."
    my_bar = st.progress(0, text=text)
    
    adim = 1.0 / len(liste)
    suan = 0.0

    for symbol in liste:
        try:
            # Yahoo'yu kızdırmamak için minik bekleme (Anti-Ban)
            time.sleep(0.1) 
            
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
                
                # HDFGS Özel Kuralı
                if "HDFGS" in symbol:
                    if kat > 1.5:
                        durum = "HDFGS HAREKETLİ 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                
                # Diğerleri için filtre
                elif kat > 2.3: # Hacim 2.3 kat artmalı
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
        my_bar.progress(min(suan, 1.0), text=f"{symbol} kontrol ediliyor...")
    
    my_bar.empty()
    return sinyaller

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🏙️ BORSA (120+ HİSSE)", "₿ KRİPTO"])

with tab1:
    st.header(f"Borsa İstanbul Geniş Tarama")
    if st.button("GENİŞ TARAMAYI BAŞLAT 📡", key="btn_bist", type="primary"):
        sonuclar = tarama_yap(hisseler, "BIST")
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
            st.info("Tarama bitti. Şu an olağandışı bir hacim yok.")

with tab2:
    st.header(f"Kripto Tarama")
    if st.button("KRİPTOYU TARA 📡", key="btn_kripto", type="primary"):
        sonuclar = tarama_yap(kriptolar, "KRIPTO")
        if sonuclar:
            st.success(f"{len(sonuclar)} Kripto Balinası Yakalandı!")
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
            st.info("Kripto sakin.")
