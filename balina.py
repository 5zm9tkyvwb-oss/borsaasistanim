import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
import requests
import plotly.graph_objects as go
from datetime import datetime
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="PALA Balina Avcısı", layout="wide", page_icon="🦈")

# ==========================================
# 💰 AYARLAR & LİSTELER
# ==========================================
USDT_ADDRESS = "TV4DK7vckLWJciKSqhvY5hEpcw1Ka522AQ"
DENEME_SURESI_DK = 10 
BIST_HISSELERI = [
    "A1CAP", "ACSEL", "ADEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT",
    "AGYO", "AHGAZ", "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA",
    "AKSEN", "AKSGY", "AKSUE", "AKYHO", "ALARK", "ALBRK", "ALCAR", "ALCTL", "ALFAS", "ALGYO",
    "ALKA", "ALKIM", "ALMAD", "ALTNY", "ANELE", "ANGEN", "ANHYT", "ANSGR", "ARASE", "ARCLK",
    "ARDYZ", "ARENA", "ARSAN", "ARTMS", "ARZUM", "ASELS", "ASGYO", "ASTOR", "ASUZU", "ATAGY",
    "ATAKP", "ATATP", "ATEKS", "ATLAS", "ATSYH", "AVGYO", "AVHOL", "AVOD", "AVPGY", "AVTUR",
    "AYCES", "AYDEM", "AYEN", "AYES", "AYGAZ", "AZTEK", "BAGFS", "BAKAB", "BALAT", "BANVT",
    "BARMA", "BASCM", "BASGZ", "BAYRK", "BEGYO", "BERA", "BEYAZ", "BFREN", "BIENY", "BIGCH",
    "BIMAS", "BINHO", "BIOEN", "BIZIM", "BJKAS", "BLCYT", "BMSCH", "BMSTL", "BNTAS", "BOBET",
    "BORLS", "BOSSA", "BRISA", "BRKO", "BRKSN", "BRKVY", "BRLSM", "BRMEN", "BRSAN", "BRYAT",
    "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "BYDNR", "CANTE", "CATES", "CELHA",
    "CEMAS", "CEMTS", "CEOEM", "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO", "CRDFA",
    "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGH", "DAGI", "DAPGM", "DARDL", "DENGE", "DERHL",
    "DERIM", "DESA", "DESPC", "DEVA", "DGATE", "DGGYO", "DGNMO", "DIRIT", "DITAS", "DMSAS",
    "DNISI", "DOAS", "DOBUR", "DOCO", "DOGUB", "DOHOL", "DOKTA", "DURDO", "DYOBY", "DZGYO",
    "EBEBK", "ECILC", "ECLC", "ECZYT", "EDATA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO",
    "EGSER", "EKGYO", "EKIZ", "EKSUN", "ELITE", "EMKEL", "EMNIS", "ENJSA", "ENKAI", "ENSRI",
    "ENTRA", "EPLAS", "ERBOS", "ERCB", "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR",
    "ETYAT", "EUHOL", "EUKYO", "EUPWR", "EUREN", "EUYO", "EYGYO", "FADE", "FENER", "FLAP",
    "FMIZP", "FONET", "FORMT", "FORTE", "FRIGO", "FROTO", "FZLGY", "GARAN", "GARFA", "GEDIK",
    "GEDZA", "GENIL", "GENTS", "GEREL", "GESAN", "GIPTA", "GLBMD", "GLCVY", "GLRYH", "GLYHO",
    "GMTAS", "GOKNR", "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GSDDE", "GSDHO", "GSRAY",
    "GUBRF", "GWIND", "GZNMI", "HALKB", "HATEK", "HDFGS", "HEDEF", "HEKTS", "HKTM", "HLGYO",
    "HITIT", "HRKET", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDEAS", "IDGYO", "IEYHO", "IHAAS",
    "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IHYAY", "IMASM", "INDES", "INFO", "INGRM", "INTEM",
    "INVEO", "INVES", "IPEKE", "ISATR", "ISBIR", "ISBTR", "ISCTR", "ISDMR", "ISFIN", "ISGSY",
    "ISGYO", "ISKPL", "ISKUR", "ISMEN", "ISSEN", "ISYAT", "ITTFH", "IZENR", "IZFAS", "IZINV",
    "IZMDC", "JANTS", "KAPLM", "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KBORU",
    "KCAER", "KCHOL", "KENT", "KERVN", "KERVT", "KFEIN", "KGYO", "KIMMR", "KLGYO", "KLKIM",
    "KLMSN", "KLNMA", "KLRHO", "KMH", "KMPUR", "KNFRT", "KONKA", "KONTR", "KONYA", "KOPOL",
    "KORDS", "KOTON", "KOZAA", "KOZAL", "KRDMA", "KRDMB", "KRDMD", "KRGYO", "KRONT", "KRPLS",
    "KRSTL", "KRTEK", "KRVGD", "KSTUR", "KTLEV", "KTSKR", "KUTPO", "KUVVA", "KUYAS", "KZBGY",
    "KZGYO", "LIDER", "LILAK", "LIDFA", "LINK", "LKMNH", "LOGO", "LUKSK", "MAALT", "MACKO",
    "MAGEN", "MAKIM", "MAKTK", "MANAS", "MARBL", "MARKA", "MARTI", "MAVI", "MEDTR", "MEGAP",
    "MEGMT", "MEKAG", "MNDRS", "MNDTR", "MERCN", "MERIT", "MERKO", "METRO", "METUR", "MGROS",
    "MIATK", "MIPAZ", "MMCAS", "MNDRS", "MOBTL", "MOGAN", "MPARK", "MRGYO", "MRSHL", "MSGYO",
    "MTRKS", "MTRYO", "MZHLD", "NATEN", "NETAS", "NIBAS", "NTGAZ", "NUGYO", "NUHCM", "OBAMS",
    "OBASE", "ODAS", "ODINE", "OFSYM", "ONCSM", "ORCAY", "ORGE", "ORMA", "OSMEN", "OSTIM",
    "OTKAR", "OTTO", "OYAKC", "OYAYO", "OYLUM", "OYYAT", "OZGYO", "OZKGY", "OZRDN", "OZSUB",
    "PAGYO", "PAMEL", "PAPIL", "PARSN", "PASEU", "PASEU", "PCILT", "PEGYO", "PEKGY", "PENGD",
    "PENTA", "PETKM", "PETUN", "PGSUS", "PINSU", "PKART", "PKENT", "PLAT", "PLTUR", "PNLSN",
    "PNSUT", "POLHO", "POLTK", "PRDGS", "PRKAB", "PRKME", "PRZMA", "PSDTC", "PSGYO", "QNBFB",
    "QNBFL", "QUAGR", "RALYH", "RAYSG", "RNPOL", "REEDR", "RHEAG", "RODRG", "ROYAL", "RTALB",
    "RUBNS", "RYGYO", "RYSAS", "SAFKR", "SAHOL", "SAMAT", "SANEL", "SANFM", "SANKO", "SARKY",
    "SASA", "SAYAS", "SDTTR", "SEKFK", "SEKUR", "SELEC", "SELGD", "SELVA", "SEYKM", "SILVR",
    "SISE", "SKBNK", "SKTAS", "SKYMD", "SMRTG", "SNGYO", "SNKRN", "SNPAM", "SODSN", "SOKE",
    "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SUWEN", "TABGD", "TARKM", "TATEN", "TATGD",
    "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTU", "TERA", "TETMT", "TGSAS", "THYAO", "TKFEN",
    "TKNSA", "TLMAN", "TMPOL", "TMSN", "TNZTP", "TOASO", "TRCAS", "TRGYO", "TRILC", "TSGYO",
    "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TURGG", "TURSG", "UFUK",
    "ULAS", "ULKER", "ULUFA", "ULUSE", "ULUUN", "UMPAS", "UNLU", "USAK", "UZERB", "VAKBN",
    "VAKFN", "VAKKO", "VANGD", "VBTYZ", "VERUS", "VESBE", "VESTL", "VKFYO", "VKGYO", "VKING",
    "VRGYO", "YAPRK", "YATAS", "YAYLA", "YEOTK", "YESIL", "YGGYO", "YGYO", "YKBNK", "YKSLN",
    "YUNSA", "YYAPI", "YYLGD", "ZEDUR", "ZOREN", "ZRGYO",
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD", "DOGE-USD", "SHIB-USD"
]
BIST_HISSELERI = sorted(list(set(BIST_HISSELERI)))

