import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala Balina Savar", layout="wide", page_icon="🥸")

# --- VERİTABANI SİSTEMİ ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": []}}
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session State Başlatma
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- CSS TASARIMI (SİYAH & ALTIN BUTONLAR) ---
st.markdown("""
    <style>
    /* GENEL SAYFA */
    .stApp { background-color: #000000; color: #e5e5e5; }
    
    /* --- BUTON TASARIMI (PALA STİLİ) --- */
    .stButton > button {
        width: 100%;
        background-color: #000000 !important; /* Siyah Zemin */
        color: #FFD700 !important; /* Altın Yazı */
        border: 2px solid #FFD700 !important; /* Altın Çerçeve */
        border-radius: 10px !important;
        height: 50px;
        font-size: 16px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    /* Üzerine Gelince (Hover) */
    .stButton > button:hover {
        background-color: #FFD700 !important; /* Zemin Altın Olsun */
        color: #000000 !important; /* Yazı Siyah Olsun */
        box-shadow: 0 0 15px #FFD700 !important; /* Parlama Efekti */
        border-color: #FFD700 !important;
        transform: scale(1.02);
    }
    
    /* Tıklayınca (Active) */
    .stButton > button:active {
        background-color: #d4af37 !important;
        color: black !important;
    }
    
    /* GİRİŞ KUTULARI (INPUT) */
    .stTextInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #FFD700 !important;
        border: 1px solid #FFD700 !important;
    }
    
    /* PALA STICKER */
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    
    /* VIP KART */
    .vip-card { background: linear-gradient(135deg, #111 0%, #000 100%); border: 2px solid #FFD700; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 30px rgba(255, 215, 0, 0.15); }
    .odeme-kutu { background-color: #111; padding: 15px; border-radius: 10px; border: 1px solid #333; border-left: 5px solid #FFD700; margin-bottom: 10px; }
    .onay-bekliyor { background-color: #220; color: #FFD700; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #FFD700; margin-top: 20px; }
    
    /* Balina Kartları */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; position: relative; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; border: 1px solid #34d399; } 
    .sell { background-color: #450a0a; color: #f87171; border: 1px solid #f87171; } 
    .breakout { background-color: #312e81; color: #a78bfa; border: 1px solid #a78bfa; animation: flash 1s infinite; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. YÖNETİM PANELİ (ADMIN)
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 PALA PANELİ")
    st.sidebar.info("Yetkili: Admin")
    
    menu = st.sidebar.radio("Yönetim:", ["Üyeler & Onay", "Gelen Mesajlar"])
    db = load_db() 
    
    if menu == "Üyeler & Onay":
        st.subheader("👥 Üye Listesi")
        uye_listesi = []
        for k, v in db.items():
            if k != "admin":
                durum = "✅ Aktif" if v.get('onay') else "❌ Bekliyor"
                uye_listesi.append({"Kullanıcı": k, "İsim": v.get('isim', '-'), "Durum": durum})
        
        if len(uye_listesi) > 0:
            st.table(pd.DataFrame(uye_listesi))
            col1, col2 = st.columns(2)
            with col1:
                onaysizlar = [u['Kullanıcı'] for u in uye_listesi if u['Durum'] == "❌ Bekliyor"]
                if onaysizlar:
                    user_to_approve = st.selectbox("Onaylanacak Kişi:", onaysizlar)
                    if st.button("YETKİ VER (ONAYLA) ✅"):
                        db[user_to_approve]['onay'] = True
                        save_db(db)
                        st.success(f"{user_to_approve} onaylandı!")
                        time.sleep(1)
                        st.rerun()
            with col2:
                tum_uyeler = [u['Kullanıcı'] for u in uye_listesi]
                if tum_uyeler:
                    user_to_delete = st.selectbox("Silinecek Kişi:", tum_uyeler)
                    if st.button("ÜYELİĞİ SİL 🗑️"):
                        del db[user_to_delete]
                        save_db(db)
                        st.warning(f"{user_to_delete} silindi!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.info("Sistemde kayıtlı üye yok.")

    elif menu == "Gelen Mesajlar":
        st.subheader("📩 Ödeme Bildirimleri")
        mesaj_var = False
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                mesaj_var = True
                st.markdown(f"### 👤 {v['isim']} ({k})")
                for msg in v['mesajlar']:
                    st.info(msg)
        if not mesaj_var:
            st.info("Okunmamış mesaj yok.")

# ==========================================
# 2. ÖDEME VE BEKLEME EKRANI
# ==========================================
def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 HESAP ONAY BEKLİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK ÜCRETİ: $500</h2><p>Pala Balina Savar sistemine erişmek için ödeme yapmanız gerekmektedir.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme Bilgileri")
        st.markdown("<div class='odeme-kutu'><strong>₿ KRİPTO (USDT)</strong><br><code>TXaBCdef1234567890...</code></div>", unsafe_allow_html=True)
        st.markdown("<div class='odeme-kutu'><strong>🏦 BANKA (IBAN)</strong><br><code>TR12 0000 ... (Pala Yazılım)</code></div>", unsafe_allow_html=True)
        
    with col2:
        st.subheader("💬 Bildirim Gönder")
        user_msg = st.text_area("Dekont No veya Mesajınız:", placeholder="Örn: Ahmet Yılmaz, gönderdim.")
        if st.button("ADMİN'E GÖNDER 📨"):
            kullanici = st.session_state.login_user
            db = load_db()
            if kullanici in db:
                if "mesajlar" not in db[kullanici]: db[kullanici]["mesajlar"] = []
                db[kullanici]["mesajlar"].append(f"[{datetime.now().strftime('%d/%m %H:%M')}] {user_msg}")
                save_db(db)
                st.success("İletildi! Admin onayı bekleniyor.")
    
    st.markdown("---")
    st.markdown("<div class='onay-bekliyor'>⏳ Hesabınız incelemede. Onay sonrası otomatik açılır.</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([3,1])
    if c1.button("🔄 ONAY DURUMUMU KONTROL ET"):
        updated_db = load_db()
        user = st.session_state.login_user
        if updated_db[user]['onay'] == True:
            st.session_state.db = updated_db
            st.success("✅ ONAYLANDINIZ! Yönlendiriliyorsunuz...")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Henüz onaylanmamış.")
    if c2.button("Çıkış"):
        st.session_state.login_user = None
        st.rerun()

# ==========================================
# 3. ANA UYGULAMA (PRO ANALİZ)
# ==========================================
def ana_uygulama():
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = st.session_state.db[st.session_state.login_user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Erişim Aktif ✅")
    with col_head[1]:
        if st.button("GÜVENLİ ÇIKIŞ"):
            st.session_state.login_user = None
            st.rerun()

    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    def grafik_ciz(symbol):
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if not df.empty:
                last = df.iloc[-1]; prev = df.iloc[-2]
                pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
                r1 = (2 * pivot) - prev['Low']; s1 = (2 * pivot) - prev['High']
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
                fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"DİRENÇ: {r1:.2f}")
                fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"DESTEK: {s1:.2f}")
                fig.update_layout(title=f"{symbol} Analiz", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
                return fig
        except: return None

    if st.session_state.secilen_hisse:
        st.info(f"📈 {st.session_state.secilen_hisse} Grafiği")
        fig = grafik_ciz(st.session_state.secilen_hisse)
        if fig: st.plotly_chart(fig, use_container_width=True)
        if st.button("Grafiği Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()
        st.divider()

    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

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
                    son = df.iloc[-1]; prev = df.iloc[-15]
                    pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
                    r1 = (2 * pivot) - prev['Low']; s1 = (2 * pivot) - prev['High']
                    hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                    kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                    fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                    
                    durum = None; renk = "gray"; aciklama = ""; kirilim = ""
                    if fiyat > r1: kirilim = "DİRENÇ KIRILDI 💥"
                    elif fiyat < s1: kirilim = "DESTEK KIRILDI 🩸"
                    
                    if "HDFGS" in symbol:
                        if kat > 1.2: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy" if degisim>0 else "sell"; aciklama = "Anlık Hacim"; oncelik = 999
                        else: durum = "HDFGS SAKİN"; aciklama = "Takipte..."; oncelik = 999
                    elif kat > 2.5 or (kat > 1.5 and kirilim != ""):
                        if degisim > 0.5: durum = "BALİNA GİRDİ 🚀"; renk = "buy" if kirilim == "" else "breakout"; aciklama = f"Hacim {kat:.1f}x"; oncelik = kat
                        elif degisim < -0.5: durum = "BALİNA ÇIKTI 🔻"; renk = "sell"; aciklama = "Yüklü Satış"; oncelik = kat
                        if kirilim: aciklama += f" | {kirilim}"

                    if durum:
                        isim = symbol.replace(".IS", "").replace("-USD", "")
                        bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "HacimKat": kat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Oncelik": oncelik, "Destek": s1, "Direnc": r1, "Kod": symbol})
                bar.progress((i + 1) / toplam); time.sleep(0.01)
            except: continue
        bar.empty()
        bulunanlar = sorted(bulunanlar, key=lambda x: x['Oncelik'], reverse=True)
        return bulunanlar[:20]

    tab1, tab2 = st.tabs(["🏙️ BIST", "₿ KRİPTO"])
    with tab1:
        if st.button("TAHTALARI TARA 📡", key="bist_btn"): st.cache_data.clear(); st.rerun()
        sonuclar = verileri_getir(bist_listesi, "BIST")
        if sonuclar:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    st.markdown(f"""<div class="balina-karti bist-card {ozel}"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div><div class="seviye-kutu"><span style="color:#4ade80;">🛡️ S: {veri['Destek']:.2f}</span><span style="color:#f87171;">🧱 R: {veri['Direnc']:.2f}</span></div></div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK AÇ ({veri['Sembol']}) 📈", key=f"btn_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
        else: st.info("Pala şu an çay içiyor.")
    with tab2:
        if st.button("COINLERİ TARA 📡", key="kripto_btn"): st.cache_data.clear(); st.rerun()
        sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
        if sonuclar_kripto:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar_kripto):
                with cols[i % 2]:
                    st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div><div class="seviye-kutu"><span style="color:#4ade80;">🛡️ S: {veri['Destek']:.4f}</span><span style="color:#f87171;">🧱 R: {veri['Direnc']:.4f}</span></div></div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK AÇ ({veri['Sembol']}) 📈", key=f"btn_cr_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
        else: st.info("Kripto sakin.")

