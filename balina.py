import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Balina Avcısı PRO", layout="wide", page_icon="🦅")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 BALİNA AVCISI & GRAFİK MERKEZİ")

# ==========================================
# 1. DETAYLI GRAFİK ANALİZİ (ÜST BÖLÜM)
# ==========================================
with st.container():
    st.markdown("### 🔍 Detaylı Hisse/Coin Analizi (Destek-Direnç Çizimli)")
    col_input, col_btn = st.columns([3, 1])
    
    with col_input:
        secilen_varlik = st.text_input("İncelenecek Varlık Kodu:", "HDFGS.IS").upper()
    with col_btn:
        st.write("") # Hizalama boşluğu
        st.write("") 
        analiz_et = st.button("GRAFİK ÇİZ 📈", type="primary")

    if analiz_et:
        try:
            with st.spinner("Grafik çiziliyor ve seviyeler hesaplanıyor..."):
                # Veri Çek
                df_grafik = yf.download(secilen_varlik, period="6mo", interval="1d", progress=False)
                if hasattr(df_grafik.columns, 'levels'): df_grafik.columns = df_grafik.columns.get_level_values(0)
                
                if not df_grafik.empty:
                    son_fiyat = df_grafik['Close'].iloc[-1]
                    
                    # PİVOT HESABI (Destek/Direnç)
                    high = df_grafik['High'].iloc[-2]
                    low = df_grafik['Low'].iloc[-2]
                    close = df_grafik['Close'].iloc[-2]
                    
                    pivot = (high + low + close) / 3
                    r1 = (2 * pivot) - low  # Direnç
                    s1 = (2 * pivot) - high # Destek
                    
                    # GRAFİK OLUŞTUR (Plotly)
                    fig = go.Figure()
                    
                    # Mum Grafiği
                    fig.add_trace(go.Candlestick(
                        x=df_grafik.index,
                        open=df_grafik['Open'], high=df_grafik['High'],
                        low=df_grafik['Low'], close=df_grafik['Close'],
                        name="Fiyat"
                    ))
                    
                    # Destek Çizgisi (Yeşil)
                    fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"GÜÇLÜ DESTEK: {s1:.2f}", annotation_position="bottom right")
                    
                    # Direnç Çizgisi (Kırmızı)
                    fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"GÜÇLÜ DİRENÇ: {r1:.2f}", annotation_position="top right")
                    
                    # Pivot (Sarı)
                    fig.add_hline(y=pivot, line_dash="dot", line_color="yellow", annotation_text="PİVOT", annotation_position="right")

                    # Grafik Ayarları
                    fig.update_layout(
                        title=f"{secilen_varlik} Analiz Grafiği",
                        yaxis_title="Fiyat",
                        xaxis_rangeslider_visible=False,
                        template="plotly_dark",
                        height=500
                    )
                    
                    # Ekrana Bas
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Yorum
                    col_res1, col_res2, col_res3 = st.columns(3)
                    col_res1.metric("Anlık Fiyat", f"{son_fiyat:.2f}")
                    col_res2.metric("Destek (Alım)", f"{s1:.2f}", delta_color="normal")
                    col_res3.metric("Direnç (Satım)", f"{r1:.2f}", delta_color="inverse")
                    
                else:
                    st.error("Veri bulunamadı.")
        except Exception as e:
            st.error(f"Hata: {e}")

st.divider()

# ==========================================
# 2. GENEL PİYASA TARAMASI (ALT BÖLÜM)
# ==========================================
st.subheader("🌊 Piyasa Taraması (Balina Avı)")

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

# --- ÖNBELLEKLİ TARAMA ---
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

# --- TARAMA ARAYÜZÜ ---
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
