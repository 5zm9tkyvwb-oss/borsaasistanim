import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import random
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala Terminal v4.0", layout="wide", page_icon="💻")

# --- VERİTABANI SİSTEMİ ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "SYSTEM ADMIN", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
        save_db(default_db); return default_db
    try: with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- MATRIX / CYBERPUNK TASARIM ---
st.markdown("""
    <style>
    /* GENEL SAYFA */
    .stApp { 
        background-color: #050505 !important; 
        font-family: 'Courier New', Courier, monospace;
        background-image: radial-gradient(circle at 50% 50%, #112211 0%, #000000 100%);
    }
    
    /* YAZILAR */
    h1, h2, h3, p, label, span { color: #00ff41 !important; text-shadow: 0 0 5px #003300; }
    .stCaption { color: #008F11 !important; }
    
    /* INPUT ALANLARI */
    .stTextInput input, .stNumberInput input, .stTextArea textarea { 
        background-color: #0d0d0d !important; 
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important; 
        border-radius: 5px;
        box-shadow: 0 0 5px #00ff41;
    }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #000000 !important; 
        color: #00ff41 !important; 
        border: 2px solid #00ff41 !important; 
        border-radius: 0px !important; /* Köşeli Terminal Butonu */
        font-weight: bold !important; 
        font-family: 'Courier New', monospace;
        height: 50px !important; 
        width: 100% !important;
        transition: all 0.2s ease !important;
        letter-spacing: 2px;
    }
    div.stButton > button:hover { 
        background-color: #00ff41 !important; 
        color: #000000 !important; 
        box-shadow: 0 0 20px #00ff41;
        transform: scale(1.02);
    }
    
    /* CANLI TICKER */
    .ticker-wrap {
        width: 100%; overflow: hidden; background-color: #000; 
        border-bottom: 1px solid #00ff41; border-top: 1px solid #00ff41;
        padding: 8px; white-space: nowrap;
        box-shadow: 0 0 10px #00ff41;
    }
    .ticker-item { display: inline-block; padding: 0 2rem; font-size: 16px; font-weight: bold; color: #00ff41; text-shadow: 0 0 5px #00ff41; }
    
    /* KARTLAR & PANELLER */
    .balina-karti { 
        background-color: rgba(0, 20, 0, 0.8); 
        border: 1px solid #00ff41; 
        padding: 15px; 
        margin-bottom: 10px; 
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
    }
    .bist-card { border-left: 5px solid #00ff41; }
    .crypto-card { border-left: 5px solid #00bfff; }
    
    /* ETIKETLER */
    .signal-box { padding: 4px 8px; font-weight: bold; font-size: 12px; display: inline-block; color: black; }
    .buy { background-color: #00ff41; box-shadow: 0 0 10px #00ff41; } 
    .sell { background-color: #ff0033; color: white; box-shadow: 0 0 10px #ff0033; } 
    
    /* HDFGS OZEL */
    .hdfgs-ozel { 
        border: 2px solid #00bfff; 
        box-shadow: 0 0 25px #00bfff; 
        animation: pulse 1.5s infinite; 
    }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #00bfff; } 50% { box-shadow: 0 0 20px #00bfff; } 100% { box-shadow: 0 0 5px #00bfff; } }
    
    /* PALA LOGO */
    .pala-sticker { 
        position: fixed; top: 60px; right: 20px; 
        background-color: black; 
        border: 2px solid #00ff41;
        color: #00ff41; 
        padding: 10px; 
        text-align: center; font-weight: bold; 
        z-index: 9999; 
        box-shadow: 0 0 15px #00ff41; 
        font-family: 'Courier New';
    }
    </style>
    <div class="pala-sticker">
        <span style="font-size:25px">💀</span><br>SYSTEM<br>ONLINE
    </div>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][0]:
            db["admin"]["loglar"].insert(0, f"[{tarih}] {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
    except: pass

def get_ticker_html():
    items = ["SYSTEM: ONLINE", "HDFGS: MONITORING", "BTC: CONNECTED", "USD: TRACKING", "TARGET: LOCKED"]
    html_content = ""
    for i in items:
        html_content += f"<div class='ticker-item'>{i}</div>"
    return html_content

# --- GRAFİK ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            prev = df.iloc[-2]; pivot = (prev['High']+prev['Low']+prev['Close'])/3
            r1=(2*pivot)-prev['Low']; s1=(2*pivot)-prev['High']
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="PRICE"))
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text="RESISTANCE")
            fig.add_hline(y=s1, line_dash="dash", line_color="#00ff41", annotation_text="SUPPORT")
            # Grafik Arka Planı Siyah
            fig.update_layout(title=f"SYSTEM ANALYSIS: {symbol}", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, plot_bgcolor='#000000', paper_bgcolor='#000000')
            return fig, df.iloc[-1]['Close'], s1, r1
    except: return None, None, None, None

# ==========================================
# 1. YÖNETİM PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("🔒 ROOT ACCESS")
    menu = st.sidebar.radio("Command:", ["USERS", "LOGS"])
    db = load_db()
    
    if menu == "USERS":
        uye_data = []
        for k, v in db.items():
            if k != "admin":
                durum = "ACCESS GRANTED" if v.get('onay') else "ACCESS DENIED"
                uye_data.append({"User": k, "Status": durum})
        if len(uye_data) > 0:
            st.table(pd.DataFrame(uye_data))
            c1, c2 = st.columns(2)
            with c1:
                onaysizlar = [u['User'] for u in uye_data if u['Status'] == "ACCESS DENIED"]
                if onaysizlar:
                    u_app = st.selectbox("Grant Access:", onaysizlar)
                    if st.button("AUTHORIZE ✅"):
                        db[u_app]['onay'] = True; save_db(db); st.success("ACCESS GRANTED"); time.sleep(1); st.rerun()
            with c2:
                tum = [u['User'] for u in uye_data]
                if tum:
                    u_del = st.selectbox("Delete User:", tum)
                    if st.button("TERMINATE 🗑️"):
                        del db[u_del]; save_db(db); st.warning("USER TERMINATED"); time.sleep(1); st.rerun()
        else: st.info("No users found in database.")

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    user = st.session_state.login_user; db = st.session_state.db
    
    # Ticker
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker">{get_ticker_html()}</div></div>""", unsafe_allow_html=True)
    
    col_head = st.columns([8, 2])
    with col_head[0]:
        st.title("📟 PALA TERMINAL v4.0")
        st.caption(f"USER: {user.upper()} | STATUS: ONLINE | CONNECTION: SECURE")
    with col_head[1]:
        if st.button("LOGOUT"):
            st.session_state.login_user = None; st.rerun()

    if db[user].get('rol') == 'admin': admin_dashboard()

    menu = st.radio("MODULES:", ["📊 RADAR", "💼 WALLET", "🔥 HEATMAP", "🩻 X-RAY"], horizontal=True)
    st.markdown("<hr style='border: 1px solid #00ff41;'>", unsafe_allow_html=True)

    # --- WALLET ---
    if menu == "💼 WALLET":
        st.subheader("💾 ASSET MANAGEMENT")
        with st.expander("➕ ADD ASSET"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.text_input("SYMBOL", "HDFGS.IS").upper()
            y_mal = c2.number_input("ENTRY PRICE", value=2.63)
            y_adt = c3.number_input("QUANTITY", value=194028)
            if c4.button("SAVE DATA"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != y_sem]
                db[user]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("DATA SAVED"); st.rerun()

        if "portfoy" in db[user] and db[user]["portfoy"]:
            total_val = 0; total_profit = 0; table_data = []
            for p in db[user]["portfoy"]:
                try:
                    fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                    val = fiyat * p['adet']; profit = (fiyat - p['maliyet']) * p['adet']
                    total_val += val; total_profit += profit
                    table_data.append({"ASSET": p['sembol'], "PRICE": f"{fiyat:.2f}", "PROFIT": f"{profit:,.0f}"})
                except: pass
            
            k1, k2 = st.columns(2)
            k1.metric("TOTAL BALANCE", f"{total_val:,.0f} TL")
            k2.metric("NET PROFIT", f"{total_profit:,.0f} TL", delta_color="normal")
            st.table(pd.DataFrame(table_data))
            
            sil = st.selectbox("DELETE ASSET:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("CONFIRM DELETE"):
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sil]; save_db(db); st.rerun()
        else: st.info("NO ASSETS FOUND.")

    # --- RADAR ---
    elif menu == "📊 RADAR":
        c_s1, c_s2 = st.columns([3, 1])
        arama = c_s1.text_input("SEARCH TARGET:", placeholder="HDFGS...").upper()
        if c_s2.button("SCAN TARGET 🚀"):
            sym = f"{arama}.IS" if "-" not in arama and ".IS" not in arama and "USD" not in arama else arama
            st.session_state.secilen_hisse = sym; st.rerun()

        if st.session_state.secilen_hisse:
            with st.spinner("SCANNING..."):
                fig, fiyat, s1, r1 = grafik_ciz(st.session_state.secilen_hisse)
                if fig:
                    st.success("TARGET ACQUIRED")
                    k1, k2, k3 = st.columns(3)
                    k1.metric("PRICE", f"{fiyat:.2f}")
                    k2.metric("SUPPORT", f"{s1:.2f}")
                    k3.metric("RESISTANCE", f"{r1:.2f}")
                    st.plotly_chart(fig, use_container_width=True)
            if st.button("CLOSE VISUAL"): st.session_state.secilen_hisse = None; st.rerun()

        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS"]
        kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD"]

        @st.cache_data(ttl=180, show_spinner=False)
        def tarama_yap(liste):
            bulunanlar = []; bar = st.progress(0, text="SCANNING SECTOR...")
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
                    bar.progress((i+1)/len(liste)); time.sleep(0.01)
                except: continue
            bar.empty()
            return bulunanlar

        t1, t2 = st.tabs(["BIST SECTOR", "CRYPTO SECTOR"])
        with t1:
            if st.button("SCAN BIST 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(bist_listesi)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        ozel = "hdfgs-ozel" if "HDFGS" in v['Sembol'] else ""
                        st.markdown(f"""<div class="balina-karti bist-card {ozel}"><h4>{v['Sembol']}</h4><p>{v['Fiyat']:.2f} TL</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style='font-size:10px'>{v['Aciklama']}</p></div>""", unsafe_allow_html=True)
            else: st.info("NO SIGNAL DETECTED.")
        with t2:
            if st.button("SCAN CRYPTO 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(kripto_listesi)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><h4>{v['Sembol']}</h4><p>${v['Fiyat']:.4f}</p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style='font-size:10px'>{v['Aciklama']}</p></div>""", unsafe_allow_html=True)
            else: st.info("NO SIGNAL DETECTED.")

    # --- DİĞERLERİ ---
    elif menu == "🩻 X-RAY":
        st.subheader("FUNDAMENTAL ANALYSIS")
        s = st.text_input("ASSET:", "HDFGS.IS").upper()
        if st.button("ANALYZE"):
            try:
                inf = yf.Ticker(s).info
                c1, c2 = st.columns(2)
                c1.metric("P/E RATIO", inf.get('trailingPE','-')); c2.metric("P/B RATIO", inf.get('priceToBook','-'))
                st.write(inf.get('longBusinessSummary','No Data.')[:500])
            except: st.error("DATA ERROR")
            
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

# ==========================================
# LOGIN
# ==========================================
def login_page():
    st.markdown("""
    <div style="text-align:center; margin-top:50px;">
        <h1 style="color:#00ff41; font-size: 60px; text-shadow: 0 0 20px #00ff41;">📟 PALA TERMINAL</h1>
        <p style="color:#008F11;">SECURE ACCESS GATEWAY v4.0</p>
    </div>
    """, unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["LOGIN", "REGISTER"])
    with t1:
        k = st.text_input("USERNAME"); s = st.text_input("PASSWORD", type="password")
        if st.checkbox("SYSTEM RESET (Admin Recovery)"):
            if st.button("EXECUTE RESET"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "System Admin", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("RESET COMPLETE: admin / pala500")
        if st.button("ACCESS SYSTEM"):
            db=load_db()
            if k in db and db[k]['sifre']==s: st.session_state.login_user=k; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("ACCESS DENIED")
    with t2:
        yk = st.text_input("NEW USERNAME"); y_ad = st.text_input("FULL NAME"); ys = st.text_input("NEW PASSWORD", type="password")
        if st.button("CREATE ACCOUNT"):
            db=load_db()
            if yk not in db: db[yk] = {"sifre":ys, "isim":y_ad, "onay":False, "rol":"user", "mesajlar":[], "portfoy":[]}; save_db(db); st.success("ACCOUNT CREATED. PROCEED TO PAYMENT.")
            else: st.error("USERNAME TAKEN")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FF0000;'>🔒 ACCESS RESTRICTED</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background-color:#111; border:2px solid #FF0000; padding:30px; text-align:center; box-shadow:0 0 30px #FF0000;">
        <h2 style="color:#FF0000">MEMBERSHIP FEE: $500</h2>
        <p>LIFETIME ACCESS TO PALA TERMINAL</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div style='background:#000; padding:10px; border:1px solid #00ff41; margin-top:10px;'><strong>USDT (TRC20)</strong><br><code>TXa...</code></div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("PAYMENT PROOF (TXID / NAME)"); 
        if st.button("SEND PROOF"):
            u=st.session_state.login_user; db=load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"]=[]
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("PROOF SENT. AWAITING ADMIN APPROVAL.")
    if st.button("LOGOUT"): st.session_state.login_user=None; st.rerun()

if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
