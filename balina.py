import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala Admin Panel", layout="wide", page_icon="🥸")

# --- KULLANICI VERİTABANI (BAŞLANGIÇ) ---
# Burası veritabanı gibi çalışır.
if 'users' not in st.session_state:
    st.session_state.users = {
        "pala": {"sifre": "pala500", "rol": "admin", "isim": "Büyük Patron"},
        "admin": {"sifre": "admin", "rol": "admin", "isim": "Yedek Admin"},
        "misafir": {"sifre": "1234", "rol": "user", "isim": "Misafir Üye"}
    }

if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False
if 'aktif_kullanici' not in st.session_state:
    st.session_state.aktif_kullanici = None
if 'user_rol' not in st.session_state:
    st.session_state.user_rol = None
if 'secilen_hisse' not in st.session_state:
    st.session_state.secilen_hisse = None

# ==========================================
# 1. GİRİŞ EKRANI
# ==========================================
def login_ekrani():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: white; }
        .pala-title { font-size: 55px; font-weight: 900; text-align: center; background: -webkit-linear-gradient(#fff, #aaa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 15px #FFD700; margin-bottom: 10px; }
        .biyik-logo { font-size: 80px; text-align: center; display: block; margin-bottom: -20px; animation: float 3s ease-in-out infinite; }
        @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
        .vip-card { background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%); border: 3px solid #FFD700; border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 0 40px rgba(255, 215, 0, 0.3); max-width: 600px; margin: 0 auto; }
        .price-tag { font-size: 60px; color: #4ade80; font-weight: bold; margin: 15px 0; font-family: 'Courier New', monospace; }
        .odeme-yontemi { background-color: #222; padding: 15px; border-radius: 10px; margin-bottom: 10px; text-align: left; border-left: 5px solid #FFD700; font-size: 14px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="biyik-logo">🥸</div>', unsafe_allow_html=True)
    st.markdown('<div class="pala-title">PALA İLE İYİ TAHTALAR</div>', unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>⚜️ VIP GİRİŞ BİLETİ</h2><p>Admin Paneli, Üye Yönetimi ve Balina Takibi.</p><div class='price-tag'>$500</div><p style='color:#FFD700; font-weight:bold;'>LIFETIME ACCESS</p></div>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme")
        st.markdown("<div class='odeme-yontemi'><strong>₿ KRİPTO (USDT)</strong><br><code style='color:#FFD700'>TXaBCdef1234567890...</code></div>", unsafe_allow_html=True)
    with col2:
        st.subheader("🔐 Üye Girişi")
        with st.form("giris_formu"):
            kullanici = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            giris_btn = st.form_submit_button("GİRİŞ 🚀")
            
            if giris_btn:
                users = st.session_state.users
                if kullanici in users and users[kullanici]['sifre'] == sifre:
                    st.session_state.giris_yapildi = True
                    st.session_state.aktif_kullanici = kullanici
                    st.session_state.user_rol = users[kullanici]['rol']
                    st.success(f"Hoşgeldin {users[kullanici]['isim']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Hatalı Kullanıcı Adı veya Şifre!")

# ==========================================
# 2. YÖNETİM PANELİ (SADECE ADMINLER İÇİN)
# ==========================================
def admin_paneli():
    st.sidebar.markdown("---")
    st.sidebar.header("🛠️ YÖNETİCİ PANELİ")
    
    menu = st.sidebar.selectbox("İşlem Seçiniz:", ["Üye Listesi", "Üye Ekle", "Üye Sil"])
    
    if menu == "Üye Listesi":
        st.sidebar.write("📂 **Kayıtlı Kullanıcılar**")
        df_users = pd.DataFrame.from_dict(st.session_state.users, orient='index')
        st.sidebar.table(df_users[['isim', 'rol', 'sifre']]) # Şifreyi görmek istemezsen listeden çıkar
        
    elif menu == "Üye Ekle":
        st.sidebar.write("➕ **Yeni Üye Kaydı**")
        yeni_kul = st.sidebar.text_input("Kullanıcı Adı (Nick)")
        yeni_sifre = st.sidebar.text_input("Şifre")
        yeni_isim = st.sidebar.text_input("Görünen İsim")
        yeni_rol = st.sidebar.selectbox("Yetki", ["user", "admin"])
        
        if st.sidebar.button("Üyeyi Kaydet"):
            if yeni_kul and yeni_sifre:
                if yeni_kul in st.session_state.users:
                    st.sidebar.error("Bu kullanıcı adı zaten var!")
                else:
                    st.session_state.users[yeni_kul] = {"sifre": yeni_sifre, "rol": yeni_rol, "isim": yeni_isim}
                    st.sidebar.success(f"{yeni_isim} eklendi!")
            else:
                st.sidebar.error("Bilgileri eksiksiz girin.")

    elif menu == "Üye Sil":
        st.sidebar.write("🗑️ **Üye Silme**")
        silinecek = st.sidebar.selectbox("Kimi silelim?", list(st.session_state.users.keys()))
        
        if st.sidebar.button("Kullanıcıyı Sil"):
            if silinecek == "pala": # Kendini silmesin
                st.sidebar.error("Patronu silemezsin!")
            elif silinecek == st.session_state.aktif_kullanici:
                st.sidebar.error("Kendini silemezsin!")
            else:
                del st.session_state.users[silinecek]
                st.sidebar.success(f"{silinecek} silindi!")
                st.rerun()

# ==========================================
# 3. ANA UYGULAMA (GRAFİK VE TARAMA)
# ==========================================
def ana_uygulama():
    # CSS ve Tasarım
    st.markdown("""
        <style>
        .stApp { background-color: #0a0e17; color: white; }
        .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
        .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; position: relative; }
        .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
        .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
        .signal-box { padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; display: inline-block; }
        .buy { background-color: #059669; color: white; box-shadow: 0 0 10px #059669; }
        .sell { background-color: #dc2626; color: white; box-shadow: 0 0 10px #dc2626; }
        .breakout { background-color: #7c3aed; color: white; animation: flash 1s infinite; }
        .seviye-kutu { display: flex; justify-content: space-between; font-size: 11px; margin-top: 5px; background: rgba(0,0,0,0.4); padding: 5px; border-radius: 5px; }
        .stButton button { width: 100%; border-radius: 8px; margin-top: 5px; font-weight: bold; border: 1px solid #555; }
        .stButton button:hover { border-color: #FFD700; color: #FFD700; }
        .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
        @keyframes flash { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
        <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
    """, unsafe_allow_html=True)

    # Üst Menü (Çıkış ve Bilgi)
    col_head = st.columns([8, 2])
    with col_head[0]:
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {st.session_state.users[st.session_state.aktif_kullanici]['isim']} | Yetki: {st.session_state.user_rol}")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.giris_yapildi = False
            st.session_state.aktif_kullanici = None
            st.rerun()

    # --- ADMIN PANELİ KONTROLÜ ---
    if st.session_state.user_rol == 'admin':
        admin_paneli()

    # --- GRAFİK FONKSİYONU ---
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

    # --- LİSTELER ---
    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

    # --- TARAMA MOTORU ---
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

    # --- ARAYÜZ SEKMELERİ ---
    tab1, tab2 = st.tabs(["🏙️ BIST (TOP 20)", "₿ KRİPTO (TOP 20)"])
    
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
        else: st.info("Kripto tarafı sakin.")

if st.session_state.giris_yapildi:
    ana_uygulama()
else:
    login_ekrani()
