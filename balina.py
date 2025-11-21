import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Balina Avcısı", layout="wide", page_icon="🧠")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    
    /* Kart Tasarımı */
    .balina-karti { 
        background-color: #111827; 
        padding: 15px; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Renk Kodları */
    .bist-card { border-left: 5px solid #38bdf8; } /* Mavi */
    .crypto-card { border-left: 5px solid #facc15; } /* Sarı */
    
    /* Etiketler */
    .tag {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: bold;
        margin-right: 5px;
    }
    .tag-vol { background-color: #4c1d95; color: #e9d5ff; } /* Mor Hacim */
    .tag-rsi { background-color: #be185d; color: #fbcfe8; } /* Pembe RSI */
    
    /* AI Kutusu */
    .ai-box {
        margin-top: 10px;
        background-color: #1f2937;
        padding: 10px;
        border-radius: 8px;
        border-left: 3px solid #10b981; /* Yeşil Çizgi */
        font-size: 13px;
        color: #d1d5db;
        font-style: italic;
    }

    /* HDFGS Özel Efekt */
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 AI DESTEKLİ BALİNA RADARI")
st.caption("Anlık Veri Analizi ve Otomatik Yorumlama Sistemi")

# --- HİSSE LİSTELERİ (Optimize Edilmiş) ---
bist_listesi = [
    "HDFGS.IS", # <--- KRAL EN BAŞTA
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

# --- SANAL YAPAY ZEKA MOTORU ---
def yapay_zeka_yorumu(symbol, degisim, kat, rsi):
    yorum = ""
    ikon = ""
    
    # HDFGS Özel Yorumu
    if "HDFGS" in symbol:
        if degisim > 0:
            return "🦅 **AI Analizi:** HDFGS kanatlanıyor! Hacim destekli yükseliş var, senin maliyetine (2.63) göre pozitif bölgedeyiz. Tutmaya devam edilebilir."
        else:
            return "🛡️ **AI Analizi:** HDFGS dinleniyor. Düşüş hacimsiz görünüyor, bu iyiye işaret. Panik yapma, destekleri izle."

    # Genel Algoritma
    if kat > 3.0:
        yorum += "Olağanüstü bir balina girişi var! Hacim patlamış durumda. "
    elif kat > 2.0:
        yorum += "Kurumsal alım/satım ilgisi yüksek. "
    
    if degisim > 2.0:
        yorum += "Fiyat momentumu çok güçlü, boğalar baskın. "
        ikon = "🚀"
    elif degisim < -2.0:
        yorum += "Satış baskısı çok sert, ayılar sahnede. "
        ikon = "🐻"
    
    if rsi > 75:
        yorum += "Ancak hisse teknik olarak 'Aşırı Alım' bölgesinde (RSI > 75). Kısa vadeli bir düzeltme (kar satışı) gelebilir."
    elif rsi < 25:
        yorum += "Hisse 'Aşırı Satım' bölgesinde (RSI < 25). Buradan tepki yükselişi gelmesi teknik olarak çok muhtemel."
    elif 45 < rsi < 55:
        yorum += "Kararsız bölge. Büyük bir kırılım için yön arıyor."
        
    if not yorum:
        yorum = "Yatay seyir izleniyor, hacim ortalama seviyelerde."
        
    return f"{ikon} **AI Analizi:** {yorum}"

# --- TARAMA MOTORU ---
@st.cache_data(ttl=120, show_spinner=False) # 2 Dakika Önbellek
def verileri_getir(liste, piyasa_tipi):
    sinyaller = []
    bar = st.progress(0, text=f"{piyasa_tipi} Analiz Ediliyor...")
    
    for i, symbol in enumerate(liste):
        try:
            # Yahoo'dan Veri Çek
            df = yf.download(symbol, period="2d", interval="1h", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 10:
                son = df.iloc[-1]
                
                # Veriler
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                fiyat = son['Close']
                acilis = df['Open'].iloc[-1] # Son mumun açılışı
                degisim = ((fiyat - acilis) / acilis) * 100
                
                # RSI
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]
                
                # --- FİLTRELEME ---
                goster = False
                
                # HDFGS ise her türlü göster
                if "HDFGS" in symbol:
                    goster = True
                
                # Diğerleri için: Hacim 2x VEYA Fiyat %1.5 oynamışsa VEYA RSI uçlardaysa göster
                elif kat > 2.0 or abs(degisim) > 1.5 or rsi < 30 or rsi > 70:
                    goster = True
                
                if goster:
                    # AI Yorumunu Oluştur
                    ai_mesaj = yapay_zeka_yorumu(symbol, degisim, kat, rsi)
                    
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    sinyaller.append({
                        "Sembol": isim,
                        "Fiyat": fiyat,
                        "Degisim": degisim,
                        "HacimKat": kat,
                        "RSI": rsi,
                        "AI": ai_mesaj
                    })
            
            time.sleep(0.01) # Anti-Ban
            bar.progress((i + 1) / len(liste))
        except:
            continue
            
    bar.empty()
    return sinyaller

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🏙️ BORSA İSTANBUL", "₿ KRİPTO"])

zaman = datetime.now().strftime("%H:%M")

with tab1:
    st.info(f"BIST Yapay Zeka Taraması (Son: {zaman})")
    if st.button("Analizi Yenile 🔄", key="bist_yenile"):
        st.cache_data.clear()
        st.rerun()
        
    sonuclar = verileri_getir(bist_listesi, "BIST")
    
    if sonuclar:
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar):
            with cols[i % 2]:
                ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                renk = "#4ade80" if veri['Degisim'] > 0 else "#f87171"
                
                st.markdown(f"""
                <div class="balina-karti bist-card {ozel}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h3>
                        <span style="font-size:18px; font-weight:bold; color:{renk};">
                            {veri['Fiyat']:.2f} TL (%{veri['Degisim']:.2f})
                        </span>
                    </div>
                    <div style="margin-top:10px;">
                        <span class="tag tag-vol">Hacim: {veri['HacimKat']:.1f}x</span>
                        <span class="tag tag-rsi">RSI: {veri['RSI']:.0f}</span>
                    </div>
                    <div class="ai-box">
                        {veri['AI']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("Piyasa şu an çok yatay, kayda değer bir anomali yok.")

with tab2:
    st.info(f"Kripto AI Analizi")
    if st.button("Analizi Yenile 🔄", key="kripto_yenile"):
        st.cache_data.clear()
        st.rerun()
        
    sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
    
    if sonuclar_kripto:
        cols = st.columns(2)
        for i, veri in enumerate(sonuclar_kripto):
            with cols[i % 2]:
                renk = "#4ade80" if veri['Degisim'] > 0 else "#f87171"
                
                st.markdown(f"""
                <div class="balina-karti crypto-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; color:#fef08a;">{veri['Sembol']}</h3>
                        <span style="font-size:18px; font-weight:bold; color:{renk};">
                            ${veri['Fiyat']:.4f} (%{veri['Degisim']:.2f})
                        </span>
                    </div>
                    <div style="margin-top:10px;">
                        <span class="tag tag-vol">Hacim: {veri['HacimKat']:.1f}x</span>
                        <span class="tag tag-rsi">RSI: {veri['RSI']:.0f}</span>
                    </div>
                    <div class="ai-box">
                        {veri['AI']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Kripto tarafı sakin.")
