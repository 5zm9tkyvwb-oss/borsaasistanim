import streamlit as st
import yfinance as yf
import pandas as pd
import time
import random
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala ile İyi Tahtalar", layout="wide", page_icon="🥸")

# --- GİRİŞ KONTROLÜ ---
if 'giris_yapildi' not in st.session_state:
    st.session_state.giris_yapildi = False

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
    st.markdown("<div class='vip-card'><h2>⚜️ VIP GİRİŞ BİLETİ</h2><p>Destek, Direnç, Kırılım ve HDFGS Özel Takibi.</p><div class='price-tag'>$500</div><p style='color:#FFD700; font-weight:bold;'>LIFETIME ACCESS</p></div>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💳 Ödeme")
        st.markdown("<div class='odeme-yontemi'><strong>₿ KRİPTO (USDT)</strong><br><code style='color:#FFD700'>TXaBCdef1234567890...</code></div>", unsafe_allow_html=True)
    with col2:
        st.subheader("🔐 Giriş")
        with st.form("giris_formu"):
            kullanici = st.text_input("Kullanıcı Adı")
            sifre = st.text_input("Şifre", type="password")
            giris_btn = st.form_submit_button("GİRİŞ 🚀")
            if giris_btn:
                if kullanici == "admin" and sifre == "pala500": 
                    st.session_state.giris_yapildi = True
                    st.rerun()
                else:
                    st.error("Hatalı Şifre!")

