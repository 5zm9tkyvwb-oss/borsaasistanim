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
                "mesajlar": [], 
                "loglar": [],
                "portfoy": []
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
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- TASARIM (SİYAH & ALTIN) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #e5e5e5 !important; }
    
    /* BUTONLAR */
    div.stButton > button {
        background-color: #000000 !important; color: #FFD700 !important; 
        border: 2px solid #FFD700 !important; border-radius: 12px !important; 
        font-weight: bold !important; height: 50px !important; width: 100% !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover { 
        background-color: #FFD700 !important; color: #000000 !important; 
        transform: scale(1.02) !important; 
    }
    
    /* INPUT */
    .stTextInput input, .stNumberInput input { 
        background-color: #111 !important; color: #FFD700 !important; 
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
    
    /* KARTLAR */
    .balina-karti { padding: 12px; border-radius: 12px; margin-bottom: 8px; border: 1px solid #333; background-color: #111; }
    .bist-card { border-left: 4px solid #38bdf8; }
    .crypto-card { border-left: 4px solid #facc15; }
    .signal-box { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; display: inline-block; }
    .buy { background-color: #064e3b; color: #34d399; } 
    .sell { background-color: #450a0a; color: #f87171; } 
    .future { background-color: #4c1d95; color: #a78bfa; border: 1px solid #a78bfa; }
    
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.6); } 100% { box-shadow: 0 0 5px rgba(255,215,0,0.2); } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        # Son mesaja bak, aynısıysa ekleme
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][0]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
    except: pass

# --- GRAFİK & ANALİZ MOTORU ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            prev = df.iloc[-2]
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']
            s1 = (2 * pivot) - prev['High']
            
            # Grafik
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            
            # Çizgiler
            fig.add_hline(y=r1, line_dash="dash", line_color="red", annotation_text=f"DİRENÇ: {r1:.2f}")
            fig.add_hline(y=s1, line_dash="dash", line_color="green", annotation_text=f"DESTEK: {s1:.2f}")
            fig.add_hline(y=pivot, line_dash="dot", line_color="yellow", annotation_text="PİVOT")
            
            fig.update_layout(title=f"{symbol} PALA ANALİZİ", template="plotly_dark", height=450, xaxis_rangeslider_visible=False, plot_bgcolor='#FFFF00', paper_bgcolor='#0a0e17')
            
            # Haberler
            haberler = []
            try:
                news = yf.Ticker(symbol).news
                for n in news[:3]:
                    haberler.append(f"📰 [{n['title']}]({n['link']})")
            except: pass

            return fig, df.iloc[-1]['Close'], s1, r1, haberler
    except: 
        return None, None, None, None, None

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
    user = st.session_state.login_user
    db = st.session_state.db
    
    col_head = st.columns([8, 2])
    with col_head[0]:
        isim = db[user].get('isim', 'Üye')
        st.title("🥸 PALA İLE İYİ TAHTALAR")
        st.caption(f"Hoşgeldin {isim} | VIP Panel")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.login_user = None
            st.rerun()

    # Admin Paneli (Varsa)
    if st.session_state.db[st.session_state.login_user].get('rol') == 'admin':
        admin_dashboard()

    # MENÜ
    menu = st.radio("NAVİGASYON:", ["📊 PİYASA RADARI", "🩻 RÖNTGEN ODASI (TEMEL)", "⚔️ DÜELLO (KARŞILAŞTIR)", "💼 CÜZDAN", "🔥 ISI HARİTASI"], horizontal=True)
    st.divider()

    # ----------------------------------
    # MODÜL: RÖNTGEN ODASI (TEMEL ANALİZ)
    # ----------------------------------
    if menu == "🩻 RÖNTGEN ODASI (TEMEL)":
        st.subheader("🔍 Şirket Röntgeni (Temel Analiz)")
        sembol = st.text_input("Hisse Kodu:", "HDFGS.IS").upper()
        if st.button("RÖNTGENİ ÇEK ☢️"):
            with st.spinner("Bilanço inceleniyor..."):
                try:
                    t = yf.Ticker(sembol)
                    info = t.info
                    
                    col1, col2, col3 = st.columns(3)
                    fk = info.get('trailingPE', 'Yok')
                    pd_dd = info.get('priceToBook', 'Yok')
                    ozsermaye = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                    
                    col1.metric("F/K Oranı", f"{fk}")
                    col2.metric("PD/DD", f"{pd_dd}")
                    col3.metric("Özsermaye Karlılığı", f"%{ozsermaye:.2f}")
                    
                    st.write("---")
                    st.info(f"**Sektör:** {info.get('industry', 'Bilinmiyor')}")
                    st.write(f"**İş Tanımı:** {info.get('longBusinessSummary', 'Bilgi yok.')[:300]}...")
                    
                    # Yorum
                    if isinstance(fk, float) and fk < 10: st.success("✅ F/K 10'un altında, şirket ucuz görünüyor.")
                    elif isinstance(fk, float) and fk > 30: st.error("⚠️ F/K çok yüksek, primli olabilir.")
                    
                except: st.error("Temel veriler çekilemedi.")

    # ----------------------------------
    # MODÜL: DÜELLO (KARŞILAŞTIRMA)
    # ----------------------------------
    elif menu == "⚔️ DÜELLO (KARŞILAŞTIR)":
        st.subheader("🥊 Hisse Kapıştırma")
        c1, c2 = st.columns(2)
        h1 = c1.text_input("1. Hisse", "HDFGS.IS").upper()
        h2 = c2.text_input("2. Hisse", "THYAO.IS").upper()
        
        if st.button("KAPIŞTIR 🔥"):
            try:
                df1 = yf.download(h1, period="1y", interval="1d", progress=False)['Close']
                df2 = yf.download(h2, period="1y", interval="1d", progress=False)['Close']
                
                # Normalize et (Yüzdelik getiriye çevir)
                df1 = (df1 / df1.iloc[0]) * 100
                df2 = (df2 / df2.iloc[0]) * 100
                
                birlestir = pd.DataFrame({h1: df1, h2: df2})
                st.line_chart(birlestir)
                
                kazanan = h1 if df1.iloc[-1] > df2.iloc[-1] else h2
                st.success(f"🏆 KAZANAN: **{kazanan}** (Son 1 Yılda)")
            except: st.error("Veri hatası.")

    # ----------------------------------
    # MODÜL: CÜZDAN
    # ----------------------------------
    elif menu == "💼 CÜZDAN":
        st.subheader("💰 Varlık Yönetimi")
        with st.expander("➕ Hisse Ekle"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.text_input("Sembol", "HDFGS.IS").upper()
            y_mal = c2.number_input("Maliyet", value=2.63)
            y_adt = c3.number_input("Adet", value=194028)
            if c4.button("KAYDET"):
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != y_sem]
                db[user]["portfoy"].append({"sembol": y_sem, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("Kaydedildi!"); st.rerun()

        if "portfoy" in db[user] and db[user]["portfoy"]:
            toplam_deger = 0; toplam_kar = 0; data_pie = []
            table_data = []
            for p in db[user]["portfoy"]:
                try:
                    fiyat = yf.Ticker(p['sembol']).fast_info['last_price']
                    tutar = fiyat * p['adet']
                    kar = (fiyat - p['maliyet']) * p['adet']
                    toplam_deger += tutar; toplam_kar += kar
                    table_data.append({"Hisse": p['sembol'], "Adet": p['adet'], "Fiyat": f"{fiyat:.2f}", "Değer": f"{tutar:,.0f}", "Kar": f"{kar:,.0f}"})
                    data_pie.append({"Sembol": p['sembol'], "Deger": tutar})
                except: pass
            
            k1, k2 = st.columns(2)
            k1.metric("TOPLAM SERVET", f"{toplam_deger:,.0f} TL")
            k2.metric("NET KAR", f"{toplam_kar:,.0f} TL", delta_color="normal")
            
            c_pie, c_tab = st.columns([1, 2])
            with c_pie:
                if data_pie:
                    fig_pie = px.pie(pd.DataFrame(data_pie), values='Deger', names='Sembol', hole=0.4)
                    fig_pie.update_layout(template="plotly_dark", showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_pie, use_container_width=True)
            with c_tab: st.table(pd.DataFrame(table_data))
            
            sil = st.selectbox("Sil:", [p['sembol'] for p in db[user]["portfoy"]])
            if st.button("HİSSEYİ SİL"):
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sil]; save_db(db); st.rerun()
        else: st.info("Cüzdan boş.")

    # ----------------------------------
    # MODÜL: ISI HARİTASI
    # ----------------------------------
    elif menu == "🔥 ISI HARİTASI":
        st.subheader("🌍 PİYASA RÖNTGENİ")
        tur = st.selectbox("Piyasa:", ["BIST", "KRİPTO"])
        l_bist = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS"]
        l_kripto = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD"]
        liste = l_bist if tur == "BIST" else l_kripto
        
        if st.button("HARİTAYI ÇİZ 🗺️"):
            with st.spinner("Veriler işleniyor..."):
                data = []
                for sym in liste:
                    try:
                        t = yf.Ticker(sym); info = t.fast_info
                        fiyat = info.last_price; prev = info.previous_close
                        degisim = ((fiyat - prev) / prev) * 100
                        hacim = info.last_volume
                        if "HDFGS" in sym: hacim = hacim * 10 
                        data.append({"Sembol": sym.replace(".IS","").replace("-USD",""), "Degisim": degisim, "Hacim": hacim, "Fiyat": fiyat})
                    except: pass
                
                if data:
                    df_map = pd.DataFrame(data)
                    fig = px.treemap(df_map, path=['Sembol'], values='Hacim', color='Degisim',
                                     color_continuous_scale=['red', 'black', 'green'], color_continuous_midpoint=0, hover_data=['Fiyat'])
                    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=600)
                    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------
    # MODÜL: PİYASA RADARI (ANA)
    # ----------------------------------
    elif menu == "📊 PİYASA RADARI":
        
        # ŞANS ÇARKI
        if st.button("🎲 GÜNÜN ŞANSLI HİSSESİ"):
            pool = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "EREGL.IS", "SASA.IS", "HEKTS.IS"]
            secilen = random.choice(pool)
            st.balloons()
            st.success(f"🎰 PALA SEÇTİ: **{secilen.replace('.IS','')}**")
            st.session_state.secilen_hisse = secilen
            st.rerun()

        # ARAMA VE GRAFİK
        c_s1, c_s2 = st.columns([3, 1])
        arama = c_s1.text_input("Hisse/Coin Ara:", placeholder="HDFGS, BTC...").upper()
        if c_s2.button("ANALİZ ET 🚀"):
            symbol = f"{arama}.IS" if "-" not in arama and ".IS" not in arama and "USD" not in arama else arama
            st.session_state.secilen_hisse = symbol
            st.rerun()

        if st.session_state.secilen_hisse:
            with st.spinner(f"{st.session_state.secilen_hisse} İnceleniyor..."):
                fig, fiyat, s1, r1, haberler = grafik_ciz(st.session_state.secilen_hisse)
                if fig:
                    st.success(f"✅ {st.session_state.secilen_hisse} Analizi Hazır!")
                    k1, k2, k3, k4 = st.columns(4)
                    k1.metric("ANLIK FİYAT", f"{fiyat:.2f}")
                    k2.markdown(f"<div style='text-align:center; border:1px solid green; padding:10px; border-radius:10px;'><span style='color:gray'>GÜVENLİ ALIM</span><br><span class='buy-zone'>{s1:.2f}</span></div>", unsafe_allow_html=True)
                    k3.markdown(f"<div style='text-align:center; border:1px solid red; padding:10px; border-radius:10px;'><span style='color:gray'>KAR ALMA</span><br><span class='sell-zone'>{r1:.2f}</span></div>", unsafe_allow_html=True)
                    
                    atr_stop = fiyat * 0.97 # %3 Stop Loss
                    k4.markdown(f"<div style='text-align:center; border:1px solid orange; padding:10px; border-radius:10px;'><span style='color:gray'>ACİL ÇIKIŞ 🪂</span><br><span class='sell-zone' style='color:orange'>{atr_stop:.2f}</span></div>", unsafe_allow_html=True)
                    
                    st.write(""); st.plotly_chart(fig, use_container_width=True)
                    if haberler:
                        st.write("#### 📰 Son Haberler")
                        for h in haberler: st.markdown(h)
            
            if st.button("Kapat X", type="secondary"): st.session_state.secilen_hisse = None; st.rerun()
            st.divider()

        # TARAMA LİSTELERİ
        bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", "ENKAI.IS", "TCELL.IS"]
        kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

        @st.cache_data(ttl=180, show_spinner=False)
        def tarama_yap(liste, tip):
            bulunanlar = []; bar = st.progress(0, text=f"{tip} Taranıyor...")
            for i, symbol in enumerate(liste):
                try:
                    df = yf.download(symbol, period="3d", interval="1h", progress=False)
                    if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                    if len(df) > 10:
                        son = df.iloc[-1]; hacim_son = son['Volume']; hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]; kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                        fiyat = son['Close']; degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                        durum = None; renk = "gray"; aciklama = ""
                        if "HDFGS" in symbol:
                            durum = "HDFGS HAREKETLİ 🦅" if kat > 1.2 else "HDFGS SAKİN"; renk = "buy" if degisim>0 else "sell"; aciklama = "Anlık Hacim"
                        elif kat > 2.5:
                            durum = "BALİNA 🚀" if degisim > 0 else "SATIŞ 🔻"; renk = "buy" if degisim > 0 else "sell"; aciklama = f"Hacim {kat:.1f}x"
                        if durum:
                            isim = symbol.replace(".IS", "").replace("-USD", "")
                            bulunanlar.append({"Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, "HacimKat": kat, "Sinyal": durum, "Renk": renk, "Aciklama": aciklama, "Kod": symbol})
                    bar.progress((i+1)/len(liste)); time.sleep(0.01)
                except: continue
            bar.empty()
            return bulunanlar

        t1, t2 = st.tabs(["🏙️ BIST", "₿ KRİPTO"])
        with t1:
            if st.button("BIST TARA 📡"): st.cache_data.clear(); st.rerun()
            res = tarama_yap(bist_listesi, "BIST")
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
            res = tarama_yap(kripto_listesi, "KRIPTO")
            if res:
                cols = st.columns(2)
                for i, v in enumerate(res):
                    with cols[i%2]:
                        st.markdown(f"""<div class="balina-karti crypto-card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><h4 style="margin:0; color:#fef08a;">{v['Sembol']}</h4><p style="margin:0; font-size:14px;">${v['Fiyat']:.4f}</p></div><div style="text-align:right;"><div class="signal-box {v['Renk']}">{v['Sinyal']}</div><p style="margin:2px 0 0 0; font-size:10px; color:#94a3b8;">{v['Aciklama']}</p></div></div></div>""", unsafe_allow_html=True)
                        if st.button(f"GRAFİK 📈", key=f"c_{v['Sembol']}"): st.session_state.secilen_hisse = v['Kod']; st.rerun()
            else: st.info("Sakin.")

# ==========================================
# LOGIN / PAYMENT
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center;"><h1 style="color:#FFD700; font-size: 60px;">🥸 PALA GİRİŞ</h1></div>""", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["GİRİŞ YAP", "KAYIT OL"])
    with tab1:
        k = st.text_input("Kullanıcı"); s = st.text_input("Şifre", type="password")
        if st.checkbox("Sıfırla (Hata Alırsan)"):
            if st.button("SİSTEMİ ONAR"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("Admin Hazır")
        if st.button("GİRİŞ"):
            db=load_db()
            if k in db and db[k]['sifre']==s: st.session_state.login_user=k; st.session_state.giris_yapildi=True; st.rerun()
            else: st.error("Hatalı")
    with tab2:
        yk = st.text_input("Yeni Nick"); y_ad = st.text_input("Ad"); ys = st.text_input("Yeni Şifre", type="password")
        if st.button("KAYIT"):
            db=load_db()
            if yk not in db: db[yk] = {"sifre":ys, "isim":y_ad, "onay":False, "rol":"user", "mesajlar":[], "portfoy":[]}; save_db(db); st.success("Kaydolundu")
            else: st.error("Alınmış")

def payment_screen():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔒 ONAY BEKLENİYOR</h1>", unsafe_allow_html=True)
    st.markdown("<div class='vip-card'><h2>ÜYELİK: $500</h2><p>Ödemenizi yapın ve bildirin.</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='odeme-kutu'><strong>USDT</strong><br>TXa...</div>", unsafe_allow_html=True)
    with c2:
        msg = st.text_area("Dekont Bilgisi"); 
        if st.button("GÖNDER"):
            u=st.session_state.login_user; db=load_db()
            if "mesajlar" not in db[u]: db[u]["mesajlar"]=[]
            db[u]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] {msg}"); save_db(db); st.success("İletildi")
    if st.button("Çıkış"): st.session_state.login_user=None; st.rerun()

if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('onay') or db[u].get('rol')=='admin': ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user=None; st.rerun()
