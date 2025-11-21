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

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    .vip-card { background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%); border: 3px solid #FFD700; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 30px rgba(255, 215, 0, 0.2); }
    .odeme-kutu { background-color: #222; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 10px; }
    .onay-bekliyor { background-color: #7c2d12; color: #fdba74; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; border: 1px solid #fdba74; margin-top: 20px; }
    
    /* Balina Kartları */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; position: relative; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #059669; color: white; } .sell { background-color: #dc2626; color: white; } .breakout { background-color: #7c3aed; color: white; animation: flash 1s infinite; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
    
    .stButton button { width: 100%; border-radius: 8px; margin-top: 5px; font-weight: bold; border: 1px solid #555; }
    .stButton button:hover { border-color: #FFD700; color: #FFD700; }
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
    
    # Veritabanını taze çek
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
            
            st.write("---")
            col1, col2 = st.columns(2)
            
            # Onaylama
            with col1:
                onaysizlar = [u['Kullanıcı'] for u in uye_listesi if u['Durum'] == "❌ Bekliyor"]
                if onaysizlar:
                    user_to_approve = st.selectbox("Onaylanacak Kişi:", onaysizlar)
                    if st.button("YETKİ VER (ONAYLA) ✅"):
                        db[user_to_approve]['onay'] = True
                        save_db(db)
                        st.success(f"{user_to_approve} artık sisteme girebilir!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Onay bekleyen kimse yok.")

            # Silme
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
    
    st.markdown("""
    <div class='vip-card'>
        <h2>ÜYELİK ÜCRETİ: $500</h2>
        <p>Pala Balina Savar analizlerine erişmek için ödemenizin onaylanması gerekmektedir.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme Bilgileri")
        st.markdown("""
        <div class='odeme-kutu'>
            <strong>₿ KRİPTO (USDT - TRC20)</strong><br>
            <code>TXaBCdef1234567890...</code>
        </div>
        <div class='odeme-kutu'>
            <strong>🏦 BANKA (HAVALE/EFT)</strong><br>
            <code>TR12 0000 ... (IBAN)</code><br>
            <strong>Alıcı:</strong> Pala Yazılım A.Ş.
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.subheader("💬 Ödeme Bildirimi")
        user_msg = st.text_area("Dekont No veya Mesajınız:", placeholder="Örn: Ahmet Yılmaz, saat 14:30'da gönderdim.")
        
        if st.button("ADMİN'E GÖNDER 📨"):
            # Veritabanını güncelle
            db = load_db()
            kullanici = st.session_state.login_user
            
            if kullanici in db:
                if "mesajlar" not in db[kullanici]: db[kullanici]["mesajlar"] = []
                
                zaman = datetime.now().strftime("%d/%m %H:%M")
                db[kullanici]["mesajlar"].append(f"[{zaman}] {user_msg}")
                save_db(db)
                st.success("Mesajınız iletildi! Admin kontrol edince erişiminiz açılacaktır.")
    
    st.markdown("---")
    
    # ONAY KONTROL BUTONU (YENİ ÖZELLİK)
    st.markdown("<div class='onay-bekliyor'>⏳ Hesabınız şu an incelemede. Ödeme yaptıysanız Admin onayı bekleniyor.</div>", unsafe_allow_html=True)
    
    col_check, col_out = st.columns([3, 1])
    if col_check.button("🔄 ONAY DURUMUMU KONTROL ET"):
        # Veritabanını tekrar oku ve kontrol et
        updated_db = load_db()
        user = st.session_state.login_user
        if updated_db[user]['onay'] == True:
            st.session_state.db = updated_db # Session'ı güncelle
            st.success("✅ ONAYLANDINIZ! Yönlendiriliyorsunuz...")
            time.sleep(1)
            st.rerun()
        else:
            st.warning("Henüz onaylanmamış. Lütfen bekleyiniz.")
            
    if col_out.button("Çıkış Yap"):
        st.session_state.login_user = None
        st.rerun()

# ==========================================
# 3. ANA UYGULAMA (PRO ANALİZ)
# ==========================================
def ana_uygulama():
    # Üst Başlık
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = st.session_state.db[st.session_state.login_user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Erişim Aktif ✅")
    with col_head[1]:
        if st.button("GÜVENLİ ÇIKIŞ"):
            st.session_state.login_user = None
            st.rerun()

    # Adminse Paneli Göster
    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    # GRAFİK MOTORU
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

    # TARAMA VE LİSTELEME (BALİNA MODÜLÜ)
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
        if st.
