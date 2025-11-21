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

# --- VERİTABANI SİSTEMİ ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": []}}
        save_db(default_db)
        return default_db
    try: with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #000000 !important; color: #FFD700 !important; border: 2px solid #FFD700 !important;
        border-radius: 12px !important; font-weight: bold !important; height: 50px !important; width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { background-color: #FFD700 !important; color: #000000 !important; transform: scale(1.02) !important; }
    
    /* KARTLAR */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } .sell { background-color: #450a0a; color: #f87171; } 
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    
    /* INPUT & TEXT */
    .stTextInput input, .stNumberInput input { background-color: #111 !important; color: #FFD700 !important; border: 1px solid #555 !important; }
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def log_ekle(mesaj):
    """Kara Kaplı Deftere Kayıt Atar"""
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        # Aynı mesajın tekrarını önlemek için son mesaja bak
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][-1]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}") # En başa ekle
            # Son 50 kaydı tut
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
    except: pass

# ==========================================
# GRAFİK & ANALİZ MOTORU
# ==========================================
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            prev = df.iloc[-2]
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']; s1 = (2 * pivot) - prev['High']
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"DİRENÇ: {r1:.2f}")
            fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"DESTEK: {s1:.2f}")
            fig.update_layout(title=f"{symbol} Analiz", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            return fig
    except: return None

# ==========================================
# ANA UYGULAMA
# ==========================================
def ana_uygulama():
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = st.session_state.db[st.session_state.login_user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Erişim Aktif ✅")
    with col_head[1]:
        if st.button("GÜVENLİ ÇIKIŞ"):
            st.session_state.login_user = None; st.rerun()

    # Menü
    menu = st.radio("NAVİGASYON:", ["📊 PİYASA TARAMA", "🔥 ISI HARİTASI (HEATMAP)", "📒 KARA KAPLI DEFTER"], horizontal=True)
    st.divider()

    # LİSTELER
    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

    # --- MODÜL 1: ISI HARİTASI (YENİ) ---
    if menu == "🔥 ISI HARİTASI (HEATMAP)":
        st.subheader("🌍 PİYASANIN RÖNTGENİ")
        tur = st.selectbox("Piyasa Seç:", ["BIST", "KRİPTO"])
        liste = bist_listesi if tur == "BIST" else kripto_listesi
        
        if st.button("HARİTAYI OLUŞTUR 🗺️"):
            with st.spinner("Veriler işleniyor..."):
                data = []
                for sym in liste:
                    try:
                        # Son 1 günlük veriyi çekip değişim hesapla
                        t = yf.Ticker(sym)
                        info = t.fast_info
                        fiyat = info.last_price
                        prev = info.previous_close
                        degisim = ((fiyat - prev) / prev) * 100
                        hacim = info.last_volume
                        
                        # HDFGS'yi büyük göster
                        if "HDFGS" in sym: hacim = hacim * 5 
                        
                        data.append({"Sembol": sym.replace(".IS","").replace("-USD",""), "Degisim": degisim, "Hacim": hacim, "Fiyat": fiyat})
                    except: pass
                
                df_map = pd.DataFrame(data)
                
                # Treemap Çizimi
                fig = px.treemap(df_map, path=['Sembol'], values='Hacim',
                                 color='Degisim', color_continuous_scale=['red', 'black', 'green'],
                                 color_continuous_midpoint=0,
                                 hover_data=['Fiyat'])
                fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=600)
                st.plotly_chart(fig, use_container_width=True)

    # --- MODÜL 2: KARA KAPLI DEFTER ---
    elif menu == "📒 KARA KAPLI DEFTER":
        st.subheader("📜 Sinyal Geçmişi")
        st.info("Sistem tarama yaptıkça bulduğu balinaları buraya kaydeder.")
        
        db = load_db()
        loglar = db["admin"].get("loglar", [])
        
        if loglar:
            for log in loglar:
                st.code(log)
        else:
            st.warning("Henüz kayıtlı bir balina hareketi yok.")
            
        if st.button("Defteri Temizle 🗑️"):
            db["admin"]["loglar"] = []
            save_db(db)
            st.rerun()

    # --- MODÜL 3: KLASİK TARAMA ---
    elif menu == "📊 PİYASA TARAMA":
        
        # ŞANS ÇARKI (SÜRPRİZ HİSSE)
        if st.button("🎲 PALA BANA KIYAK YAP (GÜNÜN HİSSESİ)"):
            secilen = random.choice(bist_listesi)
            st.balloons()
            st.success(f"🎰 GÜNÜN ŞANSLI HİSSESİ: **{secilen.replace('.IS','')}**")
            st.session_state.secilen_hisse = secilen
            st.rerun()

        if st.session_state.secilen_hisse:
            st.info(f"📈 {st.session_state.secilen_hisse} Grafiği")
            fig = grafik_ciz(st.session_state.secilen_hisse)
            if fig: st.plotly_chart(fig, use_container_width=True)
            if st.button("Grafiği Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()
            st.divider()

        @st.cache_data(ttl=180, show_spinner=False)
        def verileri_getir(liste, piyasa_tipi):
            bulunanlar = []
            toplam = len(liste)
            bar = st.progress(0, text=f"Pala {piyasa_tipi} Piyasasını Süzüyor...")
            for i, symbol in enumerate(liste):
                try:
                    df = yf.download(symbol, period="3d", interval="1h", progress=False)
                    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                    if len(df) > 10:
                        son = df.iloc[-1]; 
                        hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                        kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                        fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                        
                        durum = None; renk = "gray"; aciklama = ""
                        
                        if "HDFGS" in symbol:
                            if kat > 1.2: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy" if degisim>0 else "sell"; aciklama = "Anlık Hacim"; log_ekle(f"HDFGS HAREKETLENDİ! Fiyat: {fiyat:.2f}")
                            else: durum = "HDFGS SAKİN"; aciklama = "Takipte..."
                        elif kat > 2.5:
                            if degisim > 0.5: 
                                durum = "BALİNA GİRDİ 🚀"; renk = "buy"; aciklama = f"Hacim {kat:.1f}x"
                                log_ekle(f"{symbol} BALİNA GİRİŞİ! Hacim: {kat:.1f}x Fiyat: {fiyat:.2f}")
                            elif degisim < -0.5: 
                                durum = "BALİNA ÇIKTI 🔻"; renk = "sell"; aciklama = "Yüklü Satış"
                                log_ekle(f"{symbol} SATIŞ BASKISI! Fiyat: {fiyat:.2f}")

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
                        if st.button(f"GRAFİK AÇ ({veri['Sembol']}) 📈", key=f"btn_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
            else: st.info("Pala şu an çay içiyor.")
        with tab2:
            if st.button("COINLERİ TARA 📡", key="kripto_btn"): st.cache_data.clear(); st.rerun()
            sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
            if sonuclar_kripto:
                cols = st.columns(2)
                for i, veri in enumerate(sonuclar_kripto):
                    with cols[i % 2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK AÇ ({veri['Sembol']}) 📈", key=f"btn_cr_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
            else: st.info("Kripto sakin.")

# ==========================================
# ÖDEME EKRANI
# ==========================================
def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 HESAP ONAY BEKLİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK ÜCRETİ: $500</h2><p>Ödeme yapmanız gerekmektedir.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme Bilgileri")
        st.markdown("<div class='odeme-kutu'><strong>₿ KRİPTO (USDT)</strong><br><code>TXaBCdef1234567890...</code></div>", unsafe_allow_html=True)
        st.markdown("<div class='odeme-kutu'><strong>🏦 BANKA (IBAN)</strong><br><code>TR12 0000 ... (Pala Yazılım)</code></div>", unsafe_allow_html=True)
        
    with col2:
        st.subheader("💬 Bildirim Gönder")
        user_msg = st.text_area("Dekont No veya Mesajınız:")
        if st.button("ADMİN'E GÖNDER 📨"):
            kullanici = st.session_state.login_user
            db = load_db()
            if kullanici in db:
                if "mesajlar" not in db[kullanici]: db[kullanici]["mesajlar"] = []
                db[kullanici]["mesajlar"].append(f"[{datetime.now().strftime('%d/%m %H:%M')}] {user_msg}")
                save_db(db)
                st.success("Mesaj iletildi!")
    
    if st.button("Çıkış Yap"): st.session_state.login_user = None; st.rerun()

# ==========================================
# LOGIN / REGISTER
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL (Üye Ol)"])
    
    with tab1:
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.checkbox("Veritabanını Sıfırla (Hata Alırsan Bas)"):
            if st.button("SİSTEMİ ONAR 🛠️"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": []}}
                save_db(st.session_state.db)
                st.success("Sistem onarıldı!")
        if st.button("GİRİŞ 🚀"):
            db = load_db()
            if kullanici in db and db[kullanici]['sifre'] == sifre:
                st.session_state.login_user = kullanici
                st.success("Giriş Başarılı!")
                time.sleep(0.5); st.rerun()
            else: st.error("Hatalı Giriş!")

    with tab2:
        yeni_kul = st.text_input("Kullanıcı Adı (Nick)")
        yeni_isim = st.text_input("Adınız Soyadınız")
        yeni_sifre = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT OL 📝"):
            db = load_db()
            if yeni_kul in db: st.error("Bu isim alınmış!")
            elif yeni_kul and yeni_sifre:
                db[yeni_kul] = {"sifre": yeni_sifre, "isim": yeni_isim, "onay": False, "rol": "user", "mesajlar": []}
                save_db(db)
                st.success("Kayıt Başarılı! Şimdi giriş yapın.")
            else: st.warning("Boş alan bırakmayınız.")

if st.session_state.login_user is None: login_page()
else:
    user = st.session_state.login_user
    db = load_db()
    if user in db:
        if db[user].get('onay') or db[user].get('rol') == 'admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
