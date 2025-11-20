import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Hızlı Balina Avcısı", layout="wide", page_icon="⚡")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #1f2937; color: white; border-radius: 8px; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: black !important; }
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 10px #FFD700; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ HIZLI BALİNA AVCISI")
st.caption("HDFGS • BIST TÜM • KRİPTO | Akıllı Önbellek Sistemi Aktif")

# --- LİSTELER ---
bist_listesi = [
    "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", 
    "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", 
    "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS",
    "SAHOL.IS", "TCELL.IS", "ENKAI.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "PGSUS.IS",
    "KOZAL.IS", "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS",
    "ALARK.IS", "TAVHL.IS", "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS",
    "AKSEN.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS",
    "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "BRSAN.IS",
    "CIMSA.IS", "DOHOL.IS", "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS",
    "ISMEN.IS", "KLSER.IS", "KORDS.IS", "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS",
    "SOKE.IS", "TRGYO.IS", "TSPOR.IS", "ULKER.IS", "VESBE.IS", "YYLGD.IS", "ZOREN.IS"
    # Liste çok uzamasın diye en hacimli 80 taneyi tuttum, hız için optimize ettim.
]

kripto_listesi = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", 
    "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", 
    "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", 
    "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", 
    "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", 
    "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"
]

# --- AKILLI TARAMA (CACHE SİSTEMİ) ---
# Bu fonksiyonun sonucu 300 saniye (5 dakika) boyunca hafızada tutulur.
# Tekrar tıklandığında indirme yapmaz, hafızadan getirir.
@st.cache_data(ttl=300, show_spinner=False)
def verileri_getir(liste, piyasa_tipi):
    sinyaller = []
    toplam = len(liste)
    
    # İlerleme çubuğu sadece ilk yüklemede çalışır
    bar = st.progress(0, text=f"{piyasa_tipi} Verileri İndiriliyor... (İlk açılışta yavaş olabilir)")
    
    for i, symbol in enumerate(liste):
        try:
            # Hızlandırma: Sadece son 2 günlük veriyi çek (Yeterli)
            df = yf.download(symbol, period="2d", interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 10:
                son = df.iloc[-1]
                hacim_son = son['Volume']
                # Son 24 mumun ortalaması
                hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                durum = None
                renk = "gray"
                
                # HDFGS Özel
                if "HDFGS" in symbol:
                    if kat > 1.5:
                        durum = "HDFGS HAREKETLİ 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                
                # Diğerleri (Filtre 2.3x)
                elif kat > 2.3:
                    if degisim > 0.5: durum = "WHALE BUY 🚀"; renk = "buy"
                    elif degisim < -0.5: durum = "WHALE DUMP 🔻"; renk = "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    sinyaller.append({
                        "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim,
                        "HacimKat": kat, "Sinyal": durum, "Renk": renk
                    })
            
            # Barı güncelle
            bar.progress((i + 1) / toplam)
            time.sleep(0.02) # Küçük bekleme (Yahoo engellememesi için)

        except:
            continue
            
    bar.empty()
    return sinyaller

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO"])

zaman = datetime.now().strftime("%H:%M")

with tab1:
    st.info(f"BIST verileri önbellekten getiriliyor. (Son Güncelleme: {zaman})")
    
    # Butona gerek yok, açılır açılmaz getirsin (Otomatik)
    sonuclar = verileri_getir(bist_listesi, "BIST")
    
    if st.button("🔄 Verileri Şimdi Yenile (BIST)"):
        st.cache_data.clear() # Önbelleği temizle ve yeniden çek
        st.rerun()
        
    if sonuclar:
        st.success(f"{len(sonuclar)} Balina Hareketi Var!")
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar):
            with cols[i % 2]:
                ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                st.markdown(f"""
                <div class="balina-karti bist-card {ozel}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4>
                            <p style="margin:0; font-size:14px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                        </div>
                        <div style="text-align:right;">
                            <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                            <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("BIST şu an sakin.")

with tab2:
    st.info(f"Kripto verileri taranıyor...")
    sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
    
    if st.button("🔄 Verileri Şimdi Yenile (Kripto)"):
        st.cache_data.clear()
        st.rerun()

    if sonuclar_kripto:
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar_kripto):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="balina-karti crypto-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4>
                            <p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                        </div>
                        <div style="text-align:right;">
                            <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                            <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("Kripto sakin.")
