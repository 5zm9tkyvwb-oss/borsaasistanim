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
        default_db = {
            "admin": {
                "sifre": "pala500", 
                "isim": "Büyük Patron", 
                "onay": True, 
                "rol": "admin", 
                "mesajlar": []
            }
        }
        save_db(default_db)
        return default_db
    
    # --- DÜZELTİLEN KISIM (Satırlar Ayrıldı) ---
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session State Başlatma
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state:
    st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state:
    st.session_state.secilen_hisse = None

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #000000 !important; 
        color: #FFD700 !important; 
        border: 2px solid #FFD700 !important;
        border-radius: 12px !important; 
        font-weight: bold !important; 
        height: 50px !important; 
        width: 100% !important;
    }
    div.stButton > button:hover { 
        background-color: #FFD700 !important; 
        color: #000000 !important; 
        transform: scale(1.02) !important; 
    }
    
    /* INPUT */
    .stTextInput input { 
        background-color: #111 !important; 
        color: #FFD700 !important; 
        border: 1px solid #555 !important; 
    }
    
    /* PALA STICKER */
    .pala-sticker { 
        position: fixed; top: 10px; right: 10px; 
        background: linear-gradient(45deg, #FFD700, #FFA500); 
        color: black; padding: 8px 15px; border-radius: 20px; 
        border: 3px solid #000; text-align: center; font-weight: bold; 
        z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); 
        transform: rotate(5deg); 
    }
    
    /* ARAMA KUTUSU */
    .arama-kutu { background-color: #1f2937; padding: 20px; border-radius: 15px; border: 2px solid #FFD700; text-align: center; margin-bottom: 20px; }
    .buy-zone { color: #4ade80; font-weight: bold; font-size: 18px; }
    .sell-zone { color: #f87171; font-weight: bold; font-size: 18px; }
    
    /* KARTLAR */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } 
    .sell { background-color: #450a0a; color: #f87171; } 
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# --- GRAFİK VE ANALİZ MOTORU ---
def analiz_getir(symbol):
    try:
        # Veri Çek
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): 
            df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            son = df.iloc[-1]
            prev = df.iloc[-2] # Dün
            
            # PİVOT HESAPLAMA
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']  # Direnç 1
            s1 = (2 * pivot) - prev['High'] # Destek 1
            r2 = pivot + (prev['High'] - prev['Low'])
            s2 = pivot - (prev['High'] - prev['Low'])
            
            # Grafik
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            
            # Çizgiler
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"SATIM YERİ (R1): {r1:.2f}")
            fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"ALIM YERİ (S1): {s1:.2f}")
            fig.add_hline(y=pivot, line_dash="dot", line_color="yellow", annotation_text="PİVOT")
            
            fig.update_layout(title=f"{symbol} PALA ANALİZİ", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            
            return fig, son['Close'], s1, r1, s2, r2
    except: 
        return None, None, None, None, None, None

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
                uye_data.append({"Kullanıcı Adı": k, "İsim": v.get('isim', '-'), "Durum": durum})
        
        if len(uye_data) > 0:
            st.table(pd.DataFrame(uye_data))
            col1, col2 = st.columns(2)
            with col1:
                onaysizlar = [u['Kullanıcı Adı'] for u in uye_data if u['Durum'] == "❌ Bekliyor"]
                if onaysizlar:
                    user_to_approve = st.selectbox("Onaylanacak Kişi:", onaysizlar)
                    if st.button("YETKİ VER (ONAYLA)"):
                        db[user_to_approve]['onay'] = True
                        save_db(db)
                        st.success(f"{user_to_approve} onaylandı!")
                        time.sleep(1)
                        st.rerun()
            with col2:
                tum_uyeler = [u['Kullanıcı Adı'] for u in uye_data]
                if tum_uyeler:
                    user_to_delete = st.selectbox("Silinecek Kişi:", tum_uyeler)
                    if st.button("ÜYELİĞİ SİL"):
                        del db[user_to_delete]
                        save_db(db)
                        st.warning(f"{user_to_delete} silindi!")
                        time.sleep(1)
                        st.rerun()
        else: 
            st.info("Kayıtlı üye yok.")

    elif menu == "Gelen Mesajlar":
        st.subheader("📩 Ödeme Bildirimleri")
        mesaj_var = False
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                mesaj_var = True
                with st.expander(f"👤 {v.get('isim','-')} ({k})", expanded=True):
                    for msg in v['mesajlar']: st.info(msg)
        if not mesaj_var: st.info("Okunmamış mesaj yok.")

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = st.session_state.db[st.session_state.login_user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin Patron | VIP Panel")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.login_user = None
            st.rerun()

    # Admin Paneli (Varsa)
    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    # --- MERKEZİ ARAMA ---
    st.markdown("---")
    st.markdown("<h3 style='text-align:center; color:#FFD700;'>🔍 HİSSE / COIN SORGULA</h3>", unsafe_allow_html=True)
    
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        arama = st.text_input("Hisse Kodu (Örn: HDFGS, THYAO, BTC-USD)", placeholder="Kodu buraya yaz...").upper()
    with col_search2:
        st.write("") 
        st.write("") 
        ara_btn = st.button("ANALİZ ET 🚀")

    if ara_btn and arama:
        if "-" not in arama and ".IS" not in arama and "USD" not in arama: symbol = f"{arama}.IS"
        else: symbol = arama
            
        with st.spinner(f"{symbol} İnceleniyor..."):
            fig, fiyat, s1, r1, s2, r2 = analiz_getir(symbol)
            if fig:
                st.success(f"✅ {symbol} Analizi Hazır!")
                k1, k2, k3 = st.columns(3)
                k1.metric("ANLIK FİYAT", f"{fiyat:.2f}")
                k2.markdown(f"<div style='text-align:center; border:1px solid green; padding:10px; border-radius:10px;'><span style='color:gray'>GÜVENLİ ALIM YERİ</span><br><span class='buy-zone'>{s1:.2f} - {s2:.2f}</span></div>", unsafe_allow_html=True)
                k3.markdown(f"<div style='text-align:center; border:1px solid red; padding:10px; border-radius:10px;'><span style='color:gray'>KAR ALMA YERİ</span><br><span class='sell-zone'>{r1:.2f} - {r2:.2f}</span></div>", unsafe_allow_html=True)
                st.write("")
                st.plotly_chart(fig, use_container_width=True)
            else: st.error("Hisse bulunamadı!")

    st.markdown("---")

    # --- TARAMA BÖLÜMÜ ---
    st.subheader("🌊 Piyasa Balina Taraması")
    
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
# 4. ÖDEME EKRANI
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
                st.success("Mesaj iletildi! Onay bekleniyor.")
            
    st.markdown("---")
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
# 5. LOGIN / REGISTER
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

# ROUTER
if st.session_state.login_user is None:
    login_page()
else:
    user = st.session_state.login_user
    db = load_db()
    if user in db:
        user_data = db[user]
        st.session_state.db = db
        if user_data.get('rol') == 'admin': ana_uygulama()
        elif user_data.get('onay'): ana_uygulama()
        else: payment_screen()
    else:
        st.session_state.login_user = None
        st.rerun()