# ==========================================
# 🚨 TELEGRAM & VERİTABANI
# ==========================================
BOT_TOKEN = "8339988180:AAEzuiyBWo4lwxD73rDvjNy2k5wcL42EnUQ"
MY_CHAT_ID = "1252288326"

def send_telegram(message):
    if BOT_TOKEN and MY_CHAT_ID:
        try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"})
        except: pass

DB_FILE = "users_db.json"
def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f)
def load_db():
    if not os.path.exists(DB_FILE):
        default_db = {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "rol": "admin", "mesajlar": [], "duyuru": "", "kayit_tarihi": time.time()}}
        save_db(default_db); return default_db
    try: return json.load(open(DB_FILE, "r"))
    except: return {}

if 'db' not in st.session_state: st.session_state.db = load_db()
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None
if 'odeme_modu' not in st.session_state: st.session_state.odeme_modu = False

# --- TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #050a14 !important; background-image: radial-gradient(rgba(0, 255, 249, 0.1) 1px, transparent 1px); background-size: 50px 50px; color: #e6e6e6 !important; font-family: 'Orbitron', sans-serif; }
    .vip-offer-box { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 15px; text-align: center; color: #050a14; margin-bottom: 20px; box-shadow: 0 0 25px rgba(56, 239, 125, 0.4); border: 2px solid #fff; animation: pulse-green 2s infinite; }
    .vip-price { font-size: 35px; font-weight: 900; text-shadow: 0 0 5px rgba(0,0,0,0.3); }
    @keyframes pulse-green { 0% { transform: scale(1); } 50% { transform: scale(1.01); } 100% { transform: scale(1); } }
    .trial-counter { position: fixed; top: 15px; right: 20px; background: rgba(0,0,0,0.8); border: 2px solid #ff9900; color: #ff9900; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 14px; z-index: 10000; animation: blink 2s infinite; }
    @keyframes blink { 50% { border-color: red; color: red; } }
    .hero-container { padding: 40px; background: rgba(0,0,0,0.4); border-radius: 20px; border: 1px solid #00fff9; margin-bottom: 20px; }
    .hero-title { font-size: 40px; font-weight: 900; background: -webkit-linear-gradient(#00fff9, #ff00ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
    .feature-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #ff00ff; margin-bottom: 10px; }
    .feature-title { color: #00fff9; font-weight: bold; font-size: 16px; margin-bottom: 5px;}
    .login-container { background: rgba(0,0,0,0.8); padding: 30px; border-radius: 20px; border: 2px solid #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.3); }
    .top-list-box { background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; border-top: 3px solid #00fff9; margin-bottom: 5px; }
    .list-item { font-size: 13px; border-bottom: 1px solid #333; padding: 3px 0; display: flex; justify-content: space-between; }
    .pos { color: #38ef7d; } .neg { color: #ef473a; } .spek { color: #ff00ff; }
    .neon-title { font-size: 60px !important; font-weight: 900; color: #fff; text-align: center; text-shadow: 0 0 10px #00fff9, 0 0 40px #00fff9, 0 0 80px #ff00ff; }
    .wallet-box { background: rgba(0,0,0,0.6); border: 2px solid #00fff9; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 255, 249, 0.2); }
    .wallet-addr { font-family: monospace; font-size: 20px; color: #ff00ff; font-weight: bold; word-break: break-all; background: #000; padding: 10px; border-radius: 5px; border: 1px dashed #ff00ff; }
    div.stButton > button { background: linear-gradient(90deg, #00fff9, #ff00ff) !important; color: #000 !important; border: none !important; font-weight: 800 !important; }
    
    /* AI Box */
    .ai-box { background: rgba(0, 255, 249, 0.05); border: 1px solid #00fff9; padding: 15px; border-radius: 10px; margin-top: 10px; }
    .ai-title { color: #00fff9; font-weight: bold; display: flex; align-items: center; gap: 5px; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

def get_live_rates():
    try:
        data = yf.download(["TRY=X", "EURTRY=X", "GC=F", "SI=F", "BZ=F", "BTC-USD", "ETH-USD"], period="1d", progress=False)['Close'].iloc[-1]
        usd = data['TRY=X']; eur = data['EURTRY=X']
        return usd, eur, (data['GC=F']*usd)/31.1035, (data['SI=F']*usd)/31.1035, data['BZ=F'], data['BTC-USD'], data['ETH-USD']
    except: return 0,0,0,0,0,0,0

@st.cache_data(ttl=1800)
def get_market_analysis():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS", "REEDR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "HDFGS.IS", "ISCTR.IS", "YKBNK.IS", "PETKM.IS", "KOZAL.IS", "KRDMD.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "TTKOM.IS", "TCELL.IS", "SOKM.IS", "MGROS.IS", "ALFAS.IS", "CANTE.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
    w, m = [], []
    for s in candidates:
        try:
            df = yf.download(s, period="1mo", interval="1d", progress=False)
            if len(df) > 20:
                son = df['Close'].iloc[-1]; w_ch = ((son - df['Close'].iloc[-5])/df['Close'].iloc[-5])*100
                m_ch = ((son - df['Close'].iloc[0])/df['Close'].iloc[0])*100
                vol = ((df['High'].iloc[-1]-df['Low'].iloc[-1])/df['Open'].iloc[-1])*100
                w.append({"Sembol": s.replace(".IS",""), "Degisim": w_ch, "Fiyat": son, "Volatilite": vol})
                m.append({"Sembol": s.replace(".IS",""), "Degisim": m_ch, "Fiyat": son})
        except: pass
    return sorted(w, key=lambda x:x['Degisim'], reverse=True)[:5], sorted(m, key=lambda x:x['Degisim'], reverse=True)[:5], sorted(w, key=lambda x:x['Degisim'])[:5], sorted(w, key=lambda x:x['Volatilite'], reverse=True)[:5]

def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain/loss)))
            rsi_val = rsi.iloc[-1]
            pivot = (df.iloc[-2]['High'] + df.iloc[-2]['Low'] + df.iloc[-2]['Close']) / 3
            
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.add_hline(y=pivot, line_dash="dot", line_color="#00fff9", annotation_text="PIVOT")
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title=f"{symbol} ANALİZİ", height=500)
            
            # --- GAUGE (İBRE) ---
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = rsi_val,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "GÜÇ GÖSTERGESİ (RSI)", 'font': {'size': 18, 'color': "#00fff9"}},
                delta = {'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                gauge = {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#00fff9"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 30], 'color': 'rgba(0, 255, 0, 0.3)'}, # AL
                        {'range': [30, 70], 'color': 'rgba(255, 255, 0, 0.3)'}, # NÖTR
                        {'range': [70, 100], 'color': 'rgba(255, 0, 0, 0.3)'}], # SAT
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': rsi_val}}))
            fig_gauge.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=300)

            # --- AI YORUM OLUŞTURMA ---
            ai_text = f"**🤖 PALA YAPAY ZEKA YORUMU:**\n\n"
            ai_text += f"Hissenin güncel fiyatı **{df.iloc[-1]['Close']:.2f}** seviyesinde. "
            if rsi_val < 30: ai_text += "RSI göstergesi **Aşırı Satım** bölgesinde (Ucuz). Bu, balinaların alım için fırsat kolladığı bir bölge olabilir. 🟢 "
            elif rsi_val > 70: ai_text += "RSI göstergesi **Aşırı Alım** bölgesinde (Pahalı). Kâr satışları gelebilir, dikkatli ol Kaptan! 🔴 "
            else: ai_text += "Piyasa şu an kararsız (Nötr). Trendin yönünü belirlemek için Pivot seviyesine dikkat et. 🟡 "
            if df.iloc[-1]['Close'] > pivot: ai_text += f"\n\nFiyat, Pivot seviyesinin ({pivot:.2f}) **üzerinde**, bu pozitif bir işaret."
            else: ai_text += f"\n\nFiyat, Pivot seviyesinin ({pivot:.2f}) **altında**, baskı devam edebilir."

            return fig, df.iloc[-1]['Close'], pivot, (2*pivot)-df.iloc[-2]['Low'], rsi_val, fig_gauge, ai_text
    except: return None, None, None, None, None, None, None

def admin_dashboard():
    st.sidebar.title("👑 YÖNETİM"); menu = st.sidebar.radio("Menü:", ["Üyeler", "Bildirimler", "Duyuru Yap"]); db = load_db()
    if menu == "Üyeler":
        for k, v in db.items():
            if k != "admin":
                with st.expander(f"{v.get('isim')} ({k}) - {'✅' if v.get('onay') else '⏳'}"):
                    c1, c2 = st.columns(2)
                    if c1.button("ONAYLA", key=f"a_{k}"): db[k]['onay']=True; save_db(db); st.rerun()
                    if c2.button("SİL", key=f"d_{k}"): del db[k]; save_db(db); st.rerun()
    elif menu == "Duyuru Yap":
        duyuru = st.text_input("Tüm Üyelere Mesaj:"); 
        if st.button("YAYINLA") and duyuru: db["admin"]["duyuru"] = duyuru; save_db(db); st.success("Yayında!")

def ana_uygulama(kalan_sure_dk=None):
    db = load_db(); user = st.session_state.login_user; usd, eur, gram_altin, gram_gumus, petrol, btc, eth = get_live_rates()
    if user not in db: st.session_state.login_user = None; st.rerun()
    
    if kalan_sure_dk is not None:
        dk = int(kalan_sure_dk); sn = int((kalan_sure_dk - dk) * 60)
        st.markdown(f"""<div class="trial-counter">⏳ DENEME: {dk:02d}:{sn:02d}</div>""", unsafe_allow_html=True)

    # --- PATRON DUYURUSU ---
    if db["admin"].get("duyuru"):
        st.error(f"🚨 PATRONDAN ACİL MESAJ: {db['admin']['duyuru']}")

    st.markdown(f"""<div style="background:#050a14; border-bottom:2px solid #00fff9; padding:5px;">💵 USD: {usd:.2f} ⏐ 🟡 GR ALTIN: {gram_altin:.0f} ⏐ ₿ BTC: ${btc:,.0f}</div>""", unsafe_allow_html=True)
    
    # VIP TEKLİF
    if not db[user].get('onay') and not db[user].get('rol') == 'admin':
        st.markdown(f"""<div class="vip-offer-box"><div class="vip-text">🔥 VIP FIRSAT 🔥</div><div class="vip-price">$500 / AY</div></div>""", unsafe_allow_html=True)
        if st.button("💎 SATIN AL", use_container_width=True): st.session_state.odeme_modu = not st.session_state.odeme_modu
        if st.session_state.odeme_modu:
            st.info(f"TRC20: {USDT_ADDRESS}"); tx = st.text_input("TXID"); 
            if st.button("BİLDİR") and tx: 
                if "mesajlar" not in db[user]: db[user]["mesajlar"] = []
                db[user]["mesajlar"].append(f"ÖDEME: {tx}"); save_db(db); st.success("İletildi!")

    st.markdown("---")
    # TARAMA & ANALİZ
    wg, mg, wl, sp = get_market_analysis()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🟢 HAFTALIK KRALLAR</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=pos>%{i["Degisim"]:.1f}</span></div>' for i in wg])}</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🗓️ AYLIK ROKETLER</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=pos>%{i["Degisim"]:.1f}</span></div>' for i in mg])}</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='top-list-box' style='border-color:#ef473a;'><div class='list-title'>🔴 HAFTALIK KAYIPLAR</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=neg>%{i["Degisim"]:.1f}</span></div>' for i in wl])}</div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='top-list-box' style='border-color:#ff00ff;'><div class='list-title'>🎰 SPEK / VOLATİL</div>{''.join([f'<div class=list-item><span>{i["Sembol"]}</span><span class=spek>⚡ {i["Volatilite"]:.1f}</span></div>' for i in sp])}</div>", unsafe_allow_html=True)

    st.markdown("---")
    hisse = st.selectbox("Hisse Analiz Et:", BIST_HISSELERI)
    if st.button("ANALİZ ET 🚀"): st.session_state.secilen_hisse = f"{hisse}.IS" if "USD" not in hisse else hisse; st.rerun()
    
    if st.session_state.secilen_hisse:
        fig, price, pivot, res, rsi, fig_gauge, ai_comment = grafik_ciz(st.session_state.secilen_hisse)
        if fig:
            c_g1, c_g2 = st.columns([2, 1])
            with c_g1: st.plotly_chart(fig, use_container_width=True)
            with c_g2: 
                st.plotly_chart(fig_gauge, use_container_width=True)
                st.markdown(f"<div class='ai-box'>{ai_comment}</div>", unsafe_allow_html=True)
        else: st.error("Veri Yok.")
        if st.button("Kapat"): st.session_state.secilen_hisse=None; st.rerun()

def payment_screen():
    st.warning("SÜRE DOLDU! LÜTFEN ÖDEME YAPIN."); st.code(USDT_ADDRESS); 
    if st.button("ÇIKIŞ"): st.session_state.login_user=None; st.rerun()

def login_page():
    st.markdown("""<div style="text-align:center; padding:20px;"><h1 class="neon-title">PALA BALİNA AVCISI</h1></div>""", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])
    with c1: st.markdown("""<div class="hero-container"><div class="hero-title">DERİN SULARIN HAKİMİ OL.</div><div style="margin-top:20px; text-align:center;"><img src="https://images.unsplash.com/photo-1560275619-4662e36fa65c?q=80&w=2070&auto=format&fit=crop" style="width:100%; border-radius:10px; border:1px solid #00fff9;"></div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["GİRİŞ", "10DK DENE"])
        with t1:
            u = st.text_input("Kullanıcı", key="lu"); p = st.text_input("Şifre", type="password", key="lp")
            if st.button("GİRİŞ YAP"):
                db=load_db(); 
                if u in db and db[u]['sifre']==p: st.session_state.login_user=u; st.rerun()
        with t2:
            ru = st.text_input("Yeni Nick"); rp = st.text_input("Şifre", type="password", key="rp"); rn = st.text_input("İsim")
            if st.button("KAYIT OL"):
                db=load_db(); db[ru]={"sifre":rp, "isim":rn, "onay":False, "rol":"user", "mesajlar":[], "kayit_tarihi":time.time()}; save_db(db); st.session_state.login_user=ru; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.login_user: login_page()
else:
    u = st.session_state.login_user; db = load_db()
    if u in db:
        if db[u].get('rol') == 'admin' or db[u].get('onay'): ana_uygulama()
        else:
            if (time.time() - db[u].get('kayit_tarihi', 0))/60 < DENEME_SURESI_DK: ana_uygulama(DENEME_SURESI_DK - (time.time() - db[u].get('kayit_tarihi', 0))/60)
            else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
