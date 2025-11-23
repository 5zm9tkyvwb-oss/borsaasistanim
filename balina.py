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
# 💰 AYARLAR
# ==========================================
USDT_ADDRESS = "TV4DK7vckLWJciKSqhvY5hEpcw1Ka522AQ"
DENEME_SURESI_DK = 10 

# ==========================================
# 📜 BIST HİSSE LİSTESİ
# ==========================================
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
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, json=payload)
        except: pass

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
                "portfoy": [],
                "kayit_tarihi": time.time()
            }
        }
        save_db(default_db)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session State
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None
if 'odeme_modu' not in st.session_state: st.session_state.odeme_modu = False # Ödeme modalı için

# --- TASARIM (NEON CYBERPUNK) ---
st.markdown("""
    <style>
    /* --- GENEL --- */
    .stApp { 
        background-color: #050a14 !important;
        background-image: radial-gradient(rgba(0, 255, 249, 0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        color: #e6e6e6 !important; 
        font-family: 'Orbitron', sans-serif; 
    }
    
    /* --- VIP TEKLİF KUTUSU --- */
    .vip-offer-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: #050a14;
        margin-bottom: 20px;
        box-shadow: 0 0 25px rgba(56, 239, 125, 0.4);
        border: 2px solid #fff;
        animation: pulse-green 2s infinite;
    }
    .vip-price { font-size: 35px; font-weight: 900; text-shadow: 0 0 5px rgba(0,0,0,0.3); }
    .vip-text { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
    @keyframes pulse-green { 0% { transform: scale(1); } 50% { transform: scale(1.01); box-shadow: 0 0 35px rgba(56, 239, 125, 0.7); } 100% { transform: scale(1); } }

    /* --- DENEME SÜRESİ SAYACI --- */
    .trial-counter {
        position: fixed; top: 15px; right: 20px;
        background: rgba(0,0,0,0.8);
        border: 2px solid #ff9900;
        color: #ff9900;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        z-index: 10000;
        box-shadow: 0 0 15px rgba(255, 153, 0, 0.5);
        animation: blink 2s infinite;
    }
    @keyframes blink { 50% { border-color: red; color: red; } }

    /* --- REKLAM / LANDING PAGE CSS --- */
    .hero-container {
        padding: 40px;
        background: rgba(0,0,0,0.4);
        border-radius: 20px;
        border: 1px solid #00fff9;
        margin-bottom: 20px;
    }
    .hero-title {
        font-size: 40px;
        font-weight: 900;
        background: -webkit-linear-gradient(#00fff9, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .hero-subtitle { font-size: 18px; color: #e0e0e0; margin-bottom: 20px; line-height: 1.5; }
    .feature-box { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border-left: 4px solid #ff00ff; margin-bottom: 10px; }
    .feature-title { color: #00fff9; font-weight: bold; font-size: 16px; margin-bottom: 5px;}
    .feature-desc { color: #aaa; font-size: 14px; }
    .login-container { background: rgba(0,0,0,0.8); padding: 30px; border-radius: 20px; border: 2px solid #ff00ff; box-shadow: 0 0 30px rgba(255, 0, 255, 0.3); }

    /* --- DİĞER CSS --- */
    .top-list-box { background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; border-top: 3px solid #00fff9; margin-bottom: 5px; }
    .list-title { color: #00fff9; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; font-size: 14px; }
    .list-item { font-size: 13px; border-bottom: 1px solid #333; padding: 3px 0; display: flex; justify-content: space-between; }
    .pos { color: #38ef7d; } .neg { color: #ef473a; } .spek { color: #ff00ff; }
    .neon-title { font-size: 60px !important; font-weight: 900; color: #fff; text-align: center; text-shadow: 0 0 10px #00fff9, 0 0 40px #00fff9, 0 0 80px #ff00ff; }
    .wallet-box { background: rgba(0,0,0,0.6); border: 2px solid #00fff9; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 255, 249, 0.2); }
    .wallet-addr { font-family: monospace; font-size: 20px; color: #ff00ff; font-weight: bold; word-break: break-all; background: #000; padding: 10px; border-radius: 5px; border: 1px dashed #ff00ff; }
    div.stButton > button { background: linear-gradient(90deg, #00fff9, #ff00ff) !important; color: #000 !important; border: none !important; font-weight: 800 !important; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- CANLI VERİ MOTORU ---
def get_live_rates():
    try:
        tickers = ["TRY=X", "EURTRY=X", "GC=F", "SI=F", "BZ=F", "BTC-USD", "ETH-USD"]
        data = yf.download(tickers, period="1d", progress=False)['Close'].iloc[-1]
        usd = data['TRY=X']; eur = data['EURTRY=X']
        gram_altin = (data['GC=F'] * usd) / 31.1035
        gram_gumus = (data['SI=F'] * usd) / 31.1035
        petrol = data['BZ=F']; btc = data['BTC-USD']; eth = data['ETH-USD']
        return usd, eur, gram_altin, gram_gumus, petrol, btc, eth
    except: return 0, 0, 0, 0, 0, 0, 0

# --- YARDIMCI FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
        db["admin"]["loglar"] = db["admin"]["loglar"][:50]
        save_db(db)
    except: pass

@st.cache_data(ttl=1800)
def get_market_analysis():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS", "REEDR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "HDFGS.IS", "ISCTR.IS", "YKBNK.IS", "PETKM.IS", "KOZAL.IS", "KRDMD.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "TTKOM.IS", "TCELL.IS", "SOKM.IS", "MGROS.IS", "ALFAS.IS", "CANTE.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
    weekly_data = []
    monthly_data = []
    for s in candidates:
        try:
            df = yf.download(s, period="1mo", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if len(df) > 20:
                son = df['Close'].iloc[-1]
                w_change = ((son - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
                m_change = ((son - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                volatility = ((df['High'].iloc[-1] - df['Low'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                sym = s.replace(".IS","")
                weekly_data.append({"Sembol": sym, "Degisim": w_change, "Fiyat": son, "Volatilite": volatility})
                monthly_data.append({"Sembol": sym, "Degisim": m_change, "Fiyat": son})
        except: pass
    w_gainers = sorted(weekly_data, key=lambda x: x['Degisim'], reverse=True)[:5]
    w_losers = sorted(weekly_data, key=lambda x: x['Degisim'])[:5]
    m_gainers = sorted(monthly_data, key=lambda x: x['Degisim'], reverse=True)[:5]
    spek_list = sorted(weekly_data, key=lambda x: x['Volatilite'], reverse=True)[:5]
    return w_gainers, m_gainers, w_losers, spek_list

def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        if not df.empty:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain/loss)))
            pivot = (df.iloc[-2]['High'] + df.iloc[-2]['Low'] + df.iloc[-2]['Close']) / 3
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.add_hline(y=pivot, line_dash="dot", line_color="#00fff9", annotation_text="PIVOT")
            fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', title=f"{symbol} ANALİZİ")
            return fig, df.iloc[-1]['Close'], pivot, (2*pivot)-df.iloc[-2]['Low'], rsi.iloc[-1]
    except: return None, None, None, None, None

# ==========================================
# 👑 ADMIN PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 YÖNETİM")
    menu = st.sidebar.radio("Menü:", ["Üye Yönetimi", "Bildirimler", "Manuel Ekle"])
    db = load_db()
    if menu == "Üye Yönetimi":
        st.subheader("👥 KULLANICI LİSTESİ")
        for k, v in db.items():
            if k != "admin":
                reg_time = v.get('kayit_tarihi', 0); gecen_sure = (time.time() - reg_time) / 60; kalan_sure = DENEME_SURESI_DK - gecen_sure
                durum_ikon = "🔴 BİTTİ"
                if v.get('onay'): durum_ikon = "✅ PREMİUM"
                elif kalan_sure > 0: durum_ikon = f"⏳ DENEME ({int(kalan_sure)} dk)"
                with st.expander(f"👤 {v.get('isim')} ({k}) - {durum_ikon}"):
                    c1, c2, c3 = st.columns(3)
                    if not v.get('onay'):
                        if c1.button(f"ONAYLA", key=f"app_{k}"): db[k]['onay'] = True; save_db(db); st.rerun()
                    else:
                        if c1.button(f"İPTAL", key=f"ban_{k}"): db[k]['onay'] = False; save_db(db); st.rerun()
                    if c2.button(f"SİL", key=f"del_{k}"): del db[k]; save_db(db); st.rerun()
                    if c3.button(f"SIFIRLA", key=f"rst_{k}"): db[k]['kayit_tarihi'] = time.time(); db[k]['onay'] = False; save_db(db); st.success("Sıfırlandı!"); st.rerun()
    elif menu == "Bildirimler":
        st.subheader("📩 BİLDİRİMLER")
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                with st.expander(f"✉️ {k} ({len(v['mesajlar'])})"):
                    for m in v['mesajlar']: st.info(m)
                    if st.button(f"Temizle {k}", key=f"clr_{k}"): db[k]['mesajlar'] = []; save_db(db); st.rerun()
    elif menu == "Manuel Ekle":
        u = st.text_input("Nick"); p = st.text_input("Şifre"); n = st.text_input("İsim")
        if st.button("Ekle") and u and p: db[u] = {"sifre": p, "isim": n, "onay": True, "rol": "user", "mesajlar": [], "portfoy": [], "kayit_tarihi": time.time()}; save_db(db); st.success("Eklendi.")

# ==========================================
# 💰 ÖDEME EKRANI (Deneme Bittiğinde)
# ==========================================
def payment_screen():
    u = st.session_state.login_user; db = load_db()
    st.markdown("""<div style="text-align:center; padding-top:20px;"><h1 style="color:#ff00ff;">⛔ DENEME SÜRESİ DOLDU ⛔</h1><p style="font-size:18px;">10 Dakikalık VIP kullanım hakkınız bitti.</p><p>Devam etmek için Premium Üyelik satın almalısınız.</p></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="wallet-box"><h3 style="color:#00fff9;">💎 USDT (TRC20) CÜZDAN</h3><div class="wallet-addr">{USDT_ADDRESS}</div></div>""", unsafe_allow_html=True)
    st.subheader("📩 Ödeme Bildirimi")
    col1, col2 = st.columns([3, 1])
    with col1: tx_msg = st.text_area("Açıklama / TXID")
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("GÖNDER 🚀"):
            if tx_msg:
                if "mesajlar" not in db[u]: db[u]["mesajlar"] = []
                db[u]["mesajlar"].append(f"[{datetime.now().strftime('%d/%m %H:%M')}] {tx_msg}")
                save_db(db); st.success("İletildi."); send_telegram(f"💰 ÖDEME: {u}")
    if st.button("ÇIKIŞ YAP 🔙"): st.session_state.login_user = None; st.rerun()

# ==========================================
# 💎 VIP UPSELL (Deneme Süresindeki Üye İçin Fırsat Kutusu)
# ==========================================
def render_vip_offer(user, db):
    # Sadece deneme süresindeki (Onaysız ve Admin olmayan) kullanıcıya göster
    if not db[user].get('onay') and not db[user].get('rol') == 'admin':
        st.markdown(f"""
        <div class="vip-offer-box">
            <div class="vip-text">🔥 FIRSATI KAÇIRMA! VIP AYRICALIKLARA ŞİMDİ SAHİP OL 🔥</div>
            <div class="vip-price">AYLIK $500</div>
            <p style="margin-top:10px; font-size:14px;">Süre dolmadan yükselt, kesintisiz analize devam et.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Satın Al Butonu
        if st.button("💎 HEMEN SATIN AL VE YÜKSELT", type="primary", use_container_width=True):
            st.session_state.odeme_modu = not st.session_state.odeme_modu
        
        # Ödeme Alanı (Butona basınca açılır)
        if st.session_state.odeme_modu:
            with st.container():
                st.markdown(f"""<div class="wallet-box" style="margin-top:10px;"><h4 style="color:#00fff9;">USDT (TRC20) ADRESİNİZ</h4><div class="wallet-addr" style="font-size:16px;">{USDT_ADDRESS}</div></div>""", unsafe_allow_html=True)
                tx_input = st.text_input("Ödeme TXID Kodu:", placeholder="İşlem kodunu buraya yapıştır...")
                if st.button("ÖDEMEYİ BİLDİR ✅"):
                    if tx_input:
                        if "mesajlar" not in db[user]: db[user]["mesajlar"] = []
                        db[user]["mesajlar"].append(f"[{datetime.now().strftime('%H:%M')}] 💰 ERKEN ÖDEME: {tx_input}")
                        save_db(db)
                        st.success("Bildirim iletildi! Yöneticiler kontrol ediyor.")
                        send_telegram(f"💰 SİSTEM İÇİNDEN SATIŞ GELDİ! Üye: {user}, TXID: {tx_input}")
                        st.session_state.odeme_modu = False
                    else:
                        st.error("Lütfen TXID giriniz.")
        st.markdown("---")

# ==========================================
# 📈 ANA UYGULAMA
# ==========================================
def ana_uygulama(kalan_sure_dk=None):
    db = load_db(); user = st.session_state.login_user
    if user not in db: st.session_state.login_user = None; time.sleep(1); st.rerun()

    if kalan_sure_dk is not None:
        dk = int(kalan_sure_dk); sn = int((kalan_sure_dk - dk) * 60)
        st.markdown(f"""<div class="trial-counter">⏳ DENEME: {dk:02d}:{sn:02d}</div>""", unsafe_allow_html=True)
        st.toast(f"Deneme Sürümü Aktif! Kalan Süre: {dk} Dakika", icon="⏳")

    usd, eur, gram_altin, gram_gumus, petrol, btc, eth = get_live_rates()

    st.markdown(f"""
    <div style="background:#050a14; border-bottom:2px solid #00fff9; padding:5px; margin-bottom:20px;">
        <div style="animation:marquee 30s linear infinite; color:#00fff9; font-weight:800; white-space:nowrap;">
            💵 USD: {usd:.2f} ⏐ 💶 EUR: {eur:.2f} ⏐ 🟡 GR ALTIN: {gram_altin:.0f} TL ⏐ ⚪ GR GÜMÜŞ: {gram_gumus:.2f} TL ⏐ ⛽ BRENT: ${petrol:.1f} ⏐ ₿ BTC: ${btc:,.0f} ⏐ 🔷 ETH: ${eth:,.0f} ⏐ 🦈 PALA BALİNA AVCISI
        </div>
    </div><style>@keyframes marquee {{ 0% {{transform:translateX(0);}} 100% {{transform:translateX(-100%);}} }}</style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([8, 2])
    c1.markdown(f"<h1 style='color:#00fff9;'>🦈 PALA BALİNA AVCISI</h1>", unsafe_allow_html=True)
    c1.markdown(f"Kaptan: **{db[user].get('isim')}**")
    if c2.button("GÜVENLİ ÇIKIŞ"): st.session_state.login_user=None; st.rerun()
    if db[user].get('rol') == 'admin': admin_dashboard()
    
    # --- VIP FIRSAT KUTUSU ---
    render_vip_offer(user, db)
    
    # 4'LÜ PİYASA TARAMA
    w_gain, m_gain, w_lose, spek = get_market_analysis()
    col_w, col_m, col_l, col_s = st.columns(4)
    with col_w:
        st.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🟢 HAFTALIK KRALLAR</div>", unsafe_allow_html=True)
        for i in w_gain: st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='pos'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_m:
        st.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🗓️ AYLIK ROKETLER</div>", unsafe_allow_html=True)
        for i in m_gain: st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='pos'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_l:
        st.markdown(f"<div class='top-list-box' style='border-color:#ef473a;'><div class='list-title'>🔴 HAFTALIK KAYIPLAR</div>", unsafe_allow_html=True)
        for i in w_lose: st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='neg'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_s:
        st.markdown(f"<div class='top-list-box' style='border-color:#ff00ff;'><div class='list-title'>🎰 SPEK / VOLATİL</div>", unsafe_allow_html=True)
        for i in spek: st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='spek'>⚡ {i['Volatilite']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    sc, sb = st.columns([3, 1])
    hisse = sc.selectbox("Hisse Seç:", BIST_HISSELERI)
    if sb.button("ANALİZ ET 🚀"): st.session_state.secilen_hisse = f"{hisse}.IS" if "USD" not in hisse else hisse; st.rerun()
    
    if st.session_state.secilen_hisse:
        fig, price, pivot, res, rsi = grafik_ciz(st.session_state.secilen_hisse)
        if fig:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("FİYAT", f"{price:.2f}")
            m2.metric("RSI", f"{rsi:.1f}", delta="AL" if rsi<30 else "SAT" if rsi>70 else "NÖTR")
            m3.metric("PİVOT", f"{pivot:.2f}")
            m4.metric("DİRENÇ", f"{res:.2f}")
            st.plotly_chart(fig, use_container_width=True)
        else: st.error("Veri yok.")
        if st.button("Kapat"): st.session_state.secilen_hisse=None; st.rerun()

# ==========================================
# 🔐 YENİ GİRİŞ EKRANI (Landing Page)
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center; padding:20px;"><h1 class="neon-title">PALA BALİNA AVCISI</h1></div>""", unsafe_allow_html=True)
    col_info, col_login = st.columns([3, 2])
    with col_info:
        st.markdown("""<div class="hero-container"><div class="hero-title">DERİN SULARIN HAKİMİ OL.</div><div class="hero-subtitle">Borsa İstanbul ve Kripto dünyasında kaybolma. Profesyonel balina avcılarının kullandığı terminale hoş geldin.</div><div class="feature-box"><div class="feature-title">🚀 CANLI SİNYAL YAKALAYICI</div><div class="feature-desc">Hangi hisseye balina girdi? RSI, Pivot ve Hacim patlamalarını saniyesinde gör.</div></div><div class="feature-box"><div class="feature-title">🧠 OTOMATİK TEKNİK ANALİZ</div><div class="feature-desc">Destek, Direnç, Pivot noktaları ve Trend analizleri tek tıkla ekranında.</div></div><div class="feature-box"><div class="feature-title">🛡️ VIP KULÜP AYRICALIĞI</div><div class="feature-desc">Sadece seçkin üyeler için özel veriler ve 7/24 piyasa takibi.</div></div><div style="margin-top:20px; text-align:center;"><img src="https://images.unsplash.com/photo-1560275619-4662e36fa65c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" style="width:100%; border-radius:10px; border:1px solid #00fff9; opacity:0.8; box-shadow: 0 0 20px rgba(0, 255, 249, 0.3);"></div></div>""", unsafe_allow_html=True)
    with col_login:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 GİRİŞ YAP", "📝 10 DK ÜCRETSİZ DENE"])
        with tab1:
            k = st.text_input("Kullanıcı Adı", key="l_u"); s = st.text_input("Şifre", type="password", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("TERMİNALE BAĞLAN ⚡", type="primary", use_container_width=True):
                db = load_db()
                if k in db and db[k]['sifre'] == s: st.session_state.login_user = k; st.rerun()
                else: st.error("Hatalı Giriş!")
        with tab2:
            st.markdown("##### Hızlı Kayıt Ol & Başla")
            u = st.text_input("Kullanıcı Adı Belirle", key="r_u"); n = st.text_input("Adın Soyadın", key="r_n"); p = st.text_input("Şifre Belirle", type="password", key="r_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("KAYDI TAMAMLA VE BAŞLA 🚀", type="primary", use_container_width=True):
                db = load_db()
                if u in db: st.warning("Bu isim alınmış!")
                elif u and p:
                    db[u] = {"sifre": p, "isim": n, "onay": False, "rol": "user", "mesajlar": [], "portfoy": [], "kayit_tarihi": time.time()}
                    save_db(db); st.success("Kayıt Başarılı!"); send_telegram(f"🆕 ÜYE: {u}")
        st.markdown("</div>", unsafe_allow_html=True)
    if st.checkbox("Admin Reset"):
        if st.button("Reset"): st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": [], "kayit_tarihi": time.time()}}; save_db(st.session_state.db); st.success("Resetlendi.")

# --- YETKİLENDİRME ---
if not st.session_state.login_user:
    login_page()
else:
    u_id = st.session_state.login_user; db = load_db()
    if u_id in db:
        user_data = db[u_id]
        if user_data.get('rol') == 'admin': ana_uygulama()
        elif user_data.get('onay') == True: ana_uygulama()
        else:
            kayit_zamani = user_data.get('kayit_tarihi', 0); gecen_sure_dk = (time.time() - kayit_zamani) / 60
            if gecen_sure_dk < DENEME_SURESI_DK:
                kalan = DENEME_SURESI_DK - gecen_sure_dk
                ana_uygulama(kalan_sure_dk=kalan)
            else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
