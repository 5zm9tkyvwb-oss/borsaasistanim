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
st.set_page_config(page_title="Pala Balina Savar", layout="wide", page_icon="🥸")

# ==========================================
# 🚨 TELEGRAM AYARLARI
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

# --- VERİTABANI SİSTEMİ (DÜZELTİLMİŞ) ---
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

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    /* Butonlar */
    div.stButton > button {
        background-color: #000000 !important; color: #FFD700 !important; 
        border: 2px solid #FFD700 !important; border-radius: 12px !important; 
        font-weight: bold !important; height: 50px !important; width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { 
        background-color: #FFD700 !important; color: #000000 !important; 
        transform: scale(1.02) !important; 
    }
    
    /* Inputlar */
    .stTextInput input, .stNumberInput input { 
        background-color: #111 !important; color: #FFD700 !important; 
        border: 1px solid #555 !important; 
    }
    
    /* Pala Sticker */
    .pala-sticker { 
        position: fixed; top: 10px; right: 10px; 
        background: linear-gradient(45deg, #FFD700, #FFA500); 
        color: black; padding: 8px 15px; border-radius: 20px; 
        border: 3px solid #000; text-align: center; font-weight: bold; 
        z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); 
        transform: rotate(5deg); 
    }
    
    /* Kartlar */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } 
    .sell { background-color: #450a0a; color: #f87171; } 
    
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    
    @keyframes pulse { 
        0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 
        50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 
        100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 
    }

    /* TOP 10 KARTLARI */
    .top10-card {
        background-color: #0a0a0a; border: 1px solid #4ade80; border-radius: 10px;
        padding: 10px; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(74, 222, 128, 0.1);
    }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# --- FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][0]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
            send_telegram(f"🔔 {mesaj}")
    except: pass

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- TOP 10 (HAFTALIK YÜKSELENLER) ---
@st.cache_data(ttl=3600)
def get_weekly_top10():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "MGROS.IS", "SOKM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "TCELL.IS", "VESTL.IS", "ARCLK.IS", "KOZAL.IS", "PETKM.IS", "PGSUS.IS"]
    results = []
    for s in candidates:
        try:
            df = yf.download(s, period="5d", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if len(df) > 1:
                ilk = df['Open'].iloc[0]; son = df['Close'].iloc[-1]
                degisim = ((son - ilk) / ilk) * 100
                if degisim > 0:
                    results.append({"Sembol": s.replace(".IS",""), "Fiyat": son, "Degisim": degisim})
        except: pass
    return sorted(results, key=lambda x: x['Degisim'], reverse=True)[:10]

# --- GRAFİK MOTORU ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            prev = df.iloc[-2]; pivot = (prev['High']+prev['Low']+prev['Close'])/3
            r1=(2*pivot)-prev['Low']; s1=(2*pivot)-prev['High']
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text="DİRENÇ"); fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text="DESTEK")
            fig.update_layout(title=f"{symbol} Analiz", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            return fig, df.iloc[-1]['Close'], s1, r1
    except: return None, None, None, None

# ==========================================
# ANA UYGULAMA
# ==========================================
def ana_uygulama():
    user = st.session_state.login_user; db = st.session_state.db
    
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = db[user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Panel")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"): st.session_state.login_user=None; st.rerun()

    if db[user].get('rol') == 'admin':
        st.sidebar.title("👑 ADMİN PANELİ")
        if st.sidebar.checkbox("Üye Listesi"): st.sidebar.write(db)

    # --- 1. VİTRİN: HAFTANIN YILDIZLARI (TOP 10) ---
    st.markdown("### 🏆 BU HAFTANIN KRALLARI (TOP 10)")
    top10 = get_weekly_top10()
    if top10:
        cols = st.columns(5)
        for i, item in enumerate(top10):
            if i < 5:
                with cols[i]:
                    st.markdown(f"""<div class="top10-card"><h3 style="margin:0; color:#FFD700;">{item['Sembol']}</h3><h2 style="margin:0; color:white;">{item['Fiyat']:.2f}</h2><span style="color:#4ade80;">+%{item['Degisim']:.1f}</span></div>""", unsafe_allow_html=True)
        cols2 = st.columns(5)
        for i, item in enumerate(top10):
            if i >= 5:
                with cols2[i-5]:
                    st.markdown(f"""<div class="top10-card"><h3 style="margin:0; color:#FFD700;">{item['Sembol']}</h3><h2 style="margin:0; color:white;">{item['Fiyat']:.2f}</h2><span style="color:#4ade80;">+%{item['Degisim']:.1f}</span></div>""", unsafe_allow_html=True)
    else: st.info("Veriler Yükleniyor...")
    
    st.divider()

    # MENÜ
    menu = st.radio("NAVİGASYON:", ["📊 HİSSE & COIN TARAMA", "💼 CÜZDAN", "🔥 ISI HARİTASI", "📒 LOGLAR"], horizontal=True)
    st.divider()

    # --- MODÜL: TARAMA VE LİSTELEME (HDFGS ÖZEL) ---
    if menu == "📊 HİSSE & COIN TARAMA":
        
        # GRAFİK AÇMA
        if st.session_state.secilen_hisse:
            st.info(f"📈 {st.session_state.secilen_hisse} Grafiği")
            fig, fiyat, s1, r1 = grafik_ciz(st.session_state.secilen_hisse)
            if fig:
                k1, k2, k3 = st.columns(3)
                k1.metric("FİYAT", f"{fiyat:.2f}")
                k2.metric("DESTEK", f"{s1:.2f}")
                k3.metric("DİRENÇ", f"{r1:.2f}")
                st.plotly_chart(fig, use_container_width=True)
            if st.button("Kapat X"): st.session_state.secilen_hisse = None; st.rerun()

        # LİSTELER
        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
        kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]
        
        telegram_aktif = st.checkbox("🔔 Telegram Bildirimi Aç")

        @st.cache_data(ttl=180, show_spinner=False)
        def tarama_yap(liste, tip, bildirim):
            bulunanlar = []; bar = st.progress(0, text=f"{tip} Taranıyor...")
            for i, symbol in enumerate(liste):
                try:
                    df = yf.download(symbol, period="3d", interval="1h", progress=False)
                    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                    if len(df) > 10:
                        son = df.iloc[-1]; hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]; kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                        fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                        
                        durum = None; renk = "gray"; aciklama = ""
                        # HDFGS HER ZAMAN LİSTEDE
                        if "HDFGS" in symbol:
                            if kat > 1.1: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy"; aciklama = "Hacim Artışı Var"
                            else: durum = "HDFGS TAKİPTE"; aciklama = "Sakin Seyir"
                        # DİĞERLERİ İÇİN FİLTRE (Alıcılı ve Hacimli)
                        elif kat > 2.0 and degisim > 0.5:
                            durum = "POTANSİYEL 🚀"; renk = "buy"; aciklama = f"Hacim {kat:.1f}x & Alıcılı"
                        
                        if durum:
                            isim = symbol.replace(".IS", "").replace("-USD", "")
                            bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Kod": symbol})
                            if bildirim and "HDFGS" in symbol and kat > 1.1: log_ekle(f"HDFGS Hareketlendi! {fiyat:.2f}")
                    bar.progress((i+1)/len(liste)); time.sleep(0.01)
                except: continue
            bar.empty()
            # Sıralama: HDFGS en üstte, sonra değişim yüzdesine göre
            return sorted(bulunanlar, key=lambda x: (x['Sembol'] != "HDFGS", -x['Degisim']))

        t1, t2 = st.tabs(["🏙️ BIST FIRSATLAR", "₿ KRİPTO FIRSATLAR"])
        with t1:
            if st.button("BIST TARA 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(bist_listesi, "BIST", telegram_aktif)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        ozel = "hdfgs-ozel" if "HDFGS" in v['Sembol'] else ""
                        st.markdown(f"""<div class="balina-karti bist-card {ozel}"><h4>{v['Sembol']}</h4><p>{v['Fiyat']:.2f} TL <span style='color:#4ade80'>(%{v['Degisim']:.2f})</span></p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style='font-size:10px; margin-top:5px'>{v['Aciklama']}</p></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"b_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
            else: st.info("Şu an alıcılı tahta yok.")
        with t2:
            if st.button("KRİPTO TARA 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(kripto_listesi, "KRIPTO", telegram_aktif)
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><h4>{v['Sembol']}</h4><p>${v['Fiyat']:.4f} <span style='color:#4ade80'>(%{v['Degisim']:.2f})</span></p><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style='font-size:10px; margin-top:5px'>{v['Aciklama']}</p></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"c_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
            else: st.info("Sakin.")

    # --- MODÜL: CÜZDAN ---
    elif menu == "💼 CÜZDAN":
        st.subheader("💰 Varlık Yönetimi")
        with st.expander("➕ Hisse Ekle"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.text_input("Sembol", "HDFGS.IS").upper()
            y_mal = c2.number_input("Maliyet", value=2.63)
            y_adt = c3.number_input("Adet", value=194028)
            if c4.button("KAYDET"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != y_sem]
                db[user]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("Kaydedildi!"); st.rerun()

        if "portfoy" in db[user] and db[user]["portfoy"]:
            total_val = 0; total_profit = 0; pie_data = []; table_data = []
            for p in db[user]["portfoy"]:
                try:
                    fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                    val = fiyat * p['adet']; profit = (fiyat - p['maliyet']) * p['adet']
                    total_val += val; total_profit += profit
                    table_data.append({"Hisse": p['sembol'], "Fiyat": f"{fiyat:.2f}", "Kar": f"{profit:,.0f}"})
                    pie_data.append({"Sembol": p['sembol'], "Deger": val})
                except: pass
            
            k1, k2 = st.columns(2)
            k1.metric("TOPLAM SERVET", f"{total_val:,.0f} TL")
            k2.metric("NET KAR", f"{total_profit:,.0f} TL", delta_color="normal")
            
            c_pie, c_tab = st.columns([1, 2])
            with c_pie:
                if pie_data:
                    fig_pie = px.pie(pd.DataFrame(data_pie), values='Deger', names='Sembol', hole=0.4)
                    fig_pie.update_layout(template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            with c_tab: st.table(pd.DataFrame(table_data))
            
            sil = st.selectbox("Sil:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("HİSSEYİ SİL"):
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sil]; save_db(db); st.rerun()

    # --- MODÜL: ISI HARİTASI ---
    elif menu == "🔥 ISI HARİTASI":
        st.subheader("🌍 PİYASA RÖNTGENİ")
        if st.button("HARİTAYI ÇİZ 🗺️"):
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
                    st.plotly_chart(fig, use_container_width=True)

    # --- MODÜL: LOGLAR ---
    elif menu == "📒 LOGLAR":
        st.subheader("📜 Sinyal Geçmişi")
        loglar = db["admin"].get("loglar", [])
        if loglar:
            for log in loglar: st.code(log)
        else: st.warning("Kayıt yok")

# ==========================================
# LOGIN / PAYMENT
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    t1, t2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
    with t1:
        k = st.text_input("Kullanıcı"); s = st.text_input("Şifre", type="password")
        if st.checkbox("Sıfırla"):
            if st.button("SİSTEMİ ONAR"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("Admin Hazır")
        if st.button("GİRİŞ"):
            db=load_db()
            if k in db and db[k]['sifre']==s: st.session_state.login_user=k; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("Hatalı")
    with t2:
        yk = st.text_input("Yeni Nick"); y_ad = st.text_input("Ad"); ys = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT"):
            db=load_db()
            if yk not in db: db[yk] = {"sifre":ys, "isim":y_ad, "onay":False, "rol":"user", "mesajlar":[], "portfoy":[]}; save_db(db); st.success("Kaydolundu")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 ONAY BEKLENİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK: $500</h2><p>Ödeme Bekleniyor.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='odeme-kutu'><strong>USDT</strong><br>TXa...</div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("Dekont"); 
        if st.button("GÖNDER"):
            u=st.session_state.login_user; db=load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"]=[]
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("İletildi")
    if st.button("Çıkış"): st.session_state.login_user=None; st.rerun()

if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
