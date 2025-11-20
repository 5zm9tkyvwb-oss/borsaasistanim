 import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Global Balina Avcısı", layout="wide", page_icon="🐳")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .balina-karti { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #374151; }
    .bist-card { background: linear-gradient(90deg, #0f2027 0%, #2c5364 100%); border-left: 5px solid #38bdf8; }
    .crypto-card { background: linear-gradient(90deg, #201c05 0%, #423808 100%); border-left: 5px solid #facc15; }
    .signal-box { padding: 5px 10px; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 14px; }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 15px #FFD700; }
    </style>
""", unsafe_allow_html=True)

st.title("🐳 MEGALODON BALİNA AVCISI")
st.caption("HDFGS • BIST TÜM (450+ HİSSE) • KRİPTO")

# --- DEVASA VERİ HAVUZU ---

# BIST GENEL (Hacimli olanların tamamı)
bist_listesi = [
    "HDFGS.IS", # 1 NUMARA SENİN
    # BIST 30 & 50 & 100
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
    "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", 
    "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS", 
    "TCELL.IS", "ENKAI.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "PGSUS.IS", "KOZAL.IS", 
    "KOZAA.IS", "IPEKE.IS", "TKFEN.IS", "HALKB.IS", "VAKBN.IS", "TSKB.IS", "ALARK.IS", 
    "TAVHL.IS", "MGROS.IS", "SOKM.IS", "MAVI.IS", "AEFES.IS", "AGHOL.IS", "AKSEN.IS", 
    "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS", 
    "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "BRSAN.IS", "CIMSA.IS", 
    "DOHOL.IS", "ECILC.IS", "ENJSA.IS", "GLYHO.IS", "GWIND.IS", "ISGYO.IS", "ISMEN.IS", 
    "KLSER.IS", "KORDS.IS", "KZBGY.IS", "OTKAR.IS", "QUAGR.IS", "SKBNK.IS", "SOKE.IS", 
    "TRGYO.IS", "TSPOR.IS", "ULKER.IS", "VESBE.IS", "YYLGD.IS", "ZOREN.IS",
    # ANA PAZAR & YILDIZ PAZAR GENİŞLEME
    "ACSEL.IS", "ADEL.IS", "ADESE.IS", "AFYON.IS", "AGESA.IS", "AKCNS.IS", "AKFGY.IS", 
    "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKYHO.IS", "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", 
    "ALGYO.IS", "ALKIM.IS", "ALMAD.IS", "ANELE.IS", "ANGEN.IS", "ANHYT.IS", "ANSGR.IS", 
    "ARASE.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARZUM.IS", "ASGYO.IS", "ASUZU.IS", 
    "ATAGY.IS", "ATAKP.IS", "ATP.IS", "AVGYO.IS", "AVHOL.IS", "AVOD.IS", "AYCES.IS", 
    "AYDEM.IS", "AYEN.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", 
    "BANVT.IS", "BARMA.IS", "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BERA.IS", "BEYAZ.IS", 
    "BFREN.IS", "BIENY.IS", "BIGCH.IS", "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", 
    "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BOSSA.IS", "BRISA.IS", "BRKO.IS", 
    "BRKSN.IS", "BRKV.IS", "BRLSM.IS", "BRMEN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", 
    "BUCIM.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASA.IS", 
    "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS", "CIMSA.IS", "CLEBI.IS", 
    "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", 
    "CVKMD.IS", "CWENE.IS", "DAGHL.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", 
    "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS", "DEVA.IS", "DGATE.IS", "DGGYO.IS", 
    "DGNMO.IS", "DIRIT.IS", "DITAS.IS", "DMSAS.IS", "DNISI.IS", "DOBUR.IS", "DOCO.IS", 
    "DOGUB.IS", "DOHOL.IS", "DOKTA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", 
    "ECILC.IS", "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EGEEN.IS", "EGGUB.IS", "EGPRO.IS", 
    "EGSER.IS", "EKGYO.IS", "EKIZ.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS", 
    "EMNIS.IS", "ENJSA.IS", "ENKAI.IS", "ENSRI.IS", "EPLAS.IS", "ERBOS.IS", "ERCB.IS", 
    "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS", "ETILR.IS", "ETYAT.IS", 
    "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "FADE.IS", "FENER.IS", 
    "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS", "FROTO.IS", 
    "FZLGY.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS", "GENTS.IS", 
    "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", 
    "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GSDDE.IS", "GSDHO.IS", 
    "GSRAY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HALKS.IS", "HATSN.IS", 
    "HATEK.IS", "HDFGS.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", 
    "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS", "IDGYO.IS", "IEYHO.IS", 
    "IHAAS.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IHYAY.IS", "IMASM.IS", 
    "INDES.IS", "INFO.IS", "INGRM.IS", "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", 
    "ISBIR.IS", "ISBTR.IS", "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS", "ISGYO.IS", 
    "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "ISYAT.IS", "ITTFH.IS", "IZFAS.IS", 
    "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", 
    "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KERVT.IS", 
    "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLMSN.IS", "KLNMA.IS", 
    "KLSER.IS", "KMPUR.IS", "KNFRT.IS", "KONKA.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", 
    "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMA.IS", "KRDMB.IS", "KRDMD.IS", "KRGYO.IS", 
    "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KRVGD.IS", "KSTUR.IS", "KTLEV.IS", 
    "KTSKR.IS", "KUTPO.IS", "KUVVA.IS", "KUYAS.IS", "KZBGY.IS", "KZGYO.IS", "LIDER.IS", 
    "LIDFA.IS", "LINK.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MACKO.IS", 
    "MAGEN.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS", "MAVI.IS", 
    "MEDTR.IS", "MEGAP.IS", "MEPET.IS", "MERCN.IS", "MERIT.IS", "MERKO.IS", "METRO.IS", 
    "METUR.IS", "MGROS.IS", "MIATK.IS", "MIPAZ.IS", "MMCAS.IS", "MNDRS.IS", "MOBTL.IS", 
    "MPARK.IS", "MRGYO.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", 
    "NATEN.IS", "NETAS.IS", "NIBAS.IS", "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", 
    "ODAS.IS", "OFSYM.IS", "ONCSM.IS", "ORCAY.IS", "ORGE.IS", "ORMA.IS", "OSMEN.IS", 
    "OSTIM.IS", "OTKAR.IS", "OTTO.IS", "OYAKC.IS", "OYAYO.IS", "OYLUM.IS", "OYYAT.IS", 
    "OZGYO.IS", "OZKGY.IS", "OZRDN.IS", "OZSUB.IS", "PAGYO.IS", "PAMEL.IS", "PAPIL.IS", 
    "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEGYO.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", 
    "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS", "PKART.IS", "PKENT.IS", "PLTUR.IS", 
    "PNLSN.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKAB.IS", "PRKME.IS", 
    "PRZMA.IS", "PSDTC.IS", "PSGYO.IS", "QNBFB.IS", "QNBFL.IS", "QUAGR.IS", "RALYH.IS", 
    "RAYSG.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", 
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SAMAT.IS", "SANEL.IS", "SANFM.IS", "SANKO.IS", 
    "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEKFK.IS", "SEKUR.IS", "SELEC.IS", 
    "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", 
    "SMART.IS", "SMRTG.IS", "SNGYO.IS", "SNKRN.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS", 
    "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TATGD.IS", 
    "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTU.IS", "TERA.IS", "TETMT.IS", 
    "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TLMAN.IS", "TMPOL.IS", "TMSN.IS", 
    "TNZTP.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRILC.IS", "TSGYO.IS", "TSKB.IS", 
    "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUKAS.IS", "TUPRS.IS", "TURGG.IS", 
    "TURSG.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS", "ULUFA.IS", "ULUSE.IS", "ULUUN.IS", 
    "UMPAS.IS", "UNLU.IS", "USAK.IS", "UZERB.IS", "VAKBN.IS", "VAKFN.IS", "VAKKO.IS", 
    "VANGD.IS", "VBTYZ.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", 
    "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS", 
    "YGYO.IS", "YKBNK.IS", "YKSLN.IS", "YONGA.IS", "YUNSA.IS", "YYAPI.IS", "YYLGD.IS", 
    "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS"
]

# KRİPTO KATEGORİLERİ
crypto_sectors = {
    "🏆 Top 50 (Major)": [
        "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "AVAX-USD", 
        "DOGE-USD", "DOT-USD", "TRX-USD", "LINK-USD", "MATIC-USD", "LTC-USD", "BCH-USD",
        "UNI-USD", "ATOM-USD", "XLM-USD", "ETC-USD", "FIL-USD", "HBAR-USD", "APT-USD",
        "NEAR-USD", "VET-USD", "ICP-USD", "ARB-USD", "OP-USD", "INJ-USD", "RNDR-USD"
    ],
    "🐸 Meme Coinler": [
        "DOGE-USD", "SHIB-USD", "PEPE-USD", "FLOKI-USD", "BONK-USD", "WIF-USD", 
        "BOME-USD", "MEME-USD", "DOGE2-USD", "BabyDoge-USD"
    ],
    "🤖 Yapay Zeka (AI)": [
        "FET-USD", "RNDR-USD", "AGIX-USD", "OCEAN-USD", "GRT-USD", "WLD-USD", 
        "NEAR-USD", "INJ-USD", "ROSE-USD", "AKT-USD"
    ]
}

# --- TARAMA FONKSİYONU ---
def tarama_yap(liste, piyasa_tipi):
    sinyaller = []
    text = f"BIST Dev Liste ({len(liste)} Hisse) Taranıyor... Bu işlem zaman alabilir ⏳" if piyasa_tipi == "BIST" else "Kripto Taranıyor..."
    my_bar = st.progress(0, text=text)
    
    adim = 1.0 / len(liste)
    suan = 0.0

    for symbol in liste:
        try:
            # YAHOO KORUMASI (Zorunlu Bekleme)
            # 450 hisse x 0.1 sn = Minimum 45 saniye sürer.
            time.sleep(0.05) 
            
            period = "5d" if piyasa_tipi == "BIST" else "2d"
            df = yf.download(symbol, period=period, interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son = df.iloc[-1]
                hacim_son = son['Volume']
                hacim_ort = df['Volume'].rolling(24).mean().iloc[-1]
                kat = hacim_son / hacim_ort if hacim_ort > 0 else 0
                
                fiyat = son['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                durum = None
                renk = "gray"
                
                if "HDFGS" in symbol:
                    if kat > 1.5:
                        durum = "HDFGS HAREKETLİ 🦅"
                        renk = "buy" if degisim > 0 else "sell"
                
                elif kat > 2.5: # Filtreyi 2.5 yaptım ki her şeyi göstermesin, sadece gerçek balinaları göstersin
                    if degisim > 0.5:
                        durum = "WHALE BUY 🚀"
                        renk = "buy"
                    elif degisim < -0.5:
                        durum = "WHALE DUMP 🔻"
                        renk = "sell"
                
                if durum:
                    isim = symbol.replace(".IS", "").replace("-USD", "")
                    sinyaller.append({
                        "Sembol": isim, "Fiyat": fiyat, "Degisim": degisim,
                        "HacimKat": kat, "Sinyal": durum, "Renk": renk
                    })
        except:
            pass
        
        suan += adim
        my_bar.progress(min(suan, 1.0), text=f"{symbol} taranıyor...")
    
    my_bar.empty()
    return sinyaller

# --- ARAYÜZ ---
tab1, tab2 = st.tabs(["🏙️ BORSA (450+ HİSSE)", "₿ KRİPTO"])

with tab1:
    st.header(f"Borsa İstanbul Mega Tarama")
    st.warning("⚠️ DİKKAT: Bu liste çok geniş olduğu için tarama 3-5 dakika sürebilir. Sayfayı kapatmayın!")
    
    if st.button("DEV TARAMAYI BAŞLAT 📡", key="btn_bist", type="primary"):
        sonuclar = tarama_yap(bist_listesi, "BIST")
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    ozel = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                    st.markdown(f"""
                    <div class="balina-karti bist-card {ozel}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#e0f2fe;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Tarama bitti. Okyanus sakin.")

with tab2:
    st.header("Kripto Sektör Tarayıcısı")
    secilen_sektor = st.selectbox("Hangi Sektörü Tarayalım?", list(crypto_sectors.keys()))
    tarama_listesi = crypto_sectors[secilen_sektor]
    
    if st.button("KRİPTOYU TARA 📡", key="btn_kripto", type="primary"):
        sonuclar = tarama_yap(tarama_listesi, "KRIPTO")
        if sonuclar:
            st.success(f"{len(sonuclar)} Balina Yakalandı!")
            cols = st.columns(2)
            for i, veri in enumerate(sonuclar):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="balina-karti crypto-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <h3 style="margin:0; color:#fef08a;">{veri['Sembol']}</h3>
                                <p style="margin:0; font-size:16px;">${veri['Fiyat']:.4f} <span style="color:{'#4ade80' if veri['Degisim']>0 else '#f87171'}">(%{veri['Degisim']:.2f})</span></p>
                            </div>
                            <div style="text-align:right;">
                                <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                                <p style="margin:3px 0 0 0; font-size:12px; color:#94a3b8;">Hacim: {veri['HacimKat']:.1f}x</p>
                            </div>
                        </div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("Bu sektörde hareket yok.")