# ==========================================
# 5. LOGIN / REGISTER EKRANI
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL (Üye Ol)"])
    
    with tab1:
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        
        if st.checkbox("Veritabanını Sıfırla (Hata Alırsan Bas)"):
            if st.button("SİSTEMİ ONAR 🛠️"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": []}}
                save_db(st.session_state.db)
                st.success("Sistem onarıldı! Admin ile girebilirsin.")

        if st.button("GİRİŞ 🚀"):
            db = load_db()
            if kullanici in db and db[kullanici]['sifre'] == sifre:
                st.session_state.login_user = kullanici
                st.success("Giriş Başarılı!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Hatalı Kullanıcı Adı veya Şifre!")

    with tab2:
        yeni_kul = st.text_input("Kullanıcı Adı (Nick)")
        yeni_isim = st.text_input("Adınız Soyadınız")
        yeni_sifre = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT OL 📝"):
            db = load_db()
            if yeni_kul in db:
                st.error("Bu isim alınmış!")
            elif yeni_kul and yeni_sifre:
                db[yeni_kul] = {"sifre": yeni_sifre, "isim": yeni_isim, "onay": False, "rol": "user", "mesajlar": []}
                save_db(db)
                st.success("Kayıt Başarılı! 'Giriş Yap' sekmesinden girebilirsiniz.")
            else:
                st.warning("Boş alan bırakmayınız.")

# ==========================================
# ROUTER (YÖNLENDİRİCİ)
# ==========================================
if st.session_state.login_user is None:
    login_page()
else:
    user = st.session_state.login_user
    db = load_db()
    if user in db:
        user_data = db[user]
        st.session_state.db = db # Session'ı güncelle
        if user_data.get('rol') == 'admin': ana_uygulama()
        elif user_data.get('onay'): ana_uygulama()
        else: payment_screen()
    else:
        st.session_state.login_user = None
        st.rerun()
