
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
st.set_page_config(page_title="Pala Terminal v5.0", layout="wide", page_icon="⚡")

# ==========================================
# 🚨 TELEGRAM AYARLARI (SABİT)
# ==========================================
BOT_TOKEN = "8339988180:AAEzuiyBWo4lwxD73rDvjNy2k5wcL42EnUQ"
MY_CHAT_ID = "1252288326"

def send_telegram(message):
    if BOT_TOKEN and MY_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=payload)
        except: pass

# --- VERİTABANI SİSTEMİ ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {
            "admin": {
                "sifre": "pala500", 
                "isim": "Büyük Patron", 
                "onay": True, 
                "rol": "admin", 
                "mesajlar": [], 
                "loglar": [], 
                "portfoy": []
            }
        }
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session State
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- ULTRA NEON CSS TASARIMI ---
st.markdown("""
    <style>
    /* GENEL SAYFA */
    .stApp { 
        background-color: #000000; 
        background-image: radial-gradient(circle at 50% 50%, #101010 0%, #000000 100%);
        color: #e0e0e0; 
    }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #000000 !important; 
        color: #00ff41 !important; /* Hacker Yeşili */
        border: 2px solid #00ff41 !important; 
        border-radius: 0px !important; /* Köşeli Terminal Tarzı */
        font-weight: bold !important; height: 50px !important; width: 100% !important;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { 
        background-color: #00ff41 !important; 
        color: #000000 !important; 
        box-shadow: 0 0 20px #00ff41;
        transform: scale(1.02) !important; 
    }

    /* INPUT ALANLARI */
    .stTextInput input, .stNumberInput input, .stTextArea textarea { 
        background-color: #0a0a0a !important; 
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important; 
        font-family: 'Courier New', monospace;
    }

    /* Ticker */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-bottom: 1px solid #00ff41; border-top: 1px solid #00ff41;
        padding: 8px; white-space: nowrap;
    }
    .ticker { display: inline-block; animation: marquee 30s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    .ticker-item { display: inline-block; padding: 0 2rem; font-size: 16px; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41; }
    
    /* PALA STICKER */
    .pala-sticker { 
        position: fixed; top: 60px; right: 20px; 
        background-color: rgba(0,0,0,0.9); 
        border: 2px solid #00ff41;
        color: #00ff41; padding: 10px 20px; 
        text-align: center; font-weight: bold; 
        z-index: 9999; box-shadow: 0 0 15px #00ff41; 
        font-family: 'Courier New';
    }
    
    /* KARTLAR */
    .balina-karti { 
        padding: 15px; margin-bottom: 10px; 
        background-color: rgba(20,20,20,0.8); 
        border: 1px solid #333;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    .bist-card { border-left: 4px solid #00ff41; }
    .crypto-card { border-left: 4px solid #bd00ff; }
    
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; color: black;}
    .buy { background-color: #00ff41; box-shadow: 0 0 10px #00ff41; } 
    .sell { background-color: #ff003c; color: white; box-shadow: 0 0 10px #ff003c; } 
    
    .hdfgs-ozel { 
        border: 2px solid #00ff41; box-shadow: 0 0 20px rgba(0, 255, 65, 0.4); 
        animation: pulse 1.5s infinite; 
    }
    @keyframes pulse { 
        0% { box-shadow: 0 0 5px rgba(0,255,65,0.2); } 
        50% { box-shadow: 0 0 20px rgba(0,255,65,0.6); } 
        100% { box-shadow: 0 0 5px rgba(0,255,65,0.2); } 
    }

    /* Top 10 Kart */
    .top10-card {
        background: #0a0a0a; border: 1px solid #00ff41;
        padding: 10px; text-align: center; margin-bottom: 10px;
    }
    </style>
    <div class="pala-sticker"><span style="font-size:25px">⚡</span><br>SYSTEM<br>ONLINE</div>
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
            # TELEGRAM TETİKLEME
            send_telegram(f"🔔 *PALA ALERT*\n{mesaj}")
    except: pass

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def get_ticker_html():
    # Canlı Ticker Simülasyonu
    items = ["HDFGS: MONITORING", "BTC: LIVE", "USD: TRACKING", "GOLD: STABLE", "SYSTEM: SECURE"]
    html = ""
    for i in items:
        html += f"<div class='ticker-item'>{i}</div>"
    return html

@st.cache_data(ttl=3600) 
def get_top_10_potential():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS"]
    results = []
    for s in candidates:
        try:
            df = yf.download(s, period="5d", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if len(df) > 2:
                son = df.iloc[-1]
                change = ((son['Close'] - df['Open'].iloc[-1])/df['Open'].iloc[-1])*100
                if change > 0:
                    results.append({"Sembol": s.replace(".IS",""), "Fiyat": son['Close'], "Degisim": change})
        except: pass
    return sorted(results, key=lambda x: x['Degisim'], reverse=True)[:5]

# --- GRAFİK MOTORU ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            prev = df.iloc[-2]; pivot = (prev['High']+prev['Low']+prev['Close'])/3
            r1=(2*pivot)-prev['Low']; s1=(2*pivot)-prev['High']
            
            fig = go.Figure()
            # Neon Mumlar
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                         increasing_line_color='#00ff41', decreasing_line_color='#ff003c', name="Price"))
            
            fig.add_hline(y=r1, line_dash="dash", line_color="#ff003c", annotation_text="RESISTANCE")
            fig.add_hline(y=s1, line_dash="dash", line_color="#00ff41", annotation_text="SUPPORT")
            
            fig.update_layout(title=f"{symbol} ANALYSIS", template="plotly_dark", height=500, 
                              xaxis_rangeslider_visible=False, plot_bgcolor='#050505', paper_bgcolor='#050505')
            
            news = []
            try:
                n = yf.Ticker(symbol).news
                for i in n[:3]: news.append(f"📰 [{i['title']}]({i['link']})")
            except: pass
            return fig, df.iloc[-1]['Close'], s1, r1, news
    except: return None, None, None, None, None

# ==========================================
# 1. YÖNETİM PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 ADMIN ROOT")
    
    # Telegram Test
    if st.sidebar.button("🔔 Test Telegram"):
        send_telegram("🦅 *Pala Terminal:* System Check OK.")
        st.sidebar.success("Signal Sent.")

    menu = st.sidebar.radio("System:", ["USERS", "MESSAGES"])
    db = load_db()
    
    if menu == "USERS":
        uye_data = []
        for k, v in db.items():
            if k != "admin":
                durum = "✅ ACTIVE" if v.get('onay') else "❌ PENDING"
                uye_data.append({"User": k, "Name": v.get('isim', '-'), "Status": durum})
        if len(uye_data) > 0:
            st.table(pd.DataFrame(uye_data))
            c1, c2 = st.columns(2)
            with c1:
                onaysizlar = [u['User'] for u in uye_data if u['Status'] == "❌ PENDING"]
                if onaysizlar:
                    u_app = st.selectbox("Approve:", onaysizlar)
                    if st.button("AUTHORIZE ✅"):
                        db[u_app]['onay'] = True; save_db(db)
                        st.success(f"{u_app} Authorized!"); send_telegram(f"✅ New User: {u_app}")
                        time.sleep(1); st.rerun()
            with c2:
                tum = [u['User'] for u in uye_data]
                if tum:
                    u_del = st.selectbox("Delete:", tum)
                    if st.button("TERMINATE 🗑️"):
                        del db[u_del]; save_db(db); st.warning("User Deleted"); time.sleep(1); st.rerun()
        else: st.info("No users.")
    elif menu == "MESSAGES":
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                with st.expander(f"👤 {v.get('isim','-')} ({k})"):
                    for msg in v['mesajlar']: st.info(msg)

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    user = st.session_state.login_user; db = st.session_state.db
    
    # Ticker
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker">{get_ticker_html()}</div></div>""", unsafe_allow_html=True)
    
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = db[user].get('isim', 'Operator')
        st.title("⚡ PALA NEON TERMINAL")
        st.caption(f"OPERATOR: {isim.upper()} | ACCESS LEVEL: VIP")
    with col_head[1]:
        if st.button("LOGOUT"): st.session_state.login_user = None; st.rerun()

    if db[user].get('rol') == 'admin': admin_dashboard()

    # --- HAFTANIN YILDIZLARI ---
    st.markdown("### 🌟 TOP PERFORMERS (WEEKLY)")
    top10 = get_top_10_potential()
    if top10:
        cols = st.columns(5)
        for i, item in enumerate(top10):
            with cols[i]:
                st.markdown(f"""
                <div class="top10-card">
                    <h3 style="margin:0; color:#00ff41;">{item['Sembol']}</h3>
                    <h2 style="margin:0; color:white;">{item['Fiyat']:.2f}</h2>
                    <span style="color:#00ff41;">+%{item['Degisim']:.1f}</span>
                </div>""", unsafe_allow_html=True)

    menu = st.radio("MODULES:", ["📊 RADAR", "💼 WALLET", "🔥 HEATMAP", "📒 LOGS", "🩻 X-RAY", "⚔️ DUEL"], horizontal=True)
    st.markdown("<hr style='border: 1px solid #00ff41;'>", unsafe_allow_html=True)

    # --- WALLET ---
    if menu == "💼 WALLET":
        st.subheader("💾 ASSET MANAGEMENT")
        with st.expander("➕ ADD ASSET"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.text_input("SYM", "HDFGS.IS").upper()
            y_mal = c2.number_input("COST", value=2.63)
            y_adt = c3.number_input("QTY", value=194028)
            if c4.button("SAVE"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != y_sem]
                db[user]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("SAVED"); st.rerun()
        
        if "portfoy" in db[user] and db[user]["portfoy"]:
            total_val = 0; total_profit = 0; pie_data = []; table_data = []
            for p in db[user]["portfoy"]:
                try:
                    fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                    val = fiyat * p['adet']; profit = (fiyat - p['maliyet']) * p['adet']
                    total_val += val; total_profit += profit
                    table_data.append({"ASSET": p['sembol'], "PRICE": f"{fiyat:.2f}", "PROFIT": f"{profit:,.0f}"})
                    pie_data.append({"Sembol": p['sembol'], "Deger": val})
                except: pass
            
            k1, k2 = st.columns(2)
            k1.metric("TOTAL EQUITY", f"{total_val:,.0f} TL")
            k2.metric("NET PROFIT", f"{total_profit:,.0f} TL", delta_color="normal")
            
            c_pie, c_tab = st.columns([1, 2])
            with c_pie:
                if pie_data:
                    fig = px.pie(pd.DataFrame(data_pie), values='Deger', names='Sembol', hole=0.5)
                    fig.update_traces(textinfo='label+percent')
                    fig.update_layout(template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
            with c_tab: st.table(pd.DataFrame(table_data))
            
            sil = st.selectbox("DELETE:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("CONFIRM DELETE"):
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sil]; save_db(db); st.rerun()

    # --- RADAR ---
    elif menu == "📊 RADAR":
        c_s1, c_s2 = st.columns([3, 1])
        arama = c_s1.text_input("SEARCH:", placeholder="HDFGS...").upper()
        if c_s2.button("SCAN 🚀"):
            sym = f"{arama}.IS" if "-" not in arama and ".IS" not in arama and "USD" not in arama else arama
            st.session_state.secilen_hisse = sym; st.rerun()

        if st.session_state.secilen_hisse:
            with st.spinner("SCANNING..."):
                fig, fiyat, s1, r1, news = grafik_ciz(st.session_state.secilen_hisse)
                if fig:
                    st.success("TARGET ACQUIRED")
                    k1, k2, k3 = st.columns(3)
                    k1.metric("PRICE", f"{fiyat:.2f}")
                    k2.metric("SUPPORT", f"{s1:.2f}")
                    k3.metric("RESISTANCE", f"{r1:.2f}")
                    st.plotly_chart(fig, use_container_width=True)
                    if news:
                        st.write("#### 📰 NEWS FEED")
                        for n in news: st.markdown(n)
            if st.button("CLOSE X"): st.session_state.secilen_hisse = None; st.rerun()
        
        # LISTELER
        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
        kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]
        
        telegram_aktif = st.checkbox("🔔 SEND TELEGRAM ALERTS")

        @st.cache_data(ttl=180, show_spinner=False)
        def tarama_yap(liste, tip, bildirim):
            bulunanlar = []; bar = st.progress(0, text=f"SCANNING {tip}...")
            for i, symbol in enumerate(liste):
                try:
                    df = yf.download(symbol, period="3d", interval="1h", progress=False)
                    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                    if len(df) > 10:
                        son = df.iloc[-1]; hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]; kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                        fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                        
                        durum = None; renk = "gray"; aciklama = ""
                        if "HDFGS" in symbol:
                            if kat > 1.1: durum = "HDFGS ACTIVE 🦅"; renk = "buy"
                            else: durum = "HDFGS STABLE"
                        elif kat > 2.5:
                            durum = "WHALE ALERT 🚀" if degisim > 0 else "DUMP ALERT 🔻"; renk = "buy" if degisim > 0 else "sell"; aciklama = f"VOL: {kat:.1f}x"
                        
                        if durum:
                            isim = symbol.replace(".IS", "").replace("-USD", "")
                            bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama})
                            
                            if bildirim:
                                if "HDFGS" in symbol and kat > 1.1: log_ekle(f"HDFGS MOVING! {fiyat:.2f}")
                                elif kat > 2.5: log_ekle(f"{isim} WHALE! {fiyat:.2f}")
                                
                    bar.progress((i+1)/len(liste)); time.sleep(0.01)
                except: continue
            bar.empty()
            return bulunanlar

        t1, t2 = st.tabs(["BIST SECTOR", "CRYPTO SECTOR"])
        with t1:
            if st.button("SCAN BIST 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(bist_listesi, "BIST", telegram_aktif)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        ozel = "hdfgs-ozel" if "HDFGS" in v['Sembol'] else ""
                        st.markdown(f"""<div class="balina-karti bist-card {ozel}"><h4>{v['Sembol']}</h4><p>{v['Fiyat']:.2f} TL</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div></div>""", unsafe_allow_html=True)
            else: st.info("NO SIGNAL.")
        with t2:
            if st.button("SCAN CRYPTO 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(kripto_listesi, "KRIPTO", telegram_aktif)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><h4>{v['Sembol']}</h4><p>${v['Fiyat']:.4f}</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div></div>""", unsafe_allow_html=True)
            else: st.info("NO SIGNAL.")

    # --- DİĞER MODÜLLER ---
    elif menu == "🔥 HEATMAP":
        st.subheader("MARKET HEATMAP")
        if st.button("GENERATE MAP"):
            l = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS"]
            with st.spinner("PROCESSING..."):
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

    elif menu == "📒 LOGS":
        st.subheader("SIGNAL LOGS")
        loglar = db["admin"].get("loglar", [])
        if loglar:
            for log in loglar: st.code(log)
        else: st.warning("NO LOGS")
        if st.button("CLEAR LOGS"): db["admin"]["loglar"] = []; save_db(db); st.rerun()

    elif menu == "🩻 X-RAY":
        st.subheader("FUNDAMENTAL DATA")
        s = st.text_input("ASSET:", "HDFGS.IS").upper()
        if st.button("SCAN"):
            try:
                inf = yf.Ticker(s).info
                c1, c2 = st.columns(2)
                c1.metric("P/E", inf.get('trailingPE','-')); c2.metric("P/B", inf.get('priceToBook','-'))
                st.write(inf.get('longBusinessSummary','NO DATA')[:500])
            except: st.error("ERROR")
            
    elif menu == "⚔️ DUEL":
        c1, c2 = st.columns(2)
        h1 = c1.text_input("ASSET 1", "HDFGS.IS"); h2 = c2.text_input("ASSET 2", "THYAO.IS")
        if st.button("COMPARE"):
            try:
                d1 = yf.download(h1, period="1y", progress=False)['Close']
                d2 = yf.download(h2, period="1y", progress=False)['Close']
                d1 = (d1/d1.iloc[0])*100; d2 = (d2/d2.iloc[0])*100
                st.line_chart(pd.DataFrame({h1:d1, h2:d2}))
            except: st.error("ERROR")

# ==========================================
# LOGIN / PAYMENT
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center; margin-top:50px;"><h1 style="color:#00ff41; font-size: 60px; text-shadow: 0 0 20px #00ff41;">⚡ PALA TERMINAL</h1></div>""", unsafe_allow_html=True)
    t1, t2 = st.tabs(["LOGIN", "REGISTER"])
    with t1:
        k = st.text_input("USERNAME"); s = st.text_input("PASSWORD", type="password")
        if st.checkbox("SYSTEM RESET"):
            if st.button("EXECUTE RESET"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "System Admin", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("RESET COMPLETE: admin / pala500")
        if st.button("ACCESS"):
            db=load_db()
            if k in db and db[k]['sifre']==s: st.session_state.login_user=k; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("ACCESS DENIED")
    with t2:
        yk = st.text_input("NEW USER"); y_ad = st.text_input("NAME"); ys = st.text_input("NEW PASS", type="password")
        if st.button("CREATE ACCOUNT"):
            db=load_db()
            if yk not in db: db[yk] = {"sifre":ys, "isim":y_ad, "onay":False, "rol":"user", "mesajlar":[], "portfoy":[]}; save_db(db); st.success("ACCOUNT CREATED. PLEASE LOGIN.")
            else: st.error("USERNAME TAKEN")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#ff003c;'>🔒 ACCESS RESTRICTED</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>FEE: $500</h2><p>WAITING FOR ADMIN APPROVAL</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='odeme-kutu'><strong>USDT</strong><br>TXa...</div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("PAYMENT PROOF"); 
        if st.button("SEND PROOF"):
            u=st.session_state.login_user; db=load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"]=[]
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("SENT")
    if st.button("LOGOUT"): st.session_state.login_user=None; st.rerun()

if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
