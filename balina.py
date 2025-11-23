import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import requests
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="PALA Balina Avcısı", layout="wide", page_icon="🦈")

# ==========================================
# 💰 AYARLAR & LİSTELER
# ==========================================
USDT_ADDRESS = "TV4DK7vckLWJciKSqhvY5hEpcw1Ka522AQ"
DENEME_SURESI_DK = 10 
BIST_HISSELERI = [
    "THYAO", "ASELS", "GARAN", "AKBNK", "TUPRS", "SASA", "HEKTS", "EREGL", "KCHOL", "BIMAS",
    "EKGYO", "ODAS", "KONTR", "GUBRF", "FROTO", "ASTOR", "REEDR", "EUPWR", "GESAN", "SMRTG",
    "HDFGS", "ISCTR", "YKBNK", "PETKM", "KOZAL", "KRDMD", "VESTL", "ARCLK", "TOASO", "TTKOM",
    "TCELL", "SOKM", "MGROS", "ALFAS", "CANTE", "CVKMD", "KCAER", "OYAKC", "EGEEN", "DOAS",
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD", "DOGE-USD", "SHIB-USD"
]
BIST_HISSELERI.sort()

# ==========================================
# 🚨 TELEGRAM & VERİTABANI
# ==========================================
BOT_TOKEN = "8339988180:AAEzuiyBWo4lwxD73rDvjNy2k5wcL42EnUQ"
MY_CHAT_ID = "1252288326"

def send_telegram(message):
    if BOT_TOKEN and MY_CHAT_ID:
        try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"})
        except: pass

DB_FILE = "users_db.json"
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)
def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "duyuru": "", "kayit_tarihi": time.time()}}
        save_db(default_db); return default_db
    try: return json.load(open(DB_FILE, "r"))
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None
if 'odeme_modu' not in st.session_state: st.session_state.odeme_modu = False