# ==========================================
# 2. ANA UYGULAMA (PRO ANALİZ)
# ==========================================
def ana_uygulama():
    st.markdown("""
        <style>
        .stApp { background-color: #0a0e17; color: white; }
        .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
        .balina-karti { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #374151; position: relative; overflow: hidden; }
        
        .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 5px solid #38bdf8; }
        .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 5px solid #facc15; }
        
        .signal-box { padding: 5px 10px; border-radius: 6px; font-weight: bold; font-size: 13px; display: inline-block; }
        .buy { background-color: #059669; color: white; box-shadow: 0 0 10px #059669; }
        .sell { background-color: #dc2626; color: white; box-shadow: 0 0 10px #dc2626; }
        .breakout { background-color: #7c3aed; color: white; box-shadow: 0 0 10px #8b5cf6; animation: flash 1s infinite; }
        
        .seviye-kutu { display: flex; justify-content: space-between; font-size: 12px; margin-top: 8px; background: rgba(0,0,0,0.3); padding: 5px; border-radius: 5px; }
        .pala-yorum { margin-top: 8px; font-style: italic; color: #FFD700; font-size: 13px; font-weight: bold; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 5px; }
        
        .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px #FFD700; animation: pulse 1.5s infinite; }
        
        @keyframes pulse { 0% { box-shadow: 0 0 5px #FFD700; } 50% { box-shadow: 0 0 25px #FFA500; } 100% { box-shadow: 0 0 5px #FFD700; } }
        @keyframes flash { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        </style>
        <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>İYİ TAHTALAR</div>
    """, unsafe_allow_html=True)

    if st.button("ÇIKIŞ"):
        st.session_state.giris_yapildi = False
        st.rerun()

    st.title("🥸 PALA İLE İYİ TAHTALAR")
    st.caption("Destek/Direnç Analizi • Kırılım Takibi • HDFGS Özel")

    # --- HİSSE LİSTESİ (200'e yakın) ---
    bist_listesi = [
        "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
        "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", 
        "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", "ALARK.IS", "TAVHL.IS", 
        "MGROS.IS", "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", 
        "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "KOZAL.IS", "PGSUS.IS", "TOASO.IS", 
        "ENKAI.IS", "TCELL.IS", "VESTL.IS", "ARCLK.IS", "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", 
        "VAKBN.IS", "TSKB.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS", "AKSEN.IS", "BRSAN.IS", 
        "CIMSA.IS", "DOHOL.IS", "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS", "ISMEN.IS", 
        "KLSER.IS", "KORDS.IS", "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS", "SOKE.IS", "TRGYO.IS", 
        "TSPOR.IS", "ULKER.IS", "VESBE.IS", "YYLGD.IS", "ZOREN.IS", "AKFGY.IS", "ALBRK.IS", "ASGYO.IS",
        "AYDEM.IS", "BAGFS.IS", "BERA.IS", "BIOEN.IS", "BOBET.IS", "BRYAT.IS", "CCOLA.IS", "CEMTS.IS",
        "CWENE.IS", "ECZYT.IS", "GENIL.IS", "GSDHO.IS", "HALKS.IS", "HUNER.IS", "IHLAS.IS", "IMASM.IS",
        "IZMDC.IS", "KARSN.IS", "KMPUR.IS", "KONYA.IS", "KOPOL.IS", "MAGEN.IS", "MTRKS.IS", "NTHOL.IS",
        "PENTA.IS", "PSGYO.IS", "SDTTR.IS", "SELEC.IS", "SNGYO.IS", "TATGD.IS", "TUKAS.IS", "TURSG.IS",
        "VERUS.IS", "YEOTK.IS", "ZRGYO.IS", "ADESE.IS", "AKSA.IS", "ALGYO.IS", "ALKIM.IS", "ANHYT.IS",
        "ANSGR.IS", "AVGYO.IS", "AYGAZ.IS", "BANVT.IS", "BASGZ.IS", "BFREN.IS", "BIENY.IS", "BRLSM.IS",
        "BUCIM.IS", "CEMAS.IS", "CLEBI.IS", "DEVA.IS", "DGGYO.IS", "DOCO.IS", "EBEBK.IS", "ECZYT.IS",
        "EGGUB.IS", "ERBOS.IS", "ESEN.IS", "FADE.IS", "FENER.IS", "GEDIK.IS", "GOLTS.IS", "GOODY.IS",
        "GOZDE.IS", "GSRAY.IS", "HLGYO.IS", "INDES.IS", "INFO.IS", "INVEO.IS", "ISFIN.IS", "ISGSY.IS",
        "JANTS.IS", "KAREL.IS", "KARTN.IS", "KERVT.IS", "KIMMR.IS", "KLGYO.IS", "KMPUR.IS", "KNFRT.IS",
        "LOGO.IS", "MAALT.IS", "MAKIM.IS", "MERCN.IS", "METRO.IS", "MIATK.IS", "MPARK.IS", "NATEN.IS",
        "NETAS.IS", "NUGYO.IS", "NUHCM.IS", "OFSYM.IS", "ORGE.IS", "OZKGY.IS", "OZSUB.IS", "PAGYO.IS",
        "PAPIL.IS", "PARSN.IS", "PCILT.IS", "PEKGY.IS", "POLHO.IS", "PRKME.IS", "QNBFB.IS", "RYSAS.IS",
        "SAYAS.IS", "SEKFK.IS", "TEKTU.IS", "TMSN.IS", "TRCAS.IS", "TRILC.IS", "TSGYO.IS", "TTRAK.IS",
        "TURGG.IS", "ULUSE.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS", "VAKKO.IS", "VKGYO.IS", "YATAS.IS",
        "YAYLA.IS", "YGGYO.IS", "YKSLN.IS", "YUNSA.IS"
    ]

    kripto_listesi = ["BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "DOGE-USD", "ADA-USD", "AVAX-USD", "SHIB-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "LINK-USD", "ATOM-USD", "FET-USD", "RNDR-USD", "PEPE-USD", "FLOKI-USD", "NEAR-USD", "ARB-USD", "APT-USD", "SUI-USD", "INJ-USD", "OP-USD", "LDO-USD", "FIL-USD", "HBAR-USD", "VET-USD", "ICP-USD", "GRT-USD", "MKR-USD", "AAVE-USD", "SNX-USD", "ALGO-USD", "SAND-USD", "MANA-USD", "WIF-USD", "BONK-USD", "BOME-USD"]

    # --- GAZA GETİREN SÖZLER ---
    laf_sok = [
        "Tahtacı masaya vurdu! 👊", "Roketler ateşlendi 🚀", "Para şelalesi akıyor 💸", 
        "Balina ağzını açtı 🐋", "Bu tahta yanıyor 🔥", "Pala iş başında 🥸", 
        "Malı topluyorlar sessizce...", "Kemerleri bağla uçuş var ✈️"
    ]

    # --- TARAMA MOTORU ---
    @st.cache_data(ttl=180, show_spinner=False)
    def verileri_getir(liste, piyasa_tipi):
        bulunanlar = []
        toplam = len(liste)
        bar = st.progress(0, text=f"Pala {piyasa_tipi} Piyasasını Süzüyor...")
        
        for i, symbol in enumerate(liste):
            try:
                # Pivot hesabı için 2 günlük veri yeterli
                df = yf.download(symbol, period="3d", interval="1h", progress=False)
                if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
                
                if len(df) > 10:
                    son = df.iloc[-1]
                    # Pivot / Destek / Direnç Hesabı (Dünkü Kapanışa Göre)
                    # Son gün değil, bir önceki günün High/Low/Close'unu alıyoruz ki bugünün sınırlarını çizelim
                    prev = df.iloc[-15] # Yaklaşık bir önceki seans/gün ortalaması gibi davranır saatlikte
                    
                    pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
                    r1 = (2 * pivot) - prev['Low']
                    s1 = (2 * pivot) - prev['High']
                    
                    hacim_son = son['Volume']
                    hacim_ort = df['Volume'].rolling(20).mean().iloc[-1]
                    kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                    
                    fiyat = son['Close']
                    degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                    
                    durum = None; renk = "gray"; aciklama = ""
                    pala_yorumu = ""
                    
                    # KIRILIM KONTROLÜ
                    kirilim = ""
                    if fiyat > r1: kirilim = "DİRENÇ KIRILDI 💥"
                    elif fiyat < s1: kirilim = "DESTEK KIRILDI 🩸"
                    
                    # HDFGS Kuralı
                    if "HDFGS" in symbol:
                        durum = "HDFGS ÖZEL TAKİP"
                        if kat > 1.1: 
                            aciklama = "Hacim Artışı Var!"
                            renk = "buy" if degisim > 0 else "sell"
                            pala_yorumu = "Bizim oğlan hareketlendi, takipte kal!"
                        else:
                            aciklama = "Hacim Stabil"
                            renk = "gray"
                            pala_yorumu = "Şu an dinleniyor, güç topluyor."
                            
                    # Diğerleri için Balina Filtresi
                    elif kat > 2.5 or (kat > 1.5 and kirilim != ""):
                        if degisim > 0.5: 
                            durum = "BALİNA GİRDİ 🚀"
                            renk = "buy" if kirilim == "" else "breakout" # Mor renk kırılım varsa
                            aciklama = f"Hacim {kat:.1f}x"
                            pala_yorumu = random.choice(laf_sok)
                            if kirilim: pala_yorumu = f"{kirilim} - {pala_yorumu}"
                            
                        elif degisim < -0.5: 
                            durum = "BALİNA SATIYOR 🔻"
                            renk = "sell"
                            aciklama = "Yüklü Çıkış"
                            pala_yorumu = "Dikkat et, mal boşaltıyorlar!"

                    if durum:
                        isim = symbol.replace(".IS", "").replace("-USD", "")
                        # Sort önceliği: HDFGS en başa (999), Kırılım varsa 2. sıra (500), Hacim 3. sıra
                        oncelik = 999 if "HDFGS" in symbol else (500 if kirilim else kat)
                        
                        bulunanlar.append({
                            "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim, 
                            "HacimKat": kat, "Sinyal": durum, "Renk": renk, 
                            "Aciklama": aciklama, "Oncelik": oncelik,
                            "Destek": s1, "Direnc": r1, "Yorum": pala_yorumu
                        })
                
                bar.progress((i + 1) / toplam)
                time.sleep(0.01)
            except: continue
        bar.empty()
        
        # Sıralama ve İlk 20
        bulunanlar = sorted(bulunanlar, key=lambda x: x['Oncelik'], reverse=True)
        return bulunanlar[:20]

    # --- ARAYÜZ ---
    tab1, tab2 = st.tabs(["🏙️ BIST (TOP 20)", "₿ KRİPTO (TOP 20)"])
    
    with tab1:
        if st.button("TAHTALARI TARA 📡", key="bist_btn"): st.cache_data.clear(); st.rerun()
        sonuclar = verileri_getir(bist_listesi, "BIST")
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
                                <p style="margin:0; font-size:16px; font-weight:bold;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else ('#f87171' if veri['Degisim']<0 else 'white')}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">{veri['Aciklama']}</p>
                            </div>
                        </div>
                        <div class="seviye-kutu">
                            <span style="color:#4ade80;">🛡️ Destek: {veri['Destek']:.2f}</span>
                            <span style="color:#f87171;">🧱 Direnç: {veri['Direnc']:.2f}</span>
                        </div>
                        <div class="pala-yorum">💬 {veri['Yorum']}</div>
                    </div>""", unsafe_allow_html=True)
        else: st.info("Pala şu an çay içiyor, tahtalar sakin.")

    with tab2:
        if st.button("COINLERİ TARA 📡", key="kripto_btn"): st.cache_data.clear(); st.rerun()
        sonuclar_kripto = verileri_getir(kripto_listesi, "KRIPTO")
        if sonuclar_kripto:
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar_kripto):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="balina-karti crypto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h4 style="margin:0; color:#fef08a;">{veri['Sembol']}</h4>
                                <p style="margin:0; font-size:16px; font-weight:bold;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:2px 0 0 0; font-size:11px; color:#94a3b8;">{veri['Aciklama']}</p>
                            </div>
                        </div>
                        <div class="seviye-kutu">
                            <span style="color:#4ade80;">🛡️ S: {veri['Destek']:.4f}</span>
                            <span style="color:#f87171;">🧱 R: {veri['Direnc']:.4f}</span>
                        </div>
                        <div class="pala-yorum">💬 {veri['Yorum']}</div>
                    </div>""", unsafe_allow_html=True)
        else: st.info("Kripto tarafı sakin.")

if st.session_state.giris_yapildi:
    ana_uygulama()
else:
    login_ekrani()
