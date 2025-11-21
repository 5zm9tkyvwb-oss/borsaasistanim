
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

# --- VERİTABANI FONKSİYONLARI ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        # Dosya yoksa varsayılanı oluştur
        default_db = {
            "admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": []}
        }
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session Başlatma
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state:
    st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state:
    st.session_state.secilen_hisse = None

# ==========================================
# 1. YÖNETİM PANELİ (ADMIN)
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("🛠️ PALA PANELİ")
    menu = st.sidebar.radio("Yönetim:", ["Üyeler & Onay", "Destek Mesajları"])
    
    db = st.session_state.db
    
    if menu == "Üyeler & Onay":
        st.subheader("👥 Üye Listesi")
        uye_listesi = []
        for k, v in db.items():
            if k != "admin":
                uye_listesi.append({"Kullanıcı": k, "İsim": v.get('isim', '-'), "Onay": v.get('onay', False)})
        
        if len(uye_listesi) > 0:
            st.table(pd.DataFrame(uye_listesi))
            col1, col2 = st.columns(2)
            with col1:
                onaysizlar = [u['Kullanıcı'] for u in uye_listesi if not u['Onay']]
                if onaysizlar:
                    user_to_approve = st.selectbox("Onaylanacak Üye", onaysizlar)
                    if st.button("✅ ONAYLA"):
                        db[user_to_approve]['onay'] = True
                        save_db(db)
                        st.success(f"{user_to_approve} onaylandı!")
                        st.rerun()
            with col2:
                tum_uyeler = [u['Kullanıcı'] for u in uye_listesi]
                if tum_uyeler:
                    user_to_delete = st.selectbox("Silinecek Üye", tum_uyeler)
                    if st.button("🗑️ SİL"):
                        del db[user_to_delete]
                        save_db(db)
                        st.warning(f"{user_to_delete} silindi!")
                        st.rerun()
        else:
            st.info("Henüz üye yok.")

    elif menu == "Destek Mesajları":
        st.subheader("📩 Mesajlar")
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                for msg in v['mesajlar']:
                    st.info(f"👤 **{k}:** {msg}")

# ==========================================
# 2. ANA UYGULAMA (BALİNA)
# ==========================================
def main_app():
    # --- CSS ---
    st.markdown("""
        <style>
        .stApp { background-color: #0a0e17; color: white; }
        .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
        .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; position: relative; }
        .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
        .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
        .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
        .buy { background-color: #059669; color: white; } .sell { background-color: #dc2626; color: white; } .breakout { background-color: #7c3aed; color: white; animation: flash 1s infinite; }
        .seviye-kutu { display: flex; justify-content: space-between; font-size: 11px; margin-top: 5px; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 5px; }
        .stButton button { width: 100%; border-radius: 8px; margin-top: 5px; font-weight: bold; border: 1px solid #555; }
        .stButton button:hover { border-color: #FFD700; color: #FFD700; }
        .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
        @keyframes flash { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
        <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
    """, unsafe_allow_html=True)

    col_head = st.columns([8, 2])
    with col_head[0]:
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Kullanıcı: {st.session_state.login_user}")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.login_user = None
            st.rerun()

    # Admin Panelini Göster (Eğer Admisse)
    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    # GRAFİK FONKSİYONU
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

    # LİSTELER & TARAMA
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
# 4. ÖDEME EKRANI (ONAYSIZLAR İÇİN)
# ==========================================
def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 HESAP ONAY BEKLİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK ÜCRETİ: $500</h2><p>Pala Balina Savar sistemine erişmek için ödeme yapmanız gerekmektedir.</p></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme Bilgileri")
        st.warning("Lütfen ödemeyi yapıp dekont gönderin.")
        st.code("USDT (TRC20): TXaBCdef1234567890...")
        st.code("IBAN: TR12 0000 ... (Pala Yazılım)")
        
    with col2:
        st.subheader("💬 Bildirim Gönder")
        user_msg = st.text_area("Mesajınız (Dekont no vb.)")
        if st.button("BİLDİRİM GÖNDER 📨"):
            kullanici = st.session_state.login_user
            db = st.session_state.db
            if "mesajlar" not in db[kullanici]: db[kullanici]["mesajlar"] = []
            db[kullanici]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {user_msg}")
            save_db(db)
            st.success("Admin'e iletildi! Onaylanınca giriş yapabileceksiniz.")
            
    if st.button("Çıkış Yap"):
        st.session_state.login_user = None
        st.rerun()

# ==========================================
# 5. LOGIN / REGISTER EKRANI
# ==========================================
def login_page():
    st.markdown("""
    <div style="text-align:center;">
        <h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL (Üye Ol)"])
    
    with tab1:
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        
        # --- ACİL DURUM SIFIRLAMA BUTONU ---
        # Eğer veritabanı bozulursa buna basarak admini geri getirebilirsin
        if st.checkbox("Veritabanını Sıfırla (Sadece Hata Alırsan Kullan)"):
            if st.button("SİSTEMİ ONAR 🛠️"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": []}}
                save_db(st.session_state.db)
                st.success("Sistem onarıldı! Admin ile girebilirsin.")
        # ------------------------------------

        if st.button("GİRİŞ 🚀"):
            db = st.session_state.db
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
            db = st.session_state.db
            if yeni_kul in db:
                st.error("Bu kullanıcı adı alınmış!")
            elif yeni_kul and yeni_sifre:
                db[yeni_kul] = {"sifre": yeni_sifre, "isim": yeni_isim, "onay": False, "rol": "user", "mesajlar": []}
                save_db(db)
                st.success("Kayıt Başarılı! Şimdi 'Giriş Yap' sekmesinden girebilirsiniz.")
            else:
                st.warning("Alanları doldurun.")

# ==========================================
# ROUTER (YÖNLENDİRİCİ)
# ==========================================
if st.session_state.login_user is None:
    login_page()
else:
    user = st.session_state.login_user
    if user in st.session_state.db: # Kullanıcı veritabanında var mı kontrolü
        user_data = st.session_state.db[user]
        if user_data.get('rol') == 'admin':
            ana_uygulama() # Admin direkt girer
        elif user_data.get('onay'):
            ana_uygulama() # Onaylı üye girer
        else:
            payment_screen() # Onaysız üye ödeme ekranına
    else:
        st.session_state.login_user = None # Hata varsa çıkış yap
        st.rerun()
