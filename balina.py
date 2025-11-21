import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala ile İyi Tahtalar", layout="wide", page_icon="🥸")

# --- GİRİŞ KONTROLÜ ---
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

# ==========================================
# 1. BÖLÜM: GİRİŞ VE ÖDEME EKRANI ($500)
# ==========================================
def login_ekrani():
    st.markdown("""
        <style>
        .stApp { background-color: #000000; color: white; }
        
        /* PALA BAŞLIK ANİMASYONU */
        .pala-title {
            font-size: 55px;
            font-weight: 900;
            text-align: center;
            background: -webkit-linear-gradient(#fff, #aaa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px #FFD700;
            margin-bottom: 10px;
        }
        
        .biyik-logo {
            font-size: 80px;
            text-align: center;
            display: block;
            margin-bottom: -20px;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }

        .vip-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%);
            border: 3px solid #FFD700;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 0 40px rgba(255, 215, 0, 0.3);
            max-width: 600px;
            margin: 0 auto;
        }
        
        .price-tag {
            font-size: 60px;
            color: #4ade80; /* Yeşil */
            font-weight: bold;
            margin: 15px 0;
            font-family: 'Courier New', monospace;
        }
        
        .odeme-yontemi {
            background-color: #222;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: left;
            border-left: 5px solid #FFD700;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Logo ve Başlık
    st.markdown('<div class="biyik-logo">🥸</div>', unsafe_allow_html=True)
    st.markdown('<div class="pala-title">PALA İLE İYİ TAHTALAR</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#888;'>Sadece Seçkin Yatırımcılar İçin.</h3>", unsafe_allow_html=True)
    
    st.write("")

    # VIP KART (500 DOLAR)
    st.markdown("""
    <div class="vip-card">
        <h2 style="color: white;">⚜️ VIP GİRİŞ BİLETİ</h2>
        <p style="color: #ccc;">Balina hareketleri, HDFGS özel takibi ve anlık sinyaller.</p>
        <div class="price-tag">$500</div>
        <p style="color:#FFD700; font-weight:bold; letter-spacing: 2px;">LIFETIME ACCESS</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Ödeme Yöntemleri")
        st.markdown("""
        <div class="odeme-yontemi">
            <strong>₿ KRİPTO (USDT - TRC20)</strong><br>
            <code style="color:#FFD700">TXaBCdef1234567890...</code>
        </div>
        <div class="odeme-yontemi">
            <strong>🏦 BANKA HAVALE / EFT</strong><br>
            <code style="color:#FFD700">TR12 0000 ... (IBAN)</code><br>
            Alıcı: Pala Yazılım A.Ş.
        </div>
        """, unsafe_allow_html=True)
        st.warning("Dekontu iletiniz. Giriş şifresi tarafınıza gönderilecektir.")

    with col2:
        st.subheader("🔐 Giriş Yap")
        with st.form("giris_formu"):
            kullanici = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Özel Şifreniz", type="password")
            giris_btn = st.form_submit_button("SİSTEME GİRİŞ 🚀")
            
            if giris_btn:
                # ŞİFRELER (Burayı kendine göre değiştirebilirsin)
                if kullanici == "admin" and sifre == "pala500": 
                    st.session_state.giris_yapildi = True
                    st.success("Hoşgeldin Patron! Piyasa Açılıyor...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Hatalı Şifre! Ödeme onayı alınamadı.")

# ==========================================
# 2. BÖLÜM: ANA UYGULAMA (İÇERİSİ)
# ==========================================
def ana_uygulama():
    # --- CSS TASARIMI (PALA BIYIK STİLİ) ---
    st.markdown("""
        <style>
        .stApp { background-color: #0a0e17; color: white; }
        
        /* KÖŞEDEKİ PALA AMBLEMİ */
        .pala-sticker {
            position: fixed; top: 10px; right: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: black;
            padding: 8px 15px; border-radius: 20px;
            border: 3px solid #000; text-align: center; font-weight: bold;
            z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            transform: rotate(5deg);
        }
        .pala-emoji { font-size: 32px; display: block; }
        .pala-text { font-size: 12px; font-family: 'Arial Black'; }

        /* Kartlar */
        .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #374151; }
        .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 4px solid #38bdf8; }
        .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 4px solid #facc15; }
        
        .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
        .buy { background-color: #059669; color: white; }
        .sell { background-color: #dc2626; color: white; }
        
        .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 20px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
        </style>
        
        <div class="pala-sticker">
            <span class="pala-emoji">🥸</span>
            <span class="pala-text">İYİ TAHTALAR</span>
        </div>
    """, unsafe_allow_html=True)

    # Çıkış
    col_head = st.columns([8, 1])
    if col_head[1].button("ÇIKIŞ YAP"):
        st.session_state.giris_yapildi = False
        st.rerun()

    st.title("🥸 PALA İLE İYİ TAHTALAR")
    st.caption("HDFGS • BIST 100 • KRİPTO | Vip Panel")

    # --- LİSTELER ---
    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

    # --- TARAMA MOTORU ---
    @st.cache_data(ttl=180, show_spinner=False)
    def verileri_getir(liste, piyasa_tipi):
        sinyaller = []
        toplam = len(liste)
        bar = st.progress(0, text=f"{piyasa_tipi} Taranıyor...")
        for i, symbol in enumerate(liste):
            try:
                df = yf.download(symbol, period="5d", interval="1h", progress=False)
                if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                if len(df) > 10:
                    son = df.iloc[-1]
                    hacim_son = son['Volume']
                    hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                    kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                    fiyat = son['Close']
                    degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                    delta = df['Close'].diff(); gain = delta.where(delta>0,0).rolling(14).mean(); loss = (-delta.where(delta<0,0)).rolling(14).mean(); rs=gain/loss; rsi=100-(100/(1+rs)).iloc[-1]
                    
                    durum = None; renk = "gray"; aciklama = ""
                    if "HDFGS" in symbol:
                        if kat > 1.2: durum = "HDFGS HAREKETLİ 🦅"; renk = "buy" if degisim>0 else "sell"; aciklama = "Anlık Hacim"
                        else: durum = "HDFGS SAKİN"; aciklama = "Takipte..."
                    elif kat > 2.5:
                        if degisim > 0.5: durum = "İYİ TAHTA (ALIM) 🚀"; renk = "buy"; aciklama = f"Hacim {kat:.1f}x Arttı"
                        elif degisim < -0.5: durum = "SATIŞ BASKISI 🔻"; renk = "sell"; aciklama = "Yüklü Çıkış"
                    elif rsi < 35 and kat > 1.2: durum = "SİNSİ TOPLAMA 🕵️"; renk = "buy"; aciklama = "Dipte Hacim Var"

                    if durum:
                        isim = symbol.replace(".IS", "").replace("-USD", "")
                        sinyaller.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama})
                bar.progress((i + 1) / toplam); time.sleep(0.01)
            except: continue
        bar.empty()
        return sinyaller

    # --- ARAYÜZ ---
    tab1, tab2 = st.tabs(["🏙️ BIST TAHTALARI", "₿ KRİPTO"])
    
    with tab1:
        if st.button("TAHTALARI TARA 📡", key="bist_btn"): st.cache_data.clear(); st.rerun()
        sonuclar = verileri_getir(bist_listesi, "BIST")
        if sonuclar:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    st.markdown(f"""<div class="balina-karti bist-card {ozel}"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
        else: st.info("Pala şu an çay içiyor, tahtalar sakin.")

    with tab2:
        if st.button("COINLERİ TARA 📡", key="kripto_btn"): st.cache_data.clear(); st.rerun()
        sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
        if sonuclar_kripto:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar_kripto):
                with cols[i % 2]:
                    st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4><p style="margin:0; font-size:14px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p></div><div style="text-align:right;"><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{veri['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
        else: st.info("Kripto tarafı sakin.")

# ==========================================
# ANA KONTROL
# ==========================================
if st.session_state.giris_yapildi:
    ana_uygulama()
else:
    login_ekrani()
