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
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "portfoy": []}}
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
    
    /* Butonlar */
    div.stButton > button {
        background-color: #000000 !important; color: #FFD700 !important; border: 2px solid #FFD700 !important;
        border-radius: 12px !important; font-weight: bold !important; height: 50px !important; width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { background-color: #FFD700 !important; color: #000000 !important; transform: scale(1.02) !important; }
    
    /* Inputlar */
    .stTextInput input, .stNumberInput input { background-color: #111 !important; color: #FFD700 !important; border: 1px solid #555 !important; }
    
    /* Pala Sticker */
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    
    /* Kartlar */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } .sell { background-color: #450a0a; color: #f87171; } 
    .golden { background-color: #FFD700; color: black; box-shadow: 0 0 15px #FFD700; animation: pulse 1s infinite; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# ==========================================
# GRAFİK & ANALİZ MOTORU
# ==========================================
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            # Pivot ve Ortalamalar
            last = df.iloc[-1]; prev = df.iloc[-2]
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']; s1 = (2 * pivot) - prev['High']
            
            # Golden Cross için
            df['SMA50'] = df['Close'].rolling(50).mean()
            df['SMA200'] = df['Close'].rolling(200).mean()
            
            fig = go.Figure()
            # Mumlar
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            # Ortalamalar
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='orange', width=1), name="SMA 50"))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='blue', width=1), name="SMA 200"))
            # Destek/Direnç
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"DİRENÇ: {r1:.2f}")
            fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"DESTEK: {s1:.2f}")
            
            fig.update_layout(title=f"{symbol} Detaylı Analiz", template="plotly_dark", height=500, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            return fig, df
    except: return None, None

# ==========================================
# ANA UYGULAMA
# ==========================================
def ana_uygulama():
    user = st.session_state.login_user
    db = st.session_state.db
    
    # Üst Başlık & Çıkış
    c1, c2 = st.columns([8, 2])
    c1.title("🥸 PALA İLE İYİ TAHTALAR")
    if c2.button("GÜVENLİ ÇIKIŞ"):
        st.session_state.login_user = None; st.rerun()

    # Menü Seçimi
    menu = st.radio("MENÜ:", ["📊 PİYASA RADARI", "💼 PALA'NIN KASASI (CÜZDAN)", "🌡️ PİYASA ATEŞİ"], horizontal=True)
    st.divider()

    # -------------------------------------------
    # 1. MODÜL: CÜZDAN (PORTFÖY)
    # -------------------------------------------
    if menu == "💼 PALA'NIN KASASI (CÜZDAN)":
        st.subheader("💰 Varlık Yönetimi")
        
        # Yeni Hisse Ekleme
        with st.expander("➕ Portföye Hisse Ekle"):
            c_add1, c_add2, c_add3, c_add4 = st.columns(4)
            yeni_sembol = c_add1.text_input("Sembol", "HDFGS.IS").upper()
            yeni_maliyet = c_add2.number_input("Maliyet", value=2.63, format="%.2f")
            yeni_adet = c_add3.number_input("Adet (Lot)", value=194028)
            if c_add4.button("EKLE / GÜNCELLE"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                # Varsa güncelle, yoksa ekle
                mevcut = next((item for item in db[user]["portfoy"] if item["sembol"] == yeni_sembol), None)
                if mevcut:
                    mevcut["maliyet"] = yeni_maliyet
                    mevcut["adet"] = yeni_adet
                else:
                    db[user]["portfoy"].append({"sembol": yeni_sembol, "maliyet": yeni_maliyet, "adet": yeni_adet})
                save_db(db)
                st.success("Portföy Güncellendi!")
                st.rerun()

        # Portföyü Göster ve Hesapla
        if "portfoy" in db[user] and db[user]["portfoy"]:
            toplam_deger = 0
            toplam_kar = 0
            
            df_list = []
            for p in db[user]["portfoy"]:
                try:
                    ticker = yf.Ticker(p['sembol'])
                    fiyat = ticker.fast_info['last_price']
                    tutar = fiyat * p['adet']
                    kar_tl = (fiyat - p['maliyet']) * p['adet']
                    kar_yuzde = ((fiyat - p['maliyet']) / p['maliyet']) * 100
                    
                    toplam_deger += tutar
                    toplam_kar += kar_tl
                    
                    df_list.append({
                        "Hisse": p['sembol'],
                        "Maliyet": p['maliyet'],
                        "Fiyat": f"{fiyat:.2f}",
                        "Adet": p['adet'],
                        "Tutar": f"{tutar:,.0f} TL",
                        "Kar/Zarar": f"{kar_tl:,.0f} TL",
                        "Durum": f"%{kar_yuzde:.1f}"
                    })
                except: pass
            
            # Özet Kartlar
            k1, k2, k3 = st.columns(3)
            k1.metric("TOPLAM SERVET", f"{toplam_deger:,.0f} TL")
            k2.metric("TOPLAM NET KAR", f"{toplam_kar:,.0f} TL", delta_color="normal")
            if toplam_deger > 0:
                k3.metric("GENEL PERFORMANS", f"%{(toplam_kar/(toplam_deger-toplam_kar))*100:.1f}")
            
            st.table(pd.DataFrame(df_list))
            
            # Silme İşlemi
            sil_sec = st.selectbox("Silinecek Hisse:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("HİSSEYİ SİL"):
                db[user]["portfoy"] = [i for i in db[user]["portfoy"] if i['sembol'] != sil_sec]
                save_db(db)
                st.rerun()
        else:
            st.info("Henüz portföyüne hisse eklemedin Patron.")

    # -------------------------------------------
    # 2. MODÜL: PİYASA ATEŞİ (FEAR & GREED)
    # -------------------------------------------
    elif menu == "🌡️ PİYASA ATEŞİ":
        st.subheader("Piyasa Genel Durumu")
        
        # BIST 30 Hızlı Tarama ile Genel RSI Ortalaması
        if st.button("ATEŞİ ÖLÇ 🌡️"):
            with st.spinner("Piyasa nabzı ölçülüyor..."):
                bist30 = ["THYAO.IS", "GARAN.IS", "AKBNK.IS", "EREGL.IS", "SISE.IS", "KCHOL.IS", "TUPRS.IS", "ASELS.IS", "BIMAS.IS", "EKGYO.IS"]
                rsi_list = []
                for s in bist30:
                    try:
                        d = yf.download(s, period="1mo", interval="1d", progress=False)
                        if hasattr(d.columns, 'levels'): d.columns = d.columns.get_level_values(0)
                        delta = d['Close'].diff()
                        gain = delta.where(delta>0,0).rolling(14).mean(); loss = (-delta.where(delta<0,0)).rolling(14).mean()
                        rs = gain/loss; rsi = 100 - (100 / (1+rs)).iloc[-1]
                        rsi_list.append(rsi)
                    except: pass
                
                if rsi_list:
                    avg_rsi = sum(rsi_list) / len(rsi_list)
                    
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = avg_rsi,
                        title = {'text': "BIST KORKU & AÇGÖZLÜLÜK ENDEKSİ"},
                        gauge = {
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "black"},
                            'steps': [
                                {'range': [0, 30], 'color': "green"}, # Korku (Alım Fırsatı)
                                {'range': [30, 70], 'color': "gray"},
                                {'range': [70, 100], 'color': "red"}], # Açgözlülük (Satış Riski)
                            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': avg_rsi}}))
                    st.plotly_chart(fig)
                    
                    if avg_rsi < 30: st.success("Piyasa Korkuyor! (DİP BÖLGESİ - ALIM FIRSATI OLABİLİR)")
                    elif avg_rsi > 70: st.error("Piyasa Çok Açgözlü! (TEPE BÖLGESİ - DÜZELTME GELEBİLİR)")
                    else: st.info("Piyasa Dengeli.")

    # -------------------------------------------
    # 3. MODÜL: PİYASA RADARI (BALİNA + GOLDEN CROSS)
    # -------------------------------------------
    elif menu == "📊 PİYASA RADARI":
        
        # Merkezi Arama
        col_s1, col_s2 = st.columns([3,1])
        arama = col_s1.text_input("Hisse Ara:", placeholder="HDFGS, BTC...").upper()
        if col_s2.button("GRAFİK & HABER"):
            st.session_state.secilen_hisse = f"{arama}.IS" if "." not in arama and "-" not in arama else arama
            st.rerun()
            
        # Grafik ve Haber Gösterimi
        if st.session_state.secilen_hisse:
            st.info(f"📈 {st.session_state.secilen_hisse} Analizi")
            fig, df_news = grafik_ciz(st.session_state.secilen_hisse)
            if fig: 
                st.plotly_chart(fig, use_container_width=True)
                
                # HABERLER
                st.subheader("📰 Son Dakika Haberleri")
                try:
                    news = yf.Ticker(st.session_state.secilen_hisse).news
                    if news:
                        for n in news[:3]:
                            st.write(f"🔹 [{n['title']}]({n['link']})")
                    else: st.write("Güncel haber bulunamadı.")
                except: st.write("Haber servisine ulaşılamadı.")
            
            if st.button("Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()
            st.divider()

        # Taramalar
        tab_bist, tab_crypto = st.tabs(["BIST BALİNALARI", "KRİPTO BALİNALARI"])
        
        # LİSTELER
        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
        
        with tab_bist:
            c_btn1, c_btn2 = st.columns(2)
            tara_normal = c_btn1.button("📡 HACİM TARAMASI (HIZLI)")
            tara_golden = c_btn2.button("⚔️ GOLDEN CROSS TARAMASI (YAVAŞ)")
            
            if tara_normal:
                sonuclar = verileri_getir(bist_listesi, "BIST")
                if sonuclar:
                    cols = st.columns(2)
                    for i, veri in enumerate(sonuclar):
                        with cols[i % 2]:
                            ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                            st.markdown(f"""<div class="balina-karti bist-card {ozel}"><h4>{veri['Sembol']}</h4><p>{veri['Fiyat']:.2f} TL</p><div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div></div>""", unsafe_allow_html=True)
            
            if tara_golden:
                st.info("Golden Cross (50 HO > 200 HO) taranıyor... Bu işlem veri yoğunluğu nedeniyle uzun sürebilir.")
                gc_list = []
                bar = st.progress(0)
                for i, sym in enumerate(bist_listesi):
                    try:
                        d = yf.download(sym, period="1y", interval="1d", progress=False)
                        if hasattr(d.columns, 'levels'): d.columns = d.columns.get_level_values(0)
                        if len(d) > 200:
                            sma50 = d['Close'].rolling(50).mean()
                            sma200 = d['Close'].rolling(200).mean()
                            # Kesişim Kontrolü (Son 3 günde kesmiş mi?)
                            if sma50.iloc[-1] > sma200.iloc[-1] and sma50.iloc[-5] < sma200.iloc[-5]:
                                gc_list.append(sym.replace(".IS",""))
                    except: pass
                    bar.progress((i+1)/len(bist_listesi))
                bar.empty()
                
                if gc_list:
                    st.success(f"⚔️ GOLDEN CROSS YAKALANANLAR: {', '.join(gc_list)}")
                    for g in gc_list:
                        st.markdown(f"<div class='balina-karti bist-card golden' style='text-align:center;'><h3>⚔️ {g}</h3><p>SMA 50, SMA 200'ü Yukarı Kesti!</p></div>", unsafe_allow_html=True)
                else:
                    st.warning("Şu an yeni bir Golden Cross oluşumu yok.")

@st.cache_data(ttl=180, show_spinner=False)
def verileri_getir(liste, piyasa_tipi):
    bulunanlar = []
    bar = st.progress(0, text=f"{piyasa_tipi} Taranıyor...")
    for i, symbol in enumerate(liste):
        try:
            df = yf.download(symbol, period="3d", interval="1h", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if len(df) > 10:
                son = df.iloc[-1]
                hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                durum = None; renk = "gray"
                
                if "HDFGS" in symbol:
                    durum = "HDFGS TAKİP" if kat <= 1.2 else "HDFGS HAREKETLİ 🦅"; renk = "buy" if degisim > 0 else "sell"
                elif kat > 2.5:
                    durum = "BALİNA 🚀" if degisim > 0 else "SATIŞ 🔻"; renk = "buy" if degisim > 0 else "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Sinyal": durum, "Renk": renk})
            bar.progress((i+1)/len(liste)); time.sleep(0.01)
        except: continue
    bar.empty()
    return bulunanlar

# ==========================================
# GİRİŞ EKRANLARI (SABİT)
# ==========================================
def login_page():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🥸 PALA GİRİŞ</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["GİRİŞ", "KAYIT"])
    with t1:
        kul = st.text_input("Kullanıcı Adı"); sif = st.text_input("Şifre", type="password")
        if st.checkbox("Sistemi Başlat"):
            if st.button("ADMİN KUR"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "portfoy": []}}
                save_db(st.session_state.db); st.success("Admin Hazır")
        if st.button("GİRİŞ"):
            db=load_db()
            if kul in db and db[kul]['sifre']==sif: st.session_state.login_user=kul; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("Hatalı!")
    with t2:
        y_kul = st.text_input("Yeni Nick"); y_ad = st.text_input("Ad Soyad"); y_sif = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT OL"):
            db=load_db()
            if y_kul not in db: db[y_kul]={"sifre":y_sif, "isim":y_ad, "onay":False, "rol":"user", "portfoy":[]}; save_db(db); st.success("Kaydolundu!")
            else: st.error("Alınmış!")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 ONAY BEKLENİYOR ($500)</h1>", unsafe_allow_html=True)
    if st.button("ÇIKIŞ"): st.session_state.login_user=None; st.rerun()

# ROUTER
if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
