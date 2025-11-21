import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala Balina Savar", layout="wide", page_icon="🥸")

# --- VERİTABANI ---
DB_FILE = "users_db.json"

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)

def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "portfoy": []}}
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
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    div.stButton > button { background-color: #000000 !important; color: #FFD700 !important; border: 2px solid #FFD700 !important; border-radius: 12px !important; font-weight: bold !important; height: 50px !important; width: 100% !important; }
    div.stButton > button:hover { background-color: #FFD700 !important; color: #000000 !important; transform: scale(1.02) !important; }
    
    .stTextInput input, .stNumberInput input { background-color: #111 !important; color: #FFD700 !important; border: 1px solid #555 !important; }
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } .sell { background-color: #450a0a; color: #f87171; } 
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# ==========================================
# GRAFİK MOTORU (YENİ: HABERLER VE TREND)
# ==========================================
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            prev = df.iloc[-2]
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']; s1 = (2 * pivot) - prev['High']
            
            # Grafik
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"DİRENÇ: {r1:.2f}")
            fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"DESTEK: {s1:.2f}")
            
            # Basit Trend Çizgisi (Son 20 gün ortalaması)
            df['SMA20'] = df['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=2), name="Pala Ortalaması"))

            fig.update_layout(title=f"{symbol} Analiz", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            
            # Haberleri Çek
            haberler = []
            try:
                ticker = yf.Ticker(symbol)
                news = ticker.news
                for n in news[:3]: # Son 3 haber
                    haberler.append(f"📰 [{n['title']}]({n['link']})")
            except: pass
            
            return fig, haberler
    except: return None, None

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
        if st.button("ÇIKIŞ YAP"): st.session_state.login_user = None; st.rerun()

    if db[user].get('rol') == 'admin':
        st.sidebar.title("👑 ADMİN PANELİ")
        if st.sidebar.checkbox("Üye Listesi"): st.sidebar.write(db)

    menu = st.radio("MENÜ:", ["📊 PİYASA RADARI", "💼 PALA'NIN KASASI (CÜZDAN)"], horizontal=True)
    st.divider()

    # --- CÜZDAN MODÜLÜ (YENİ: PASTA GRAFİĞİ) ---
    if menu == "💼 PALA'NIN KASASI (CÜZDAN)":
        st.subheader("💰 Varlık Yönetimi")
        
        # Ekleme Paneli
        with st.expander("➕ Hisse Ekle / Güncelle"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.text_input("Sembol", "HDFGS.IS").upper()
            y_mal = c2.number_input("Maliyet", value=2.63)
            y_adt = c3.number_input("Adet", value=194028)
            if c4.button("KAYDET"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                # Varsa sil yenisini ekle (güncelleme mantığı)
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != y_sem]
                db[user]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("Kaydedildi!"); st.rerun()

        if "portfoy" in db[user] and db[user]["portfoy"]:
            toplam_deger = 0; toplam_kar = 0; data_pie = []
            
            # Tablo verisi hazırla
            table_data = []
            for p in db[user]["portfoy"]:
                try:
                    fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                    tutar = fiyat * p['adet']
                    kar = (fiyat - p['maliyet']) * p['adet']
                    toplam_deger += tutar
                    toplam_kar += kar
                    table_data.append({"Hisse": p['sembol'], "Adet": p['adet'], "Maliyet": p['maliyet'], "Fiyat": f"{fiyat:.2f}", "Değer": f"{tutar:,.0f}", "Kar": f"{kar:,.0f}"})
                    data_pie.append({"Sembol": p['sembol'], "Deger": tutar})
                except: pass
            
            # Kartlar
            k1, k2, k3 = st.columns(3)
            k1.metric("TOPLAM SERVET", f"{toplam_deger:,.0f} TL")
            k2.metric("NET KAR", f"{toplam_kar:,.0f} TL", delta_color="normal")
            
            # Pasta Grafiği
            c_pie, c_tab = st.columns([1, 2])
            with c_pie:
                if data_pie:
                    fig_pie = px.pie(pd.DataFrame(data_pie), values='Deger', names='Sembol', title='Varlık Dağılımı', hole=0.4)
                    fig_pie.update_traces(textinfo='percent+label')
                    fig_pie.update_layout(template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            with c_tab:
                st.table(pd.DataFrame(table_data))
                
            # Silme
            sil = st.selectbox("Sil:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("HİSSEYİ SİL"):
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sil]
                save_db(db); st.rerun()
        else: st.info("Cüzdan boş.")

    # --- RADAR MODÜLÜ ---
    elif menu == "📊 PİYASA RADARI":
        col_s1, col_s2 = st.columns([3, 1])
        arama = col_s1.text_input("Hisse Kodu:", "HDFGS").upper()
        if col_s2.button("ANALİZ ET 🚀"):
            sym = f"{arama}.IS" if "." not in arama and "-" not in arama else arama
            st.session_state.secilen_hisse = sym; st.rerun()

        if st.session_state.secilen_hisse:
            st.info(f"📈 {st.session_state.secilen_hisse} Raporu")
            fig, haberler = grafik_ciz(st.session_state.secilen_hisse)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                if haberler:
                    st.write("#### 📰 Son Haberler")
                    for h in haberler: st.markdown(h)
            else: st.error("Veri yok.")
            if st.button("Kapat"): st.session_state.secilen_hisse = None; st.rerun()
            st.divider()

        # TARAMA LİSTELERİ
        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
        kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "WIF-USD", "BONK-USD"]

        @st.cache_data(ttl=180, show_spinner=False)
        def verileri_getir(liste, tip):
            bulunanlar = []; bar = st.progress(0, text=f"{tip} Taranıyor...")
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
                            durum = "HDFGS HAREKETLİ 🦅" if kat > 1.2 else "HDFGS SAKİN"; renk = "buy" if degisim>0 else "sell"; aciklama = "Takipte..."
                        elif kat > 2.5:
                            durum = "BALİNA 🚀" if degisim > 0 else "SATIŞ 🔻"; renk = "buy" if degisim > 0 else "sell"; aciklama = f"Hacim {kat:.1f}x"
                        
                        if durum:
                            isim = symbol.replace(".IS", "").replace("-USD", "")
                            bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "HacimKat": kat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Kod": symbol})
                    bar.progress((i+1)/len(liste)); time.sleep(0.01)
                except: continue
            bar.empty()
            return bulunanlar

        t1, t2 = st.tabs(["BIST", "KRİPTO"])
        with t1:
            if st.button("BIST TARA 📡"): st.cache_data.clear(); st.rerun()
            res = verileri_getir(bist_listesi, "BIST")
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        ozel = "hdfgs-ozel" if "HDFGS" in v['Sembol'] else ""
                        st.markdown(f"""<div class="balina-karti bist-card {ozel}"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#e0f2fe;">{v['Sembol']}</h4><p style="margin:0; font-size:14px;">{v['Fiyat']:.2f} TL</p></div><div style="text-align:right;"><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{v['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"b_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
            else: st.info("Sakin.")
        
        with t2:
            if st.button("KRİPTO TARA 📡"): st.cache_data.clear(); st.rerun()
            res = verileri_getir(kripto_listesi, "KRIPTO")
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{v['Sembol']}</h4><p style="margin:0; font-size:14px;">${v['Fiyat']:.4f}</p></div><div style="text-align:right;"><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{v['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"c_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
            else: st.info("Sakin.")

# --- LOGIN EKRANI (STANDART) ---
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    t1, t2 = st.tabs(["GİRİŞ", "KAYIT"])
    with t1:
        k = st.text_input("Kullanıcı"); s = st.text_input("Şifre", type="password")
        if st.checkbox("Reset"): 
            if st.button("Sistem Onar"): 
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("Admin: admin/pala500")
        if st.button("GİRİŞ"):
            db = load_db()
            if k in db and db[k]['sifre'] == s: st.session_state.login_user = k; st.session_state.giris_yapildi = True; st.rerun()
            else: st.error("Hatalı")
    with t2:
        yk = st.text_input("Yeni Nick"); ya = st.text_input("Ad"); ys = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT"):
            db = load_db()
            if yk not in db: db[yk] = {"sifre": ys, "isim": ya, "onay": False, "rol": "user", "mesajlar": [], "portfoy": []}; save_db(db); st.success("Kaydolundu")
            else: st.error("Alınmış")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 ONAY BEKLENİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK: $500</h2></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='odeme-kutu'><strong>USDT</strong><br>TXa...</div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("Dekont"); 
        if st.button("GÖNDER"):
            u = st.session_state.login_user; db = load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"] = []
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("İletildi")
    if st.button("Çıkış"): st.session_state.login_user = None; st.rerun()

if st.session_state.login_user is None: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol') == 'admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
