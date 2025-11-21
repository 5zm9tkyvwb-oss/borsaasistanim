import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Balina Avcısı PRO", layout="wide", page_icon="🦅")

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
    
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }

    /* Para Barı */
    .para-bar { width: 100%; height: 25px; background-color: #333; border-radius: 5px; margin-top: 5px; overflow: hidden; }
    .para-doluluk { height: 100%; text-align: center; line-height: 25px; font-size: 12px; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 BALİNA AVCISI & PRO ANALİZ")

# ==========================================
# SOL MENÜ: DETAYLI HİSSE ANALİZİ (AKD/DERİNLİK SİMÜLASYONU)
# ==========================================
with st.sidebar:
    st.header("🔍 Detaylı Analiz Masası")
    secilen_hisse = st.text_input("Hisse Kodu Gir:", "HDFGS").upper()
    if ".IS" not in secilen_hisse: secilen_hisse += ".IS"
    
    if st.button("ANALİZ ET 🚀"):
        try:
            with st.spinner("Hesaplamalar yapılıyor..."):
                # Veri Çek (1 Yıllık veri ile sağlam analiz)
                his_df = yf.download(secilen_hisse, period="3mo", interval="1d", progress=False)
                if hasattr(his_df.columns, 'levels'): his_df.columns = his_df.columns.get_level_values(0)
                
                if not his_df.empty:
                    son = his_df.iloc[-1]
                    fiyat = son['Close']
                    
                    # 1. SANAL DERİNLİK (PİVOT NOKTALARI)
                    # Pivot noktaları, profesyonel traderların "Görünmez Destek/Direnç" olarak kullandığı yerlerdir.
                    high = his_df['High'].iloc[-2] # Dünün en yükseği
                    low = his_df['Low'].iloc[-2]   # Dünün en düşüğü
                    close = his_df['Close'].iloc[-2] # Dünün kapanışı
                    
                    pivot = (high + low + close) / 3
                    r1 = (2 * pivot) - low  # Direnç 1
                    s1 = (2 * pivot) - high # Destek 1
                    
                    # 2. PARA GİRİŞ/ÇIKIŞ (MFI - Money Flow Index)
                    # Hacim ve Fiyatı harmanlayıp paranın yönünü bulur.
                    typical_price = (his_df['High'] + his_df['Low'] + his_df['Close']) / 3
                    raw_money_flow = typical_price * his_df['Volume']
                    
                    positive_flow = []
                    negative_flow = []
                    
                    for i in range(1, len(typical_price)):
                        if typical_price.iloc[i] > typical_price.iloc[i-1]:
                            positive_flow.append(raw_money_flow.iloc[i])
                            negative_flow.append(0)
                        elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                            positive_flow.append(0)
                            negative_flow.append(raw_money_flow.iloc[i])
                        else:
                            positive_flow.append(0)
                            negative_flow.append(0)
                            
                    pos_sum = sum(positive_flow[-14:]) # Son 14 gün
                    neg_sum = sum(negative_flow[-14:])
                    
                    mfi_ratio = pos_sum / neg_sum if neg_sum != 0 else 1
                    mfi = 100 - (100 / (1 + mfi_ratio))
                    
                    # --- SONUÇLARI YAZDIR ---
                    st.markdown("---")
                    st.metric("Anlık Fiyat", f"{fiyat:.2f} TL")
                    
                    # Para Göstergesi
                    st.write("**💰 Para Giriş/Çıkış Durumu (MFI)**")
                    renk = "#059669" if mfi > 50 else "#dc2626"
                    yazi = f"PARA GİRİŞİ VAR (%{mfi:.0f})" if mfi > 50 else f"PARA ÇIKIŞI VAR (%{mfi:.0f})"
                    
                    st.markdown(f"""
                        <div class="para-bar">
                            <div class="para-doluluk" style="width: {mfi}%; background-color: {renk};">
                                {yazi}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Sanal Derinlik Tablosu
                    st.markdown("---")
                    st.write("**🧱 Sanal Derinlik (Destek/Direnç)**")
                    st.error(f"DİRENÇ (Satıcı Bloğu): {r1:.2f} TL")
                    st.warning(f"PİVOT (Denge Noktası): {pivot:.2f} TL")
                    st.success(f"DESTEK (Alıcı Bloğu): {s1:.2f} TL")
                    
                    st.info("Not: Bu veriler matematiksel hesaplamadır. Gerçek kademe derinliği lisans gerektirir.")
                    
        except Exception as e:
            st.error(f"Hata: {e}")

# ==========================================
# ANA EKRAN: HIZLI LİSTE TARAMA
# ==========================================

# --- LİSTELER ---
bist_listesi = [
    "HDFGS.IS", # <--- 1 NUMARA
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
    "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", 
    "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", 
    "TCELL.IS", "ENKAI.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "PGSUS.IS", "KOZAL.IS", 
    "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS", "ALARK.IS", 
    "TAVHL.IS", "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS", "AKSEN.IS", 
    "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", 
    "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "BRSAN.IS", "CIMSA.IS", 
    "DOHOL.IS", "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS", "ISMEN.IS", 
    "KLSER.IS", "KORDS.IS", "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS", "SOKE.IS", 
    "TRGYO.IS", "TSPOR.IS", "ULKER.IS", "VESBE.IS", "YYLGD.IS", "ZOREN.IS"
]

kripto_listesi = [
    "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", 
    "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", 
    "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", 
    "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", 
    "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", 
    "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"
]

# --- ÖNBELLEKLİ TARAMA (HIZLI) ---
@st.cache_data(ttl=180, show_spinner=False)
def verileri_getir(liste, piyasa_tipi):
    sinyaller = []
    toplam = len(liste)
    bar = st.progress(0, text=f"{piyasa_tipi} Taranıyor...")
    
    for i, symbol in enumerate(liste):
        try:
            df = yf.download(symbol, period="2d", interval="1h", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 10:
                son = df.iloc[-1]
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                durum = None
                renk = "gray"
                
                if "HDFGS" in symbol:
                    if kat > 1.2: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy" if degisim > 0 else "sell"
                    else: durum = "HDFGS SAKİN"; renk = "gray"
                elif kat > 2.5:
                    if degisim > 0.5: durum = "WHALE BUY 🚀"; renk = "buy"
                    elif degisim < -0.5: durum = "WHALE DUMP 🔻"; renk = "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    sinyaller.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "HacimKat": kat, "Sinyal": durum, "Renk": renk})
            
            bar.progress((i + 1) / toplam)
            time.sleep(0.01)
        except: continue
            
    bar.empty()
    return sinyaller

# --- SAĞ TARAF (LİSTELER) ---
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO"])
zaman = datetime.now().strftime("%H:%M")

with tab1:
    st.caption(f"Son Güncelleme: {zaman}")
    sonuclar = verileri_getir(bist_listesi, "BIST")
    if st.button("🔄 Yenile (BIST)"): st.cache_data.clear(); st.rerun()
    
    if sonuclar:
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar):
            with cols[i % 2]:
                ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                st.markdown(f"""
                <div class="balina-karti bist-card {ozel}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p></div>
                        <div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p></div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else: st.info("BIST sakin.")

with tab2:
    st.caption("Kripto Piyasası")
    sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
    if st.button("🔄 Yenile (Kripto)"): st.cache_data.clear(); st.rerun()
    
    if sonuclar_kripto:
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar_kripto):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="balina-karti crypto-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div><h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p></div>
                        <div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p></div>
                    </div>
                </div>""", unsafe_allow_html=True)
    else: st.info("Kripto sakin.")
