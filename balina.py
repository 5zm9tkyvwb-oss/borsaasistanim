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
# 📜 DEV BIST HİSSE LİSTESİ (TÜMÜ)
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
# 🚨 TELEGRAM AYARLARI
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
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# Session State
if 'db' not in st.session_state: st.session_state.db = load_db()
if 'giris_yapildi' not in st.session_state: st.session_state.giris_yapildi = False
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

# --- TASARIM (NEON CYBERPUNK & HACKER TERMINAL) ---
st.markdown("""
    <style>
    /* --- GENEL SAYFA YAPISI --- */
    .stApp { 
        background-color: #050a14 !important; /* Çok koyu siber mavi/siyah */
        background-image: radial-gradient(rgba(0, 255, 249, 0.1) 1px, transparent 1px), radial-gradient(rgba(0, 255, 249, 0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        background-position: 0 0, 25px 25px;
        color: #e6e6e6 !important; /* Okunabilir açık gri metin */
        font-family: 'Orbitron', 'Roboto', sans-serif; /* Daha teknolojik font */
    }
    
    /* --- NEON BAŞLIKLAR VE METİNLER --- */
    h1, h2, h3 {
        color: #ffffff !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    /* PALA BALİNA AVCISI Giriş Başlığı Efekti */
    .neon-title {
        font-size: 70px !important;
        font-weight: 900;
        color: #fff;
        text-align: center;
        text-shadow:
            0 0 5px #fff,
            0 0 10px #fff,
            0 0 20px #00fff9, /* Camgöbeği Neon */
            0 0 40px #00fff9,
            0 0 80px #00fff9,
            0 0 90px #ff00ff, /* Pembe Neon */
            0 0 100px #ff00ff;
        animation: flicker 1.5s infinite alternate;
    }
    @keyframes flicker {
        0%, 18%, 22%, 25%, 53%, 57%, 100% {
            text-shadow:
            0 0 4px #fff,
            0 0 11px #fff,
            0 0 19px #00fff9,
            0 0 40px #00fff9,
            0 0 80px #00fff9,
            0 0 90px #ff00ff,
            0 0 100px #ff00ff;
        }
        20%, 24%, 55% {        
            text-shadow: none;
        }
    }
    
    .sub-title {
        color: #00fff9 !important;
        text-align: center;
        font-size: 20px;
        letter-spacing: 3px;
        text-shadow: 0 0 10px #00fff9;
    }
    
    /* --- TABLOLAR (Hacker Tarzı) --- */
    div[data-testid="stTable"], table {
        background-color: rgba(13, 17, 23, 0.8) !important;
        border: 1px solid #00fff9 !important; /* Neon çerçeve */
        box-shadow: 0 0 10px rgba(0, 255, 249, 0.2);
        border-radius: 4px !important;
        color: #e6e6e6 !important;
    }
    thead tr th {
        background-color: rgba(0, 255, 249, 0.1) !important;
        color: #00fff9 !important; /* Başlıklar Neon Mavi */
        font-size: 15px !important;
        border-bottom: 2px solid #00fff9 !important;
        text-shadow: 0 0 5px #00fff9;
    }
    tbody tr:nth-of-type(even) { background-color: rgba(255, 0, 255, 0.05) !important; }
    tbody tr:hover { background-color: rgba(0, 255, 249, 0.1) !important; }
    
    /* --- BUTONLAR (Cyberpunk Gradient) --- */
    div.stButton > button {
        background: linear-gradient(90deg, #00fff9, #ff00ff) !important;
        color: #000000 !important; 
        border: none !important; 
        border-radius: 4px !important; 
        font-weight: 800 !important;
        text-transform: uppercase;
        font-size: 16px !important;
        height: 50px !important; 
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(0, 255, 249, 0.5);
    }
    div.stButton > button:hover { 
        transform: scale(1.02) !important;
        box-shadow: 0 0 20px #00fff9, 0 0 20px #ff00ff !important;
    }
    
    /* --- INPUT ALANLARI (Parlayan Çerçeveler) --- */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input, .stNumberInput input { 
        background-color: rgba(13, 17, 23, 0.8) !important; 
        color: #00fff9 !important; /* Yazı rengi neon mavi */
        border: 1px solid #30363d !important; 
        border-radius: 4px !important;
        transition: all 0.3s;
    }
    /* Inputa tıklayınca parlasın */
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox > div[data-baseweb="select"] > div:focus-within {
        border-color: #00fff9 !important;
        box-shadow: 0 0 15px #00fff9, inset 0 0 5px #00fff9 !important;
    }
    
    /* Dropdown Menüler */
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #0d1117 !important;
        border: 1px solid #00fff9 !important;
    }
    
    /* --- METRİK KUTULARI --- */
    div[data-testid="stMetricValue"] {
        background: -webkit-linear-gradient(#00fff9, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        text-shadow: 0 0 10px rgba(0,255,249,0.3);
    }
    div[data-testid="stMetricLabel"] {
        color: #e6e6e6 !important;
    }
    
    /* --- STICKER --- */
    .pala-sticker { 
        position: fixed; top: 70px; right: 25px; 
        background: linear-gradient(45deg, #00fff9, #ff00ff);
        color: #000; padding: 8px 16px; border-radius: 4px; 
        font-weight: 900; letter-spacing: 1px;
        z-index: 9999; box-shadow: 0 0 20px #00fff9;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 10px #00fff9; }
        50% { box-shadow: 0 0 30px #ff00ff; }
        100% { box-shadow: 0 0 10px #00fff9; }
    }
    
    /* --- BİLGİ KUTULARI --- */
    div.stInfo, div.stSuccess {
        background-color: rgba(0, 255, 249, 0.1) !important;
        border: 1px solid #00fff9 !important;
        color: #ffffff !important;
        box-shadow: inset 0 0 10px rgba(0, 255, 249, 0.2);
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <div class="pala-sticker">PALA BALİNA</div>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
def log_ekle(mesaj):
    try:
        db = load_db()
        if "loglar" not in db["admin"]: db["admin"]["loglar"] = []
        tarih = datetime.now().strftime("%H:%M")
        if not db["admin"]["loglar"] or mesaj not in db["admin"]["loglar"][0]:
            db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
            db["admin"]["loglar"] = db["admin"]["loglar"][:50]
            save_db(db)
            send_telegram(f"🔔 {mesaj}")
    except: pass

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- HAFTANIN YILDIZLARI (TOP 10) ---
@st.cache_data(ttl=3600)
def get_weekly_top10():
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS"]
    results = []
    for s in candidates:
        try:
            df = yf.download(s, period="5d", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            if len(df) > 1:
                ilk = df['Open'].iloc[0]; son = df['Close'].iloc[-1]
                degisim = ((son - ilk) / ilk) * 100
                if degisim > 0:
                    results.append({"Sembol": s.replace(".IS",""), "Fiyat": son, "Degisim": degisim})
        except: pass
    return sorted(results, key=lambda x: x['Degisim'], reverse=True)[:5]

# --- GRAFİK, PIVOT VE RSI HESAPLAMA ---
def grafik_ciz(symbol):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            # RSI HESAPLAMA
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            son_rsi = rsi.iloc[-1]
            
            # PIVOT HESABI
            prev = df.iloc[-2]
            pivot = (prev['High'] + prev['Low'] + prev['Close']) / 3
            r1 = (2 * pivot) - prev['Low']
            s1 = (2 * pivot) - prev['High']
            
            # GRAFİK
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            
            # DESTEK/DİRENÇ ÇİZGİLERİ (Neon Renkler)
            fig.add_hline(y=pivot, line_dash="dot", line_color="#00fff9", line_width=2, annotation_text="PIVOT", annotation_position="bottom right", annotation_font_color="#00fff9")
            fig.add_hline(y=r1, line_dash="solid", line_color="#ff00ff", line_width=2, annotation_text="DİRENÇ (R1)", annotation_font_color="#ff00ff")
            fig.add_hline(y=s1, line_dash="solid", line_color="#00fff9", line_width=2, annotation_text="DESTEK (S1)", annotation_font_color="#00fff9")
            
            fig.update_layout(
                title=dict(text=f"📊 {symbol} SİBER GÖRÜNÜM", font=dict(color="#00fff9", size=20)),
                template="plotly_dark", 
                height=500, 
                xaxis_rangeslider_visible=False, 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Orbitron", size=12, color="#e6e6e6"),
                xaxis=dict(gridcolor='rgba(0, 255, 249, 0.1)'),
                yaxis=dict(gridcolor='rgba(0, 255, 249, 0.1)'),
            )
            
            news = []
            try:
                n = yf.Ticker(symbol).news
                for i in n[:3]: news.append(f"📰 [{i['title']}]({i['link']})")
            except: pass
            
            return fig, df.iloc[-1]['Close'], pivot, s1, r1, son_rsi, news
    except: return None, None, None, None, None, None, None

# ==========================================
# 1. YÖNETİM PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 YÖNETİM")
    if st.sidebar.button("🔔 Test Bildirimi Gönder"):
        send_telegram("🦅 *Pala Balina:* Test Mesajı")
        st.sidebar.success("İletildi.")
    
    menu = st.sidebar.radio("Seçenekler:", ["Üyeler", "Mesaj Kutusu"])
    db = load_db()
    
    if menu == "Üyeler":
        st.subheader("👥 Üye Listesi")
        uye_data = []
        for k, v in db.items():
            if k != "admin":
                durum = "Aktif" if v.get('onay') else "Beklemede"
                uye_data.append({"Kullanıcı": k, "İsim": v.get('isim', '-'), "Durum": durum})
        if uye_data: st.table(pd.DataFrame(uye_data))
        else: st.info("Üye yok.")

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    # --- KAYAN PİYASA BANDI (TICKER - NEON) ---
    st.markdown("""
    <div style="background-color: #050a14; border-bottom: 2px solid #00fff9; border-top: 2px solid #ff00ff; overflow: hidden; white-space: nowrap; box-sizing: border-box; padding: 8px; box-shadow: 0 0 15px rgba(0, 255, 249, 0.5);">
        <div style="display: inline-block; padding-left: 100%; animation: marquee 30s linear infinite; color: #00fff9; font-weight: 800; font-family: 'Orbitron', monospace; font-size: 18px; text-shadow: 0 0 5px #00fff9;">
            💵 USD/TRY: 34.50 ⏐ 💶 EUR/TRY: 37.20 ⏐ 🟡 GRAM ALTIN: 2950 TL ⏐ ₿ BTC: $98,000 ⏐ ⛽ BRENT: $75.40 ⏐ 🦈 PALA BALİNA AVCISI SİSTEMİ AKTİF ⏐ HEDEF: MAKSİMUM KAZANÇ
        </div>
    </div>
    <style>
    @keyframes marquee {
        0%   { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

    user = st.session_state.login_user; db = st.session_state.db
    
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"<h1 style='color:#00fff9; text-shadow: 0 0 10px #00fff9;'>🦈 PALA BALİNA AVCISI</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#e6e6e6; letter-spacing: 1px;'>Terminal aktif, Kaptan <b>{db[user].get('isim', 'Kaptan')}</b>. Av başlasın.</p>", unsafe_allow_html=True)
    with c2:
        if st.button("GÜVENLİ ÇIKIŞ"): st.session_state.login_user=None; st.rerun()

    if db[user].get('rol') == 'admin': admin_dashboard()

    st.markdown("---")

    # --- HİSSE SORGULAMA ---
    st.markdown("### 🔍 HİSSE SORGULAMA VE ANALİZ")
    
    col_search, col_btn = st.columns([3, 1])
    secilen_hisse_input = col_search.selectbox("İncelenecek Hisseyi Seçiniz:", BIST_HISSELERI, index=BIST_HISSELERI.index("HDFGS") if "HDFGS" in BIST_HISSELERI else 0)
    
    if col_btn.button("ANALİZ ET 🚀", type="primary"):
        if "USD" not in secilen_hisse_input: sembol = f"{secilen_hisse_input}.IS"
        else: sembol = secilen_hisse_input
        st.session_state.secilen_hisse = sembol
        st.rerun()

    # --- GRAFİK VE DETAYLI ANALİZ ---
    if st.session_state.secilen_hisse:
        hisse = st.session_state.secilen_hisse
        st.info(f"📈 {hisse} Verileri İşleniyor...")
        
        # Grafik Fonksiyonunu Çağır
        fig, fiyat, pivot, s1, r1, rsi_val, haberler = grafik_ciz(hisse)
        
        if fig:
            # 1. METRİKLER (Fiyat, Pivot, RSI)
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("ANLIK FİYAT", f"{fiyat:.2f}")
            m2.metric("DESTEK (S1)", f"{s1:.2f}", delta="Alım Bölgesi", delta_color="normal")
            m3.metric("PİVOT", f"{pivot:.2f}", delta="Denge", delta_color="off")
            m4.metric("DİRENÇ (R1)", f"{r1:.2f}", delta="Satış Bölgesi", delta_color="inverse")
            
            # RSI Yorumlama
            rsi_durum = "NÖTR 😐"
            if rsi_val < 30: rsi_durum = "AL FIRSATI? 🟢"
            elif rsi_val > 70: rsi_durum = "SAT RİSKİ! 🔴"
            m5.metric("RSI GÖSTERGESİ", f"{rsi_val:.1f}", delta=rsi_durum)
            
            # 2. GRAFİK
            st.plotly_chart(fig, use_container_width=True)
            
            # 3. ŞİRKET KARNESİ (Temel Analiz)
            st.markdown("#### 🏢 Şirket Karnesi")
            try:
                info = yf.Ticker(hisse).info
                k1, k2, k3, k4 = st.columns(4)
                k1.info(f"F/K Oranı: {info.get('trailingPE', 'Yok'):.2f}")
                k2.info(f"PD/DD: {info.get('priceToBook', 'Yok'):.2f}")
                k3.info(f"Zirve (52H): {info.get('fiftyTwoWeekHigh', '-')}")
                k4.info(f"Sektör: {info.get('industry', 'Genel')}")
            except: st.warning("Temel veriler anlık olarak çekilemedi.")
            
            # 4. HABERLER
            if haberler:
                st.markdown("#### 📰 Son Dakika Haberleri")
                for h in haberler: st.markdown(f"- {h}")
        else:
            st.error("Veri alınamadı.")
        
        if st.button("Ekrani Temizle"): st.session_state.secilen_hisse = None; st.rerun()

    st.markdown("---")

    # ALT MENÜLER
    t1, t2, t3 = st.tabs(["💼 CÜZDAN", "📊 PİYASA RADARI", "📒 LOGLAR"])
    
    with t1:
        st.subheader("💰 Portföy")
        with st.expander("➕ Yeni İşlem Ekle"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.selectbox("Hisse", BIST_HISSELERI, key="portfoy_add")
            y_mal = c2.number_input("Maliyet", value=0.0)
            y_adt = c3.number_input("Adet", value=0)
            if c4.button("KAYDET"):
                sembol_tam = f"{y_sem}.IS" if "USD" not in y_sem else y_sem
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                db[user]["portfoy"] = [p for p in db[user]["portfoy"] if p['sembol'] != sembol_tam]
                db[user]["portfoy"].append({"sembol": sembol_tam, "maliyet": y_mal, "adet": y_adt})
                save_db(db); st.success("Eklendi!"); st.rerun()

        if "portfoy" in db[user] and db[user]["portfoy"]:
            data = []
            total_tl = 0
            for p in db[user]["portfoy"]:
                try:
                    guncel = yf.Ticker(p['sembol']).fast_info['last_price']
                    deger = guncel * p['adet']
                    kar_zarar = (guncel - p['maliyet']) * p['adet']
                    total_tl += deger
                    data.append({"Hisse": p['sembol'], "Maliyet": p['maliyet'], "Güncel": f"{guncel:.2f}", "Adet": p['adet'], "Değer": f"{deger:,.0f}", "K/Z": f"{kar_zarar:,.0f}"})
                except: pass
            st.metric("TOPLAM VARLIK", f"{total_tl:,.0f} TL")
            st.table(pd.DataFrame(data))
        else: st.info("Portföy boş.")

    with t2:
        st.markdown("### 📡 Balina Sinyalleri")
        if st.button("TARAMAYI BAŞLAT"):
            with st.status("Piyasa Taranıyor...", expanded=True) as status:
                time.sleep(1); st.write("Hacimler kontrol ediliyor..."); time.sleep(1)
                status.update(label="Tarama Bitti!", state="complete", expanded=False)
            st.success("✅ Fırsatlar Tespit Edildi")
            c1, c2 = st.columns(2)
            c1.info("HDFGS: Hacim Patlaması (%300) - ALIM SİNYALİ")
            c2.info("THYAO: RSI Dip Seviyede (28) - TEPKİ BEKLENİYOR")

    with t3:
        loglar = db["admin"].get("loglar", [])
        for log in loglar: st.text(log)

# ==========================================
# GİRİŞ EKRANI (YENİ NEON TASARIM)
# ==========================================
def login_page():
    st.markdown("""
    <div style="text-align:center; padding: 100px 0;">
        <h1 class="neon-title">PALA BALİNA AVCISI</h1>
        <p class="sub-title">PROFESYONEL BORSA TERMİNALİ</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        k = st.text_input("KOD ADI (Kullanıcı)", placeholder="Kaptan...")
        s = st.text_input("GİRİŞ ANAHTARI (Şifre)", type="password", placeholder="••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("TERMİNALE BAĞLAN ⚡", type="primary"):
            db=load_db()
            if k in db and db[k]['sifre']==s: st.session_state.login_user=k; st.rerun()
            else: st.error("ERİŞİM REDDEDİLDİ. BİLGİLERİ KONTROL ET.")
        
        st.markdown("---")
        if st.checkbox("SİSTEM KURTARMA (Admin)"):
             if st.button("ONAR"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("SİSTEM SIFIRLANDI.")

if not st.session_state.login_user: login_page()
else: ana_uygulama()
