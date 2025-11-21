import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import random
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="NEON TRADER PRO", layout="wide", page_icon="⚡")

# --- VERİTABANI SİSTEMİ ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"loglar": [], "portfoy": []}} # Basit DB
        save_db(default_db); return default_db
    try: with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- ULTRA NEON CSS TASARIMI ---
st.markdown("""
    <style>
    /* GENEL ARKAPLAN */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #1a0b2e 0%, #000000 100%);
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    
    /* BAŞLIKLAR */
    h1, h2, h3 {
        color: #00f2ff !important; /* Neon Mavi */
        text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff;
        font-weight: bold;
    }
    
    /* INPUT ALANLARI */
    .stTextInput input, .stNumberInput input {
        background-color: #0f0f1a !important;
        color: #00f2ff !important;
        border: 1px solid #bd00ff !important; /* Neon Mor Çerçeve */
        border-radius: 8px;
        box-shadow: 0 0 5px #bd00ff;
    }
    
    /* BUTONLAR */
    div.stButton > button {
        background: linear-gradient(45deg, #210046, #bd00ff);
        color: white !important;
        border: 1px solid #00f2ff !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        height: 50px !important;
        width: 100% !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #00f2ff, #0038ff);
        box-shadow: 0 0 20px #00f2ff;
        transform: scale(1.02);
        border: 1px solid white !important;
    }
    
    /* KARTLAR */
    .balina-karti {
        background-color: rgba(20, 20, 35, 0.9);
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .bist-card { border-left: 4px solid #00f2ff; } /* Mavi */
    .crypto-card { border-left: 4px solid #bd00ff; } /* Mor */
    
    /* SİNYAL KUTULARI */
    .signal-box { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #00ff41; color: black; box-shadow: 0 0 10px #00ff41; }
    .sell { background-color: #ff003c; color: white; box-shadow: 0 0 10px #ff003c; }
    
    /* HDFGS ÖZEL EFEKT */
    .hdfgs-ozel {
        border: 2px solid #00f2ff;
        box-shadow: 0 0 30px rgba(0, 242, 255, 0.4);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(0, 242, 255, 0.4); }
        50% { box-shadow: 0 0 30px rgba(0, 242, 255, 0.8); }
        100% { box-shadow: 0 0 10px rgba(0, 242, 255, 0.4); }
    }
    
    /* LOGO STICKER */
    .neon-sticker {
        position: fixed; top: 20px; right: 20px;
        background: rgba(0,0,0,0.8);
        border: 2px solid #00f2ff;
        color: #00f2ff;
        padding: 10px 20px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        z-index: 9999;
        box-shadow: 0 0 15px #00f2ff;
        transform: rotate(5deg);
        backdrop-filter: blur(5px);
    }
    </style>
    <div class="neon-sticker">
        <span style="font-size:24px">⚡</span><br>PALA<br>TERMINAL
    </div>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][0]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
    except: pass

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- GRAFİK MOTORU ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            prev = df.iloc[-2]; pivot = (prev['High']+prev['Low']+prev['Close'])/3
            r1=(2*pivot)-prev['Low']; s1=(2*pivot)-prev['High']
            
            fig = go.Figure()
            # Mum Grafiği (Neon Renkler)
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                         increasing_line_color='#00ff41', decreasing_line_color='#ff003c', name="Fiyat"))
            
            fig.add_hline(y=r1, line_dash="dash", line_color="#ff003c", annotation_text="DİRENÇ", annotation_font_color="#ff003c")
            fig.add_hline(y=s1, line_dash="dash", line_color="#00ff41", annotation_text="DESTEK", annotation_font_color="#00ff41")
            
            fig.update_layout(
                title=f"{symbol} NEON ANALİZ", template="plotly_dark", height=500, 
                xaxis_rangeslider_visible=False, 
                plot_bgcolor='#050505', paper_bgcolor='#050505',
                font=dict(family="Courier New, monospace", size=12, color="#00f2ff")
            )
            
            news = []
            try:
                n = yf.Ticker(symbol).news
                for i in n[:3]: news.append(f"📰 [{i['title']}]({i['link']})")
            except: pass
            return fig, df.iloc[-1]['Close'], s1, r1, news
    except: return None, None, None, None, None

# ==========================================
# ANA UYGULAMA
# ==========================================

# Başlık
col_head = st.columns([8, 2])
with col_head[0]:
    st.title("⚡ PALA NEON TERMINAL")
    st.caption("HDFGS • BIST • KRİPTO | Ücretsiz Erişim")

# Admin Gizli Butonu (Sidebar'da)
if st.sidebar.checkbox("Admin Modu"):
    st.sidebar.title("👑 ADMİN PANELİ")
    db = load_db()
    if st.sidebar.button("Logları Temizle"):
        db["admin"]["loglar"] = []
        save_db(db)
        st.sidebar.success("Temizlendi")

# MENÜ
menu = st.radio("NAVİGASYON:", ["📊 RADAR", "💼 CÜZDAN", "🔥 ISI HARİTASI", "📒 LOGLAR", "🩻 RÖNTGEN", "⚔️ DÜELLO"], horizontal=True)
st.divider()

# --- MODÜL: CÜZDAN ---
if menu == "💼 CÜZDAN":
    st.subheader("💰 Varlık Yönetimi")
    db = load_db()
    with st.expander("➕ Hisse Ekle"):
        c1, c2, c3, c4 = st.columns(4)
        y_sem = c1.text_input("Sembol", "HDFGS.IS").upper()
        y_mal = c2.number_input("Maliyet", value=2.63)
        y_adt = c3.number_input("Adet", value=194028)
        if c4.button("KAYDET"):
            if "portfoy" not in db["admin"]: db["admin"]["portfoy"] = []
            # Eski kaydı sil, yeniyi ekle
            db["admin"]["portfoy"] = [p for p in db["admin"]["portfoy"] if p['sembol'] != y_sem]
            db["admin"]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
            save_db(db); st.success("Kaydedildi!"); st.rerun()

    if "portfoy" in db["admin"] and db["admin"]["portfoy"]:
        total_val = 0; total_profit = 0; data_pie = []; table_data = []
        for p in db["admin"]["portfoy"]:
            try:
                fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                val = fiyat * p['adet']; profit = (fiyat - p['maliyet']) * p['adet']
                total_val += val; total_profit += profit
                table_data.append({"Hisse": p['sembol'], "Fiyat": f"{fiyat:.2f}", "Kar": f"{profit:,.0f}"})
                data_pie.append({"Sembol": p['sembol'], "Deger": val})
            except: pass
        
        k1, k2 = st.columns(2)
        k1.metric("TOPLAM SERVET", f"{total_val:,.0f} TL")
        k2.metric("NET KAR", f"{total_profit:,.0f} TL", delta_color="normal")
        
        c_pie, c_tab = st.columns([1, 2])
        with c_pie:
            if data_pie:
                fig_pie = px.pie(pd.DataFrame(data_pie), values='Deger', names='Sembol', hole=0.5)
                fig_pie.update_traces(textinfo='label+percent', textfont_size=14, marker=dict(line=dict(color='#000000', width=2)))
                fig_pie.update_layout(template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
        with c_tab: st.table(pd.DataFrame(table_data))
        
        sil = st.selectbox("Sil:", [p['sembol'] for p in db["admin"]["portfoy"]])
        if st.button("HİSSEYİ SİL"):
            db["admin"]["portfoy"] = [p for p in db["admin"]["portfoy"] if p['sembol'] != sil]; save_db(db); st.rerun()
    else: st.info("Cüzdan boş.")

# --- MODÜL: RADAR ---
elif menu == "📊 RADAR":
    c_s1, c_s2 = st.columns([3, 1])
    arama = c_s1.text_input("Hisse/Coin Ara:", placeholder="HDFGS...").upper()
    if c_s2.button("ANALİZ ET 🚀"):
        sym = f"{arama}.IS" if "-" not in arama and ".IS" not in arama and "USD" not in arama else arama
        st.session_state.secilen_hisse = sym; st.rerun()

    if st.session_state.secilen_hisse:
        with st.spinner("İnceleniyor..."):
            fig, fiyat, s1, r1, news = grafik_ciz(st.session_state.secilen_hisse)
            if fig:
                st.success(f"✅ {st.session_state.secilen_hisse} Hazır!")
                k1, k2, k3 = st.columns(3)
                k1.metric("FİYAT", f"{fiyat:.2f}")
                k2.metric("DESTEK", f"{s1:.2f}")
                k3.metric("DİRENÇ", f"{r1:.2f}")
                st.plotly_chart(fig, use_container_width=True)
                if news:
                    st.write("#### 📰 Haberler")
                    for n in news: st.markdown(n)
        if st.button("Kapat X"): st.session_state.secilen_hisse = None; st.rerun()
        st.divider()

    # Tarama Listesi
    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS"]
    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD"]
    
    @st.cache_data(ttl=180, show_spinner=False)
    def tarama_yap(liste, tip):
        bulunanlar = []; bar = st.progress(0, text=f"{tip} Taranıyor...")
        for i, symbol in enumerate(liste):
            try:
                df = yf.download(symbol, period="3d", interval="1h", progress=False)
                if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                if len(df) > 10:
                    son = df.iloc[-1]; hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]; kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                    fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                    
                    durum = None; renk = "gray"; aciklama = ""
                    if "HDFGS" in symbol:
                        if kat > 1.1: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy"
                        else: durum = "HDFGS SAKİN"
                    elif kat > 2.5:
                        durum = "BALİNA 🚀" if degisim > 0 else "SATIŞ 🔻"; renk = "buy" if degisim > 0 else "sell"; aciklama = f"Hacim {kat:.1f}x"
                    
                    if durum:
                        isim = symbol.replace(".IS", "").replace("-USD", "")
                        bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Kod": symbol})
                        if "HDFGS" in symbol and kat > 1.1: log_ekle(f"HDFGS Hareketlendi! {fiyat:.2f}")
                        elif kat > 2.5: log_ekle(f"{isim} BALİNA! {fiyat:.2f}")
                bar.progress((i+1)/len(liste)); time.sleep(0.01)
            except: continue
        bar.empty()
        return bulunanlar

    t1, t2 = st.tabs(["🏙️ BIST", "₿ KRİPTO"])
    with t1:
        if st.button("BIST TARA 📡"): st.cache_data.clear(); st.rerun()
        res = tarama_yap(bist_listesi, "BIST")
        if res:
            cols = st.columns(2)
            for i, v in enumerate(res):
                with cols[i%2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in v['Sembol'] else ""
                    st.markdown(f"""<div class="balina-karti bist-card {ozel}"><h4>{v['Sembol']}</h4><p>{v['Fiyat']:.2f} TL</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div></div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK 📈", key=f"b_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
        else: st.info("Sakin.")
    with t2:
        if st.button("KRİPTO TARA 📡"): st.cache_data.clear(); st.rerun()
        res = tarama_yap(kripto_listesi, "KRIPTO")
        if res:
            cols = st.columns(2)
            for i, v in enumerate(res):
                with cols[i%2]:
                    st.markdown(f"""<div class="balina-karti crypto-card"><h4>{v['Sembol']}</h4><p>${v['Fiyat']:.4f}</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div></div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK 📈", key=f"c_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
        else: st.info("Sakin.")

# --- DİĞER MODÜLLER ---
elif menu == "🔥 ISI HARİTASI":
    st.subheader("🌍 Piyasa Haritası")
    if st.button("HARİTA ÇİZ 🗺️"):
        l = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS"]
        with st.spinner("Veriler işleniyor..."):
            data = []
            for sym in l:
                try:
                    t = yf.Ticker(sym); info = t.fast_info
                    data.append({"Sembol": sym.replace(".IS",""), "Hacim": info.last_volume, "Degisim": 0})
                except: pass
            if data:
                fig = px.treemap(pd.DataFrame(data), path=['Sembol'], values='Hacim')
                fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

elif menu == "📒 LOGLAR":
    st.subheader("📜 Sinyal Geçmişi")
    db = load_db()
    loglar = db["admin"].get("loglar", [])
    if loglar:
        for log in loglar: st.code(log)
    else: st.warning("Kayıt yok")

elif menu == "🩻 RÖNTGEN":
    st.subheader("Şirket Röntgeni")
    s = st.text_input("Hisse:", "HDFGS.IS").upper()
    if st.button("ÇEK"):
        try:
            inf = yf.Ticker(s).info
            c1, c2 = st.columns(2)
            c1.metric("F/K", inf.get('trailingPE','-')); c2.metric("PD/DD", inf.get('priceToBook','-'))
            st.write(inf.get('longBusinessSummary','...')[:500])
        except: st.error("Veri yok")

elif menu == "⚔️ DÜELLO":
    c1, c2 = st.columns(2)
    h1 = c1.text_input("Hisse 1", "HDFGS.IS"); h2 = c2.text_input("Hisse 2", "THYAO.IS")
    if st.button("KAPIŞTIR"):
        d1 = yf.download(h1, period="1y", progress=False)['Close']
        d2 = yf.download(h2, period="1y", progress=False)['Close']
        d1 = (d1/d1.iloc[0])*100; d2 = (d2/d2.iloc[0])*100
        st.line_chart(pd.DataFrame({h1:d1, h2:d2}))
