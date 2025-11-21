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
st.set_page_config(page_title="Pala Balina Savar", layout="wide", page_icon="🥸")

# --- VERİTABANI ---
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
                "loglar": [] 
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

# --- CSS TASARIMI (SİYAH & ALTIN) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    /* Butonlar */
    div.stButton > button {
        background-color: #000000 !important; color: #FFD700 !important; border: 2px solid #FFD700 !important;
        border-radius: 12px !important; font-weight: bold !important; height: 50px !important; width: 100% !important;
    }
    div.stButton > button:hover { background-color: #FFD700 !important; color: #000000 !important; transform: scale(1.02) !important; }
    
    /* Inputlar */
    .stTextInput input { background-color: #111 !important; color: #FFD700 !important; border: 1px solid #555 !important; }
    
    /* Sticker */
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    
    /* Kartlar */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } .sell { background-color: #450a0a; color: #f87171; } 
    .future { background-color: #4c1d95; color: #a78bfa; border: 1px solid #a78bfa; }
    
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# --- LİSTELER ---
bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

# --- LOG SİSTEMİ ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][-1]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
    except: pass

# ==========================================
# 1. YÖNETİM PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 PALA PANELİ")
    menu = st.sidebar.radio("Yönetim:", ["Üyeler & Onay", "Gelen Mesajlar"])
    db = load_db()
    
    if menu == "Üyeler & Onay":
        st.subheader("👥 Üye Yönetimi")
        uye_data = []
        for k, v in db.items():
            if k != "admin":
                durum = "✅ Aktif" if v.get('onay') else "❌ Bekliyor"
                uye_data.append({"Kullanıcı": k, "İsim": v.get('isim', '-'), "Durum": durum})
        if len(uye_data) > 0:
            st.table(pd.DataFrame(uye_data))
            col1, col2 = st.columns(2)
            with col1:
                onaysizlar = [u['Kullanıcı'] for u in uye_data if u['Durum'] == "❌ Bekliyor"]
                if onaysizlar:
                    u_app = st.selectbox("Onayla:", onaysizlar)
                    if st.button("ONAYLA ✅"):
                        db[u_app]['onay'] = True; save_db(db); st.success(f"{u_app} onaylandı!"); time.sleep(1); st.rerun()
            with col2:
                tum = [u['Kullanıcı'] for u in uye_data]
                if tum:
                    u_del = st.selectbox("Sil:", tum)
                    if st.button("SİL 🗑️"):
                        del db[u_del]; save_db(db); st.warning(f"{u_del} silindi!"); time.sleep(1); st.rerun()
        else: st.info("Üye yok.")

    elif menu == "Gelen Mesajlar":
        st.subheader("📩 Bildirimler")
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                with st.expander(f"👤 {v.get('isim','-')} ({k})", expanded=True):
                    for msg in v['mesajlar']: st.info(msg)

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = st.session_state.db[st.session_state.login_user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Erişim Aktif ✅")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.login_user = None; st.rerun()

    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    # --- MENÜ SEÇİMİ (EKSİK OLAN KISIM EKLENDİ) ---
    menu = st.radio("NAVİGASYON:", ["📊 PİYASA RADARI", "🔥 ISI HARİTASI", "📒 KARA KAPLI DEFTER"], horizontal=True)
    st.divider()

    # ----------------------------------
    # MODÜL 1: KARA KAPLI DEFTER
    # ----------------------------------
    if menu == "📒 KARA KAPLI DEFTER":
        st.subheader("📜 Sinyal Geçmişi")
        db = load_db()
        loglar = db["admin"].get("loglar", [])
        if loglar:
            for log in loglar: st.code(log)
        else: st.warning("Henüz kayıtlı hareket yok.")
        if st.button("Defteri Temizle 🗑️"):
            db["admin"]["loglar"] = []; save_db(db); st.rerun()

    # ----------------------------------
    # MODÜL 2: ISI HARİTASI
    # ----------------------------------
    elif menu == "🔥 ISI HARİTASI":
        st.subheader("🌍 PİYASANIN RÖNTGENİ")
        tur = st.selectbox("Piyasa:", ["BIST", "KRİPTO"])
        liste = bist_listesi if tur == "BIST" else kripto_listesi
        if st.button("HARİTAYI ÇİZ 🗺️"):
            with st.spinner("Veriler işleniyor..."):
                data = []
                for sym in liste:
                    try:
                        t = yf.Ticker(sym); info = t.fast_info
                        fiyat = info.last_price; prev = info.previous_close
                        degisim = ((fiyat - prev) / prev) * 100
                        hacim = info.last_volume
                        if "HDFGS" in sym: hacim = hacim * 5 # HDFGS büyük görünsün
                        data.append({"Sembol": sym.replace(".IS","").replace("-USD",""), "Degisim": degisim, "Hacim": hacim, "Fiyat": fiyat})
                    except: pass
                
                if data:
                    df_map = pd.DataFrame(data)
                    fig = px.treemap(df_map, path=['Sembol'], values='Hacim', color='Degisim',
                                     color_continuous_scale=['red', 'black', 'green'], color_continuous_midpoint=0, hover_data=['Fiyat'])
                    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=600)
                    st.plotly_chart(fig, use_container_width=True)
                else: st.error("Veri alınamadı.")

    # ----------------------------------
    # MODÜL 3: PİYASA RADARI (ANA MODÜL)
    # ----------------------------------
    elif menu == "📊 PİYASA RADARI":
        
        # ŞANS ÇARKI
        if st.button("🎲 PALA BANA KIYAK YAP (GÜNÜN HİSSESİ)"):
            secilen = random.choice(bist_listesi)
            st.balloons()
            st.success(f"🎰 GÜNÜN ŞANSLI HİSSESİ: **{secilen.replace('.IS','')}**")
            st.session_state.secilen_hisse = secilen
            st.rerun()

        # ARAMA VE GRAFİK
        c_s1, c_s2 = st.columns([3,1])
        arama = c_s1.text_input("Hisse/Coin Ara:", placeholder="HDFGS, BTC...").upper()
        if c_s2.button("GRAFİK AÇ 🚀"):
            symbol = f"{arama}.IS" if "-" not in arama and ".IS" not in arama and "USD" not in arama else arama
            st.session_state.secilen_hisse = symbol
            st.rerun()

        if st.session_state.secilen_hisse:
            try:
                df = yf.download(st.session_state.secilen_hisse, period="6mo", interval="1d", progress=False)
                if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                if not df.empty:
                    prev = df.iloc[-2]; pivot = (prev['High']+prev['Low']+prev['Close'])/3
                    r1=(2*pivot)-prev['Low']; s1=(2*pivot)-prev['High']
                    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                    fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text="DİRENÇ"); fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text="DESTEK")
                    fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
                    st.info(f"📈 {st.session_state.secilen_hisse} Grafiği"); st.plotly_chart(fig, use_container_width=True)
            except: st.error("Grafik çizilemedi.")
            if st.button("Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()
            st.divider()

        # TARAMA FONKSİYONU
        @st.cache_data(ttl=180, show_spinner=False)
        def verileri_getir(liste, piyasa_tipi):
            bulunanlar = []; toplam = len(liste); bar = st.progress(0, text=f"{piyasa_tipi} Taranıyor...")
            for i, symbol in enumerate(liste):
                try:
                    df = yf.download(symbol, period="3d", interval="1h", progress=False)
                    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                    if len(df) > 10:
                        son = df.iloc[-1]; hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]; kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                        fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                        delta = df['Close'].diff(); gain = delta.where(delta>0,0).rolling(14).mean(); loss = (-delta.where(delta<0,0)).rolling(14).mean(); rs=gain/loss; rsi=100-(100/(1+rs)).iloc[-1]
                        
                        durum = None; renk = "gray"; aciklama = ""
                        if "HDFGS" in symbol:
                            durum = "HDFGS HAREKETLİ 🦅" if kat > 1.2 else "HDFGS SAKİN"; renk = "buy" if degisim>0 else "sell"; aciklama = "Takipte..."
                            if kat > 1.2: log_ekle(f"HDFGS Hareketlendi! Fiyat: {fiyat:.2f}")
                        elif kat > 2.5:
                            durum = "BALİNA 🚀" if degisim > 0 else "SATIŞ 🔻"; renk = "buy" if degisim > 0 else "sell"; aciklama = f"Hacim {kat:.1f}x"
                            log_ekle(f"{symbol} BALİNA! Fiyat: {fiyat:.2f} ({'Giriş' if degisim>0 else 'Çıkış'})")
                        elif rsi < 35 and kat > 1.2:
                            durum = "SİNSİ TOPLAMA 🕵️"; renk = "future"; aciklama = "Dipte Hacim"
                        
                        if durum:
                            isim = symbol.replace(".IS", "").replace("-USD", "")
                            bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "HacimKat": kat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Kod": symbol})
                    bar.progress((i + 1) / toplam); time.sleep(0.01)
                except: continue
            bar.empty()
            return bulunanlar

        tab1, tab2 = st.tabs(["🏙️ BIST", "₿ KRİPTO"])
        with tab1:
            if st.button("TAHTALARI TARA 📡", key="bist_btn"): st.cache_data.clear(); st.rerun()
            sonuclar = verileri_getir(bist_listesi, "BIST")
            if sonuclar:
                cols = st.columns(2)
                for i, veri in enumerate(sonuclar):
                    with cols[i % 2]:
                        ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                        st.markdown(f"""<div class="balina-karti bist-card {ozel}"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"b_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
            else: st.info("Pala şu an çay içiyor.")
        with tab2:
            if st.button("COINLERİ TARA 📡", key="kripto_btn"): st.cache_data.clear(); st.rerun()
            sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
            if sonuclar_kripto:
                cols = st.columns(2)
                for i, veri in enumerate(sonuclar_kripto):
                    with cols[i % 2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"c_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
            else: st.info("Kripto sakin.")

# ==========================================
# 5. LOGIN / PAYMENT
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
    with tab1:
        kul = st.text_input("Kullanıcı Adı"); sif = st.text_input("Şifre", type="password")
        if st.checkbox("Sıfırla (Hata Alırsan)"):
            if st.button("SİSTEMİ ONAR"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": []}}
                save_db(st.session_state.db); st.success("Admin Hazır")
        if st.button("GİRİŞ"):
            db=load_db()
            if kul in db and db[kul]['sifre']==sif: st.session_state.login_user=kul; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("Hatalı!")
    with tab2:
        y_kul = st.text_input("Yeni Nick"); y_ad = st.text_input("Ad Soyad"); y_sif = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT OL"):
            db=load_db()
            if y_kul not in db: db[y_kul]={"sifre":y_sif, "isim":y_ad, "onay":False, "rol":"user", "mesajlar":[]}; save_db(db); st.success("Kaydolundu!")
            else: st.error("Alınmış!")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 ONAY BEKLENİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK: $500</h2><p>Ödemenizi yapın ve bildirin.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='odeme-kutu'><strong>USDT</strong><br><code>TXa...</code></div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("Dekont Bilgisi"); 
        if st.button("GÖNDER"):
            u=st.session_state.login_user; db=load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"]=[]
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("İletildi.")
    if st.button("Çıkış"): st.session_state.login_user=None; st.rerun()

# ROUTER
if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