# --- TASARIM (NEON CYBERPUNK) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a14 !important; background-image: radial-gradient(rgba(0, 255, 249, 0.1) 1px, transparent 1px); background-size: 50px 50px; color: #e6e6e6 !important; font-family: 'Orbitron', sans-serif; }
    .vip-offer-box { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 15px; text-align: center; color: #050a14; margin-bottom: 20px; box-shadow: 0 0 25px rgba(56, 239, 125, 0.4); border: 2px solid #fff; animation: pulse-green 2s infinite; }
    .vip-price { font-size: 35px; font-weight: 900; text-shadow: 0 0 5px rgba(0,0,0,0.3); }
    @keyframes pulse-green { 0% { transform: scale(1); } 50% { transform: scale(1.01); } 100% { transform: scale(1); } }
    .trial-counter { position: fixed; top: 15px; right: 20px; background: rgba(0,0,0,0.8); border: 2px solid #ff9900; color: #ff9900; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; z-index: 10000; animation: blink 2s infinite; }
    @keyframes blink { 50% { border-color: red; color: red; } }
    .hero-container { padding: 40px; background: rgba(0,0,0,0.4); border-radius: 20px; border: 1px solid #00fff9; margin-bottom: 20px; }
    .hero-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(#00fff9, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .feature-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #ff00ff; margin-bottom: 10px; }
    .feature-title { color: #00fff9; font-weight: bold; font-size: 16px; margin-bottom: 5px;}
    .login-container { background: rgba(0,0,0,0.8); padding: 30px; border-radius: 20px; border: 2px solid #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.3); }
    .top-list-box { background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; border-top: 3px solid #00fff9; margin-bottom: 5px; }
    .list-item { font-size: 13px; border-bottom: 1px solid #333; padding: 3px 0; display: flex; justify-content: space-between; }
    .pos { color: #38ef7d; } .neg { color: #ef473a; } .spek { color: #ff00ff; }
    .neon-title { font-size: 60px !important; font-weight: 900; color: #fff; text-align: center; text-shadow: 0 0 10px #00fff9, 0 0 40px #00fff9, 0 0 80px #ff00ff; }
    .wallet-box { background: rgba(0,0,0,0.6); border: 2px solid #00fff9; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 255, 249, 0.2); }
    .wallet-addr { font-family: monospace; font-size: 20px; color: #ff00ff; font-weight: bold; word-break: break-all; background: #000; padding: 10px; border-radius: 5px; border: 1px dashed #ff00ff; }
    div.stButton > button { background: linear-gradient(90deg, #00fff9, #ff00ff) !important; color: #000 !important; border: none !important; font-weight: 800 !important; }
    .ai-box { background: rgba(0, 255, 249, 0.05); border: 1px solid #00fff9; padding: 15px; border-radius: 10px; margin-top: 10px; }
    
    /* Sidebar Özelleştirme */
    section[data-testid="stSidebar"] { background-color: #0b1116 !important; border-right: 1px solid #00fff9; }
    .sidebar-header { color: #00fff9; font-weight: bold; font-size: 18px; margin-bottom: 10px; border-bottom: 1px solid #ff00ff; padding-bottom: 5px; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- GÜVENLİ VERİ ÇEKME ---
def get_live_rates():
    try:
        tickers = ["TRY=X", "EURTRY=X", "GC=F", "SI=F", "BZ=F", "BTC-USD", "ETH-USD"]
        data = yf.download(tickers, period="1d", progress=False)['Close']
        if not data.empty:
            last = data.iloc[-1]
            usd = last.get('TRY=X', 34.50)
            return usd, last.get('EURTRY=X', 37.20), (last.get('GC=F', 2600) * usd) / 31.1035, (last.get('SI=F', 30) * usd) / 31.1035, last.get('BZ=F', 75), last.get('BTC-USD', 98000), last.get('ETH-USD', 3200)
        return 34.50, 37.20, 2950.0, 34.0, 75.0, 98000.0, 3200.0
    except: return 34.50, 37.20, 2950.0, 34.0, 75.0, 98000.0, 3200.0

@st.cache_data(ttl=1800)
def get_market_analysis():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "BIMAS.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "ASTOR.IS", "REEDR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "HDFGS.IS", "ISCTR.IS", "YKBNK.IS", "PETKM.IS", "KOZAL.IS", "VESTL.IS", "TOASO.IS", "TTKOM.IS", "TCELL.IS", "ALFAS.IS", "CVKMD.IS", "OYAKC.IS", "EGEEN.IS"]
    w, m, radar = [], [], []
    try:
        for s in candidates:
            try:
                df = yf.download(s, period="1mo", interval="1d", progress=False)
                if len(df) > 15:
                    son = df['Close'].iloc[-1]
                    w_ch = ((son - df['Close'].iloc[-5])/df['Close'].iloc[-5])*100
                    m_ch = ((son - df['Close'].iloc[0])/df['Close'].iloc[0])*100
                    vol = ((df['High'].iloc[-1]-df['Low'].iloc[-1])/df['Open'].iloc[-1])*100
                    
                    # Radar için Hacim Patlaması Kontrolü
                    hacim_son = df['Volume'].iloc[-1]
                    hacim_ort = df['Volume'].rolling(10).mean().iloc[-1]
                    if hacim_son > hacim_ort * 2:
                        radar.append(f"🚨 {s.replace('.IS','')} (+%{w_ch:.1f})")

                    w.append({"Sembol": s.replace(".IS",""), "Degisim": w_ch, "Fiyat": son, "Volatilite": vol})
                    m.append({"Sembol": s.replace(".IS",""), "Degisim": m_ch, "Fiyat": son})
            except: continue
        
        if not w: return [], [], [], [], []
        
        return (sorted(w, key=lambda x:x['Degisim'], reverse=True)[:5], 
                sorted(m, key=lambda x:x['Degisim'], reverse=True)[:5], 
                sorted(w, key=lambda x:x['Degisim'])[:5], 
                sorted(w, key=lambda x:x['Volatilite'], reverse=True)[:5],
                radar[:10])
    except: return [], [], [], [], []

def grafik_ciz(symbol, show_sma, show_bb):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            # İndikatör Hesaplamaları
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['STD'] = df['Close'].rolling(window=20).std()
            df['Upper'] = df['SMA20'] + (df['STD'] * 2)
            df['Lower'] = df['SMA20'] - (df['STD'] * 2)
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain/loss)))
            rsi_val = rsi.iloc[-1]
            pivot = (df.iloc[-2]['High'] + df.iloc[-2]['Low'] + df.iloc[-2]['Close']) / 3
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat")])
            
            # İsteğe Bağlı İndikatörler
            if show_sma:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1), name='SMA 20'))
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='blue', width=1), name='SMA 50'))
            
            if show_bb:
                fig.add_trace(go.Scatter(x=df.index, y=df['Upper'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), name='BB Üst'))
                fig.add_trace(go.Scatter(x=df.index, y=df['Lower'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1), fill='tonexty', name='BB Alt'))

            fig.add_hline(y=pivot, line_dash="dot", line_color="#00fff9", annotation_text="PIVOT")
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title=f"{symbol} ANALİZİ", height=500)
            
            # Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta", value = rsi_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "RSI GÜCÜ", 'font': {'size': 18, 'color': "#00fff9"}},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#00fff9"}, 'steps': [{'range': [0, 30], 'color': 'green'}, {'range': [70, 100], 'color': 'red'}]}))
            fig_gauge.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=300)

            ai_text = f"**🤖 PALA ANALİZ:**\nFiyat: **{df.iloc[-1]['Close']:.2f}**."
            if rsi_val < 30: ai_text += " RSI aşırı satımda (UCUZ). Tepki gelebilir. 🟢"
            elif rsi_val > 70: ai_text += " RSI aşırı alımda (PAHALI). Düzeltme gelebilir. 🔴"
            else: ai_text += " Piyasa kararsız (NÖTR). 🟡"

            return fig, df.iloc[-1]['Close'], pivot, (2*pivot)-df.iloc[-2]['Low'], rsi_val, fig_gauge, ai_text
    except: return None, None, None, None, None, None, None

def admin_dashboard():
    st.sidebar.title("👑 YÖNETİM"); menu = st.sidebar.radio("Menü:", ["Üyeler", "Duyuru"]); db = load_db()
    if menu == "Üyeler":
        for k, v in db.items():
            if k != "admin":
                with st.expander(f"{v.get('isim')} ({k}) - {'✅' if v.get('onay') else '⏳'}"):
                    c1, c2 = st.columns(2)
                    if c1.button("ONAYLA", key=f"a_{k}"): db[k]['onay']=True; save_db(db); st.rerun()
                    if c2.button("SİL", key=f"d_{k}"): del db[k]; save_db(db); st.rerun()
    elif menu == "Duyuru":
        d = st.text_input("Mesaj:"); 
        if st.button("YAYINLA") and d: db["admin"]["duyuru"] = d; save_db(db); st.success("Yayında!")

def ana_uygulama(kalan_sure_dk=None):
    db = load_db(); user = st.session_state.login_user
    if user not in db: st.session_state.login_user = None; st.rerun()
    
    # --- SIDEBAR ARAÇLARI (YENİ EKLENDİ) ---
    st.sidebar.markdown("<div class='sidebar-header'>🧮 PALA HESAP MAKİNESİ</div>", unsafe_allow_html=True)
    with st.sidebar.expander("Kâr/Zarar Hesapla", expanded=False):
        bakiye = st.number_input("Bakiye (TL)", value=10000)
        giris_f = st.number_input("Giriş Fiyatı", value=10.0)
        hedef_f = st.number_input("Hedef Fiyat", value=11.0)
        if giris_f > 0:
            lot = int(bakiye / giris_f)
            potansiyel_kar = (hedef_f - giris_f) * lot
            st.info(f"Alınabilir Lot: {lot}")
            st.success(f"Potansiyel Kâr: {potansiyel_kar:.2f} TL")

    # --- SIDEBAR BALİNA RADARI (YENİ EKLENDİ) ---
    wg, mg, wl, sp, radar = get_market_analysis() # Radar verisini de al
    st.sidebar.markdown("<br><div class='sidebar-header'>📡 PALA RADARI (CANLI)</div>", unsafe_allow_html=True)
    if radar:
        for r in radar:
            st.sidebar.markdown(f"<span style='color:#38ef7d; font-size:12px;'>{r}</span>", unsafe_allow_html=True)
    else:
        st.sidebar.info("Tarama yapılıyor...")

    # --- ANA EKRAN ---
    if kalan_sure_dk is not None:
        dk = int(kalan_sure_dk); sn = int((kalan_sure_dk - dk) * 60)
        st.markdown(f"""<div class="trial-counter">⏳ DENEME: {dk:02d}:{sn:02d}</div>""", unsafe_allow_html=True)

    usd, eur, ga, gg, pet, btc, eth = get_live_rates()
    st.markdown(f"""<div style="background:#050a14; border-bottom:2px solid #00fff9; padding:5px;">💵 USD: {usd:.2f} ⏐ 🟡 GR ALTIN: {ga:.0f} ⏐ ₿ BTC: ${btc:,.0f}</div>""", unsafe_allow_html=True)
    
    if db["admin"].get("duyuru"): st.error(f"🚨 DUYURU: {db['admin']['duyuru']}")

    if not db[user].get('onay') and not db[user].get('rol') == 'admin':
        st.markdown(f"""<div class="vip-offer-box"><div class="vip-text">🔥 VIP FIRSAT 🔥</div><div class="vip-price">$500 / AY</div></div>""", unsafe_allow_html=True)
        if st.button("💎 SATIN AL", use_container_width=True): st.session_state.odeme_modu = not st.session_state.odeme_modu
        if st.session_state.odeme_modu:
            st.info(f"TRC20: {USDT_ADDRESS}"); tx = st.text_input("TXID"); 
            if st.button("BİLDİR") and tx: 
                if "mesajlar" not in db[user]: db[user]["mesajlar"] = []
                db[user]["mesajlar"].append(f"ÖDEME: {tx}"); save_db(db); st.success("İletildi!")

    st.markdown("---")
    if wg:
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🟢 HAFTALIK KRALLAR</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=pos>%{i["Degisim"]:.1f}</span></div>' for i in wg])}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🗓️ AYLIK ROKETLER</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=pos>%{i["Degisim"]:.1f}</span></div>' for i in mg])}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='top-list-box' style='border-color:#ef473a;'><div class='list-title'>🔴 HAFTALIK KAYIPLAR</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=neg>%{i["Degisim"]:.1f}</span></div>' for i in wl])}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='top-list-box' style='border-color:#ff00ff;'><div class='list-title'>🎰 SPEK / VOLATİL</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=spek>⚡ {i["Volatilite"]:.1f}</span></div>' for i in sp])}</div>", unsafe_allow_html=True)
    else: st.info("Piyasa verileri yükleniyor veya kapalı.")

    st.markdown("---")
    
    # --- İNDİKATÖR SEÇİMİ VE ANALİZ ---
    col_sel, col_ind = st.columns([2, 2])
    with col_sel:
        hisse_secim = st.selectbox("Hisse Analiz Et:", [f"{h}.IS" for h in BIST_HISSELERI if "USD" not in h] + [h for h in BIST_HISSELERI if "USD" in h])
    with col_ind:
        st.write("İndikatörler:")
        c_i1, c_i2 = st.columns(2)
        show_sma = c_i1.checkbox("SMA 20/50", value=True)
        show_bb = c_i2.checkbox("Bollinger Bantları", value=False)

    if st.button("ANALİZ ET 🚀"): st.session_state.secilen_hisse = hisse_secim; st.rerun()
    
    if st.session_state.secilen_hisse:
        res = grafik_ciz(st.session_state.secilen_hisse, show_sma, show_bb)
        if res and res[0]:
            fig, price, pivot, s1, rsi, gauge, ai = res
            c_g1, c_g2 = st.columns([2, 1])
            with c_g1: st.plotly_chart(fig, use_container_width=True)
            with c_g2: 
                st.plotly_chart(gauge, use_container_width=True)
                st.markdown(f"<div class='ai-box'>{ai}</div>", unsafe_allow_html=True)
        else: st.error("Veri Yok.")
        if st.button("Kapat"): st.session_state.secilen_hisse=None; st.rerun()

def payment_screen():
    st.warning("SÜRE DOLDU! LÜTFEN ÖDEME YAPIN."); st.code(USDT_ADDRESS); 
    if st.button("ÇIKIŞ"): st.session_state.login_user=None; st.rerun()

def login_page():
    st.markdown("""<div style="text-align:center; padding:20px;"><h1 class="neon-title">PALA BALİNA AVCISI</h1></div>""", unsafe_allow_html=True)
    col_info, col_login = st.columns([3, 2])
    with col_info:
        st.markdown("""<div class="hero-container"><div class="hero-title">DERİN SULARIN HAKİMİ OL.</div><div class="hero-subtitle">Borsa İstanbul ve Kripto dünyasında kaybolma. Profesyonel balina avcılarının kullandığı terminale hoş geldin.</div><div class="feature-box"><div class="feature-title">🚀 CANLI SİNYAL YAKALAYICI</div><div class="feature-desc">Hangi hisseye balina girdi? RSI, Pivot ve Hacim patlamalarını saniyesinde gör.</div></div><div class="feature-box"><div class="feature-title">🧠 OTOMATİK TEKNİK ANALİZ</div><div class="feature-desc">Destek, Direnç, Pivot noktaları ve Trend analizleri tek tıkla ekranında.</div></div><div class="feature-box"><div class="feature-title">🛡️ VIP KULÜP AYRICALIĞI</div><div class="feature-desc">Sadece seçkin üyeler için özel veriler ve 7/24 piyasa takibi.</div></div><div style="margin-top:20px; text-align:center;"><img src="https://images.unsplash.com/photo-1560275619-4662e36fa65c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" style="width:100%; border-radius:10px; border:1px solid #00fff9; opacity:0.8; box-shadow: 0 0 20px rgba(0, 255, 249, 0.3);"></div></div>""", unsafe_allow_html=True)
    with col_login:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 GİRİŞ YAP", "📝 10 DK ÜCRETSİZ DENE"])
        with tab1:
            k = st.text_input("Kullanıcı Adı", key="l_u"); s = st.text_input("Şifre", type="password", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("TERMİNALE BAĞLAN ⚡", type="primary", use_container_width=True):
                db = load_db()
                if k in db and db[k]['sifre'] == s: st.session_state.login_user = k; st.rerun()
                else: st.error("Hatalı Giriş!")
        with tab2:
            st.markdown("##### Hızlı Kayıt Ol & Başla")
            u = st.text_input("Kullanıcı Adı Belirle", key="r_u"); n = st.text_input("Adın Soyadın", key="r_n"); p = st.text_input("Şifre Belirle", type="password", key="r_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("KAYDI TAMAMLA VE BAŞLA 🚀", type="primary", use_container_width=True):
                db = load_db()
                if u in db: st.warning("Bu isim alınmış!")
                elif u and p:
                    db[u] = {"sifre": p, "isim": n, "onay": False, "rol": "user", "mesajlar": [], "portfoy": [], "kayit_tarihi": time.time()}
                    save_db(db); st.success("Kayıt Başarılı!"); send_telegram(f"🆕 ÜYE: {u}")
        st.markdown("</div>", unsafe_allow_html=True)
    if st.checkbox("Admin Reset"):
        if st.button("Reset"): st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": [], "kayit_tarihi": time.time()}}; save_db(st.session_state.db); st.success("Resetlendi.")

if not st.session_state.login_user:
    login_page()
else:
    u_id = st.session_state.login_user; db = load_db()
    if u_id in db:
        user_data = db[u_id]
        if user_data.get('rol') == 'admin': ana_uygulama()
        elif user_data.get('onay') == True: ana_uygulama()
        else:
            kayit_zamani = user_data.get('kayit_tarihi', 0); gecen_sure_dk = (time.time() - kayit_zamani) / 60
            if gecen_sure_dk < DENEME_SURESI_DK: ana_uygulama(DENEME_SURESI_DK - gecen_sure_dk)
            else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
