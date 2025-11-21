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

# --- VERİTABANI ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": []}}
        save_db(default_db)
        return default_db
    try: with open(DB_FILE, "r") as f: return json.load(f)
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    
    /* Kartlar */
    .balina-karti { padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #374151; background-color: #111827; }
    .bist-card { border-left: 5px solid #38bdf8; }
    .crypto-card { border-left: 5px solid #facc15; }
    
    /* Sinyal Kutuları */
    .signal-box { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 13px; display: inline-block; margin-right: 5px; }
    .yuksek-alim { background-color: #065f46; color: #34d399; border: 1px solid #34d399; } /* Koyu Yeşil */
    .potansiyel { background-color: #4c1d95; color: #a78bfa; border: 1px solid #a78bfa; } /* Mor */
    .kopush { background-color: #b91c1c; color: #fca5a5; border: 1px solid #fca5a5; animation: pulse 1s infinite; } /* Yanıp Sönen Kırmızı (Dikkat çekmek için) */
    
    /* HDFGS Özel */
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 25px rgba(255, 215, 0, 0.2); }
    
    /* Butonlar */
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; border: 1px solid #555; background-color: #000; color: #FFD700; }
    .stButton button:hover { border-color: #FFD700; background-color: #222; }
    
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# ==========================================
# ADMIN VE GİRİŞ (KISA VERSİYON)
# ==========================================
def login_page():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🥸 PALA GİRİŞ</h1>", unsafe_allow_html=True)
    kullanici = st.text_input("Kullanıcı Adı")
    sifre = st.text_input("Şifre", type="password")
    if st.button("GİRİŞ 🚀"):
        db = load_db()
        if kullanici in db and db[kullanici]['sifre'] == sifre:
            st.session_state.login_user = kullanici
            st.session_state.giris_yapildi = True
            st.rerun()
        else: st.error("Hatalı Giriş!")

def payment_screen():
    st.warning("Hesabınız onay bekliyor. Lütfen Admin ile iletişime geçin.")
    if st.button("Çıkış"): st.session_state.login_user = None; st.rerun()

# ==========================================
# ANA UYGULAMA
# ==========================================
def ana_uygulama():
    col_head = st.columns([8, 2])
    with col_head[0]:
        st.title("📈 YÜKSELİŞ POTANSİYELİ TARAYICISI")
        st.caption("HDFGS (Sabit) • Hacim Patlayanlar • Para Girişi Olanlar")
    with col_head[1]:
        if st.button("ÇIKIŞ"):
            st.session_state.login_user = None
            st.rerun()

    # GRAFİK
    if st.session_state.secilen_hisse:
        st.info(f"📊 {st.session_state.secilen_hisse} Grafiği")
        try:
            df = yf.download(st.session_state.secilen_hisse, period="6mo", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if not df.empty:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
                st.plotly_chart(fig, use_container_width=True)
        except: st.error("Grafik yüklenemedi.")
        if st.button("Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()

    # TARAMA LİSTESİ (BIST 100 + YILDIZ PAZAR)
    bist_listesi = [
        "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
        "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", 
        "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", 
        "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", 
        "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "BRSAN.IS", "CIMSA.IS", "DOHOL.IS", 
        "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS", "ISMEN.IS", "KLSER.IS", "KORDS.IS",
        "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS", "SOKE.IS", "TRGYO.IS", "TSPOR.IS", "ULKER.IS",
        "VESBE.IS", "YYLGD.IS", "ZOREN.IS", "AKFGY.IS", "ALBRK.IS", "BIOEN.IS", "BOBET.IS", "CCOLA.IS",
        "CEMTS.IS", "CWENE.IS", "GENIL.IS", "IZMDC.IS", "KARSN.IS", "KMPUR.IS", "KONYA.IS", "MAGEN.IS",
        "MTRKS.IS", "PENTA.IS", "PSGYO.IS", "SDTTR.IS", "SELEC.IS", "SNGYO.IS", "TATGD.IS", "TURSG.IS",
        "VERUS.IS", "YEOTK.IS"
    ]

    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "AVAX-USD", "SHIB-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

    @st.cache_data(ttl=180, show_spinner=False)
    def potansiyel_tara(liste, tip):
        bulunanlar = []
        hdfgs_data = None # HDFGS'yi ayrıca tutacağız
        
        toplam = len(liste)
        bar = st.progress(0, text=f"{tip} Piyasası Taranıyor (Alıcılı Tahtalar)...")
        
        for i, symbol in enumerate(liste):
            try:
                df = yf.download(symbol, period="3d", interval="1h", progress=False)
                if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                
                if len(df) > 10:
                    son = df.iloc[-1]
                    prev = df.iloc[-2] # Bir önceki saat
                    
                    fiyat = son['Close']
                    acilis = df['Open'].iloc[-1]
                    
                    # DEĞİŞİM (Yüzde)
                    degisim = ((fiyat - acilis) / acilis) * 100
                    
                    # HACİM ANALİZİ
                    hacim_son = son['Volume']
                    hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                    kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                    
                    # MOMENTUM / RSI
                    delta = df['Close'].diff()
                    gain = delta.where(delta>0,0).rolling(14).mean()
                    loss = (-delta.where(delta<0,0)).rolling(14).mean()
                    rs = gain/loss
                    rsi = 100 - (100 / (1+rs)).iloc[-1]
                    
                    # --- KARAR MEKANİZMASI ---
                    etiket = None
                    renk_kod = "gray"
                    aciklama = ""
                    
                    # 1. HDFGS KURALI (Her zaman al)
                    if "HDFGS" in symbol:
                        if degisim > 0 and kat > 1.1:
                            etiket = "HDFGS GÜÇLÜ 💪"
                            renk_kod = "yuksek-alim"
                            aciklama = "Hacim ve Fiyat Artıyor!"
                        elif degisim < 0:
                            etiket = "HDFGS DİNLENİYOR 😴"
                            aciklama = "Takipte kal."
                        else:
                            etiket = "HDFGS NÖTR"
                            aciklama = "Yatay seyir."
                        
                        hdfgs_data = {
                            "Sembol": "HDFGS", "Fiyat": fiyat, "Degisim": degisim,
                            "Hacim": kat, "Etiket": etiket, "Renk": renk_kod, "Aciklama": aciklama,
                            "Kod": symbol
                        }
                        continue # HDFGS'yi listeye değil özel değişkene at

                    # 2. DİĞERLERİ (FİLTRELİ)
                    # Kural: Fiyat ARTI (+) olacak VE Hacim ORTALAMANIN ÜSTÜNDE olacak (>1.2x)
                    if degisim > 0.2 and kat > 1.3:
                        if kat > 2.5:
                            etiket = "🚀 HACİM PATLAMASI"
                            renk_kod = "kopush" # Yanıp sönen
                            aciklama = f"Hacim Ortalamanın {kat:.1f} Katı!"
                        elif rsi < 40:
                            etiket = "💎 DİPTEN DÖNÜŞ"
                            renk_kod = "potansiyel"
                            aciklama = "RSI Dipte + Para Girişi"
                        else:
                            etiket = "🟢 GÜÇLÜ ALIM"
                            renk_kod = "yuksek-alim"
                            aciklama = "İstikrarlı Yükseliş"
                        
                        isim = symbol.replace(".IS", "").replace("-USD", "")
                        bulunanlar.append({
                            "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim,
                            "Hacim": kat, "Etiket": etiket, "Renk": renk_kod, "Aciklama": aciklama,
                            "Kod": symbol, "Skor": kat * degisim # Sıralama için skor
                        })
                
                time.sleep(0.01)
                bar.progress((i + 1) / toplam)
            except: continue
            
        bar.empty()
        
        # SKORA GÖRE SIRALA (En potansiyelli en üste)
        bulunanlar = sorted(bulunanlar, key=lambda x: x['Skor'], reverse=True)
        
        # HDFGS'yi EN BAŞA EKLE
        if hdfgs_data:
            bulunanlar.insert(0, hdfgs_data)
            
        return bulunanlar

    # ARAYÜZ
    tab1, tab2 = st.tabs(["BIST (YÜKSELENLER)", "KRİPTO (YÜKSELENLER)"])
    
    with tab1:
        if st.button("BIST TARAMASI 📡", key="b1"): st.cache_data.clear(); st.rerun()
        sonuclar = potansiyel_tara(bist_listesi, "BIST")
        if sonuclar:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    st.markdown(f"""
                    <div class="balina-karti bist-card {ozel}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h4>
                                <p style="margin:0; font-size:16px; font-weight:bold;">{veri['Fiyat']:.2f} TL <span style="color:#4ade80;">(+%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Etiket']}</div>
                                <p style="margin:3px 0 0 0; font-size:11px; color:#9ca3af;">{veri['Aciklama']}</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK 📈", key=f"b_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
        else: st.info("Şu an alıcılı/hareketli tahta yok.")

    with tab2:
        if st.button("KRİPTO TARAMASI 📡", key="c1"): st.cache_data.clear(); st.rerun()
        sonuclar_kripto = potansiyel_tara(kripto_listesi, "KRIPTO")
        if sonuclar_kripto:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar_kripto):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="balina-karti crypto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4>
                                <p style="margin:0; font-size:16px; font-weight:bold;">${veri['Fiyat']:.4f} <span style="color:#4ade80;">(+%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Etiket']}</div>
                                <p style="margin:3px 0 0 0; font-size:11px; color:#9ca3af;">{veri['Aciklama']}</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"GRAFİK 📈", key=f"c_{veri['Sembol']}"): st.session_state.secilen_hisse = veri['Kod']; st.rerun()
        else: st.info("Hareketli coin yok.")

# --- ROUTER ---
if st.session_state.login_user:
    user_data = st.session_state.db.get(st.session_state.login_user)
    if user_data and (user_data.get('onay') or user_data.get('rol') == 'admin'): ana_uygulama()
    else: payment_screen()
else: login_page()
