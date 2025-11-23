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
# 💰 CÜZDAN AYARLARI
# ==========================================
USDT_ADDRESS = "TV4DK7vckLWJciKSqhvY5hEpcw1Ka522AQ"

# ==========================================
# 📜 BIST HİSSE LİSTESİ (TÜMÜ)
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
if 'login_user' not in st.session_state: st.session_state.login_user = None
if 'secilen_hisse' not in st.session_state: st.session_state.secilen_hisse = None

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
    
    /* --- NEON BAŞLIKLAR --- */
    .neon-title {
        font-size: 60px !important; font-weight: 900; color: #fff; text-align: center;
        text-shadow: 0 0 10px #00fff9, 0 0 40px #00fff9, 0 0 80px #ff00ff;
        animation: flicker 2s infinite alternate;
    }
    @keyframes flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { text-shadow: 0 0 10px #00fff9, 0 0 40px #00fff9, 0 0 80px #ff00ff; }
        20%, 24%, 55% { text-shadow: none; }
    }
    
    /* --- CÜZDAN KUTUSU (Ödeme Ekranı) --- */
    .wallet-box {
        background: rgba(0,0,0,0.6);
        border: 2px solid #00fff9;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 249, 0.2);
    }
    .wallet-addr {
        font-family: monospace;
        font-size: 20px;
        color: #ff00ff;
        font-weight: bold;
        word-break: break-all;
        background: #000;
        padding: 10px;
        border-radius: 5px;
        border: 1px dashed #ff00ff;
    }
    
    /* --- TABLOLAR & INPUTLAR --- */
    div[data-testid="stTable"], table { background-color: rgba(13, 17, 23, 0.9) !important; border: 1px solid #00fff9 !important; color: #e6e6e6 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea { 
        background-color: rgba(13, 17, 23, 0.8) !important; color: #00fff9 !important; border: 1px solid #30363d !important; 
    }
    .stTextInput input:focus { border-color: #00fff9 !important; box-shadow: 0 0 15px #00fff9 !important; }
    
    /* --- BUTONLAR --- */
    div.stButton > button {
        background: linear-gradient(90deg, #00fff9, #ff00ff) !important;
        color: #000 !important; border: none !important; font-weight: 800 !important;
    }
    div.stButton > button:hover { transform: scale(1.02) !important; box-shadow: 0 0 20px #00fff9 !important; }
    
    /* --- EN ÇOK YÜKSELEN/DÜŞEN TABLOLARI --- */
    .top-list-box {
        background: rgba(0,0,0,0.5);
        padding: 10px;
        border-radius: 8px;
        border-top: 3px solid #00fff9;
        margin-bottom: 5px;
    }
    .list-title { color: #00fff9; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; font-size: 14px; }
    .list-item { font-size: 13px; border-bottom: 1px solid #333; padding: 3px 0; display: flex; justify-content: space-between; }
    .pos { color: #38ef7d; } .neg { color: #ef473a; } .spek { color: #ff00ff; }
    
    /* --- STICKER --- */
    .pala-sticker { 
        position: fixed; top: 70px; right: 25px; 
        background: linear-gradient(45deg, #00fff9, #ff00ff);
        color: #000; padding: 8px 16px; border-radius: 4px; 
        font-weight: 900; z-index: 9999; animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { box-shadow: 0 0 10px #00fff9; } 50% { box-shadow: 0 0 30px #ff00ff; } 100% { box-shadow: 0 0 10px #00fff9; } }
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
        db["admin"]["loglar"].insert(0, f"⏰ {tarih} | {mesaj}")
        db["admin"]["loglar"] = db["admin"]["loglar"][:50]
        save_db(db)
    except: pass

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

# --- PİYASA TARAMA (TOP GAINERS/LOSERS) ---
@st.cache_data(ttl=3600)
def get_market_analysis():
    # Hız için kısıtlı bir liste kullanıyoruz, gerçek uygulamada veritabanı gerekir.
    candidates = ["THYAO.IS", "ASELS.IS", "GARAN.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", "HEKTS.IS", "EREGL.IS", "KCHOL.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", "KONTR.IS", "GUBRF.IS", "FROTO.IS", "ASTOR.IS", "REEDR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "HDFGS.IS", "ISCTR.IS", "YKBNK.IS", "PETKM.IS", "KOZAL.IS", "KRDMD.IS", "VESTL.IS", "ARCLK.IS", "TOASO.IS", "TTKOM.IS", "TCELL.IS", "SOKM.IS", "MGROS.IS", "ALFAS.IS", "CANTE.IS", "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS"]
    
    weekly_data = []
    monthly_data = []
    
    for s in candidates:
        try:
            # 1 Aylık veri çek
            df = yf.download(s, period="1mo", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son = df['Close'].iloc[-1]
                
                # Haftalık (5 gün)
                w_start = df['Close'].iloc[-5]
                w_change = ((son - w_start) / w_start) * 100
                
                # Aylık (20 gün)
                m_start = df['Close'].iloc[0]
                m_change = ((son - m_start) / m_start) * 100
                
                # Spek Skoru (Volatilite: (High-Low)/Open)
                volatility = ((df['High'].iloc[-1] - df['Low'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                sym = s.replace(".IS","")
                weekly_data.append({"Sembol": sym, "Degisim": w_change, "Fiyat": son, "Volatilite": volatility})
                monthly_data.append({"Sembol": sym, "Degisim": m_change, "Fiyat": son})
        except: pass
        
    # Sıralama
    w_gainers = sorted(weekly_data, key=lambda x: x['Degisim'], reverse=True)[:5]
    w_losers = sorted(weekly_data, key=lambda x: x['Degisim'])[:5]
    m_gainers = sorted(monthly_data, key=lambda x: x['Degisim'], reverse=True)[:5]
    spek_list = sorted(weekly_data, key=lambda x: x['Volatilite'], reverse=True)[:5]
    
    return w_gainers, m_gainers, w_losers, spek_list

# ==========================================
# 👑 ADMIN PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 YÖNETİM")
    menu = st.sidebar.radio("Menü:", ["Üye Yönetimi", "Gelen Bildirimler", "Manuel Üye Ekle"])
    db = load_db()
    
    if menu == "Üye Yönetimi":
        st.subheader("👥 KULLANICI LİSTESİ")
        for k, v in db.items():
            if k != "admin":
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1: st.markdown(f"**{v.get('isim')}** ({k})")
                with col2: 
                    if v.get('onay'): st.success("AKTİF ✅")
                    else: st.warning("ONAY BEKLİYOR ⏳")
                with col3:
                    if not v.get('onay'):
                        if st.button(f"ONAYLA ✅", key=f"app_{k}"): db[k]['onay'] = True; save_db(db); st.rerun()
                    else:
                        if st.button(f"ENGELLE ⛔", key=f"ban_{k}"): db[k]['onay'] = False; save_db(db); st.rerun()
                with col4:
                    if st.button(f"SİL 🗑️", key=f"del_{k}"): del db[k]; save_db(db); st.rerun()
                st.divider()

    elif menu == "Gelen Bildirimler":
        st.subheader("📩 ÖDEME BİLDİRİMLERİ")
        msg_found = False
        for k, v in db.items():
            if "mesajlar" in v and v['mesajlar']:
                msg_found = True
                with st.expander(f"✉️ {v.get('isim')} ({k}) - {len(v['mesajlar'])} Mesaj", expanded=True):
                    for m in v['mesajlar']: st.info(m)
                    if st.button(f"Temizle ({k})", key=f"clr_{k}"): db[k]['mesajlar'] = []; save_db(db); st.rerun()
        if not msg_found: st.info("Yeni bildirim yok.")

    elif menu == "Manuel Üye Ekle":
        st.subheader("➕ MANUEL ÜYE EKLE")
        c1, c2 = st.columns(2)
        n_user = c1.text_input("Nick")
        n_pass = c2.text_input("Şifre")
        n_name = st.text_input("İsim")
        if st.button("Oluştur"):
            if n_user and n_pass:
                db[n_user] = {"sifre": n_pass, "isim": n_name, "onay": True, "rol": "user", "mesajlar": [], "portfoy": []}
                save_db(db); st.success("Eklendi.")

# ==========================================
# 💰 ÖDEME EKRANI
# ==========================================
def payment_screen():
    u = st.session_state.login_user; db = load_db()
    st.markdown("""<div style="text-align:center; padding-top:20px;"><h1 style="color:#ff00ff;">⛔ ERİŞİM KISITLI ⛔</h1><p>HESABINIZ HENÜZ AKTİF DEĞİL.</p></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="wallet-box"><h3 style="color:#00fff9;">💎 USDT (TRC20) CÜZDAN</h3><div class="wallet-addr">{USDT_ADDRESS}</div></div>""", unsafe_allow_html=True)
    st.subheader("📩 Ödeme Bildirimi")
    col1, col2 = st.columns([3, 1])
    with col1: tx_msg = st.text_area("Açıklama / TXID")
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("GÖNDER 🚀"):
            if tx_msg:
                tarih = datetime.now().strftime("%d/%m %H:%M")
                if "mesajlar" not in db[u]: db[u]["mesajlar"] = []
                db[u]["mesajlar"].append(f"[{tarih}] {tx_msg}")
                save_db(db); st.success("İletildi."); send_telegram(f"💰 ÖDEME: {u} -> {tx_msg}")
    st.divider()
    if st.button("ÇIKIŞ YAP 🔙"): st.session_state.login_user = None; st.rerun()

# ==========================================
# 📈 ANA UYGULAMA
# ==========================================
def ana_uygulama():
    st.markdown("""
    <div style="background:#050a14; border-bottom:2px solid #00fff9; padding:5px; margin-bottom:20px;">
        <div style="animation:marquee 30s linear infinite; color:#00fff9; font-weight:800; white-space:nowrap;">
            💵 USD/TRY: 34.50 ⏐ 💶 EUR/TRY: 37.20 ⏐ ₿ BTC: $98,000 ⏐ 🦈 PALA BALİNA AVCISI AKTİF
        </div>
    </div><style>@keyframes marquee { 0% {transform:translateX(0);} 100% {transform:translateX(-100%);} }</style>
    """, unsafe_allow_html=True)

    user = st.session_state.login_user; db = st.session_state.db
    c1, c2 = st.columns([8, 2])
    c1.markdown(f"<h1 style='color:#00fff9;'>🦈 PALA BALİNA AVCISI</h1>", unsafe_allow_html=True)
    c1.markdown(f"Kaptan: **{db[user].get('isim')}**")
    if c2.button("GÜVENLİ ÇIKIŞ"): st.session_state.login_user=None; st.rerun()
    if db[user].get('rol') == 'admin': admin_dashboard()
    
    st.markdown("---")

    # --- YENİ EKLENEN BÖLÜM: 4'LÜ PİYASA TARAMA ---
    st.markdown("### 📡 PİYASA RÖNTGENİ")
    w_gain, m_gain, w_lose, spek = get_market_analysis()
    
    col_w, col_m, col_l, col_s = st.columns(4)
    
    with col_w:
        st.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🟢 HAFTALIK KRALLAR</div>", unsafe_allow_html=True)
        for i in w_gain:
            st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='pos'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m:
        st.markdown(f"<div class='top-list-box' style='border-color:#38ef7d;'><div class='list-title'>🗓️ AYLIK ROKETLER</div>", unsafe_allow_html=True)
        for i in m_gain:
            st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='pos'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_l:
        st.markdown(f"<div class='top-list-box' style='border-color:#ef473a;'><div class='list-title'>🔴 HAFTALIK KAYIPLAR</div>", unsafe_allow_html=True)
        for i in w_lose:
            st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='neg'>%{i['Degisim']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_s:
        st.markdown(f"<div class='top-list-box' style='border-color:#ff00ff;'><div class='list-title'>🎰 SPEK / VOLATİL</div>", unsafe_allow_html=True)
        for i in spek:
            st.markdown(f"<div class='list-item'><span>{i['Sembol']}</span><span class='spek'>⚡ {i['Volatilite']:.1f}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # HİSSE SORGULAMA
    st.markdown("### 🔍 DETAYLI ANALİZ")
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
# 🔐 GİRİŞ & KAYIT
# ==========================================
def login_page():
    st.markdown("""<div style="text-align:center; padding:50px;"><h1 class="neon-title">PALA BALİNA</h1><p style="color:#00fff9;">MEMBERSHIP ACCESS TERMINAL</p></div>""", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 GİRİŞ YAP", "📝 ÜYE OL"])
    
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            k = st.text_input("Kullanıcı Adı", key="l_user")
            s = st.text_input("Şifre", type="password", key="l_pass")
            if st.button("TERMİNALE GİRİŞ ⚡", type="primary"):
                db = load_db()
                if k in db and db[k]['sifre'] == s: st.session_state.login_user = k; st.rerun()
                else: st.error("Hatalı!")

    with tab2:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### Yeni Üyelik Formu")
            r_user = st.text_input("Kullanıcı Adı", key="r_user")
            r_name = st.text_input("Ad Soyad", key="r_name")
            r_pass = st.text_input("Şifre", type="password", key="r_pass")
            if st.button("KAYDI TAMAMLA ✅"):
                db = load_db()
                if r_user in db: st.warning("Alınmış!")
                elif r_user and r_pass:
                    db[r_user] = {"sifre": r_pass, "isim": r_name, "onay": False, "rol": "user", "mesajlar": [], "portfoy": []}
                    save_db(db); st.success("Kaydolundu."); send_telegram(f"🆕 ÜYE: {r_user}")
    
    if st.checkbox("Admin Reset"):
        if st.button("Reset"):
             st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
             save_db(st.session_state.db); st.success("Resetlendi.")

if not st.session_state.login_user: login_page()
else:
    u_id = st.session_state.login_user; db = load_db()
    if u_id in db:
        if db[u_id].get('rol') == 'admin' or db[u_id].get('onay'): ana_uygulama()
        else: payment_screen()
    else: st.session_state.login_user = None; st.rerun()
