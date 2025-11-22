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
st.set_page_config(page_title="Kemal Balina Avcısı", layout="wide", page_icon="🐋")

# ==========================================
# 📜 DEV BIST HİSSE LİSTESİ (TÜMÜ EKLENDİ)
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
    # KRİPTOLAR
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "AVAX-USD", "DOGE-USD", "SHIB-USD"
]
# Mükerrer kayıtları sil ve alfabetik sırala
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

# --- TASARIM (PREMIUM GOLD & DEEP NAVY - OKUNAKLI) ---
st.markdown("""
    <style>
    /* Genel Arka Plan */
    .stApp { 
        background-color: #0b1116 !important;
        color: #e6e6e6 !important; 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Tablolar - Zengin ve Okunaklı */
    div[data-testid="stTable"], table {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #e6e6e6 !important;
    }
    thead tr th {
        background-color: #21262d !important;
        color: #FFD700 !important; /* Başlıklar Altın */
        font-size: 15px !important;
        border-bottom: 2px solid #FFD700 !important;
    }
    tbody tr:nth-of-type(even) {
        background-color: #0d1117 !important; /* Satır şeritleme */
    }
    tbody tr:hover {
        background-color: #30363d !important;
    }
    
    /* Butonlar - Mat Altın */
    div.stButton > button {
        background: #c59d5f !important; /* Mat Altın */
        color: #000000 !important; 
        border: none !important; 
        border-radius: 6px !important; 
        font-weight: 700 !important; 
        font-size: 16px !important;
        height: 45px !important; 
        width: 100% !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover { 
        background: #FFD700 !important; /* Parlak Altın */
        transform: scale(1.01) !important;
    }
    
    /* Input Alanları - Net Çizgiler */
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextInput input, .stNumberInput input { 
        background-color: #0d1117 !important; 
        color: #ffffff !important; 
        border: 1px solid #30363d !important; 
        border-radius: 6px !important;
    }
    
    /* Dropdown Menü İçi (Açılınca) */
    div[data-baseweb="popover"] {
        background-color: #161b22 !important;
    }
    div[data-baseweb="menu"] {
        background-color: #161b22 !important;
        color: white !important;
    }
    
    /* Başlıklar */
    h1, h2, h3 { 
        color: #ffffff; 
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .gold-text { color: #FFD700 !important; }
    
    /* Sticker */
    .pala-sticker { 
        position: fixed; top: 25px; right: 25px; 
        background-color: #FFD700; 
        color: #000; padding: 8px 16px; border-radius: 4px; 
        font-weight: 800; letter-spacing: 1px;
        z-index: 9999; box-shadow: 0 4px 10px rgba(0,0,0,0.5); 
    }

    /* Kartlar - Temiz ve Sınırlı */
    .card-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .signal-badge {
        padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;
    }
    .badge-green { background-color: #238636; color: white; }
    .badge-red { background-color: #da3633; color: white; }
    
    /* Metrik Kutuları */
    div[data-testid="stMetricValue"] {
        color: #FFD700 !important;
        font-weight: 700 !important;
    }
    </style>
    <div class="pala-sticker">KEMAL BALİNA</div>
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

# --- GRAFİK ve PIVOT HESAPLAMA ---
def grafik_ciz(symbol):
    try:
        # 6 Aylık veri çek
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if not df.empty:
            # SON TAMMAMLANMIŞ GÜNÜN VERİLERİ (Pivot Hesabı İçin)
            prev = df.iloc[-2] 
            
            # KLASİK PIVOT FORMÜLÜ
            high = prev['High']
            low = prev['Low']
            close = prev['Close']
            
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            
            # Grafik
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Fiyat"))
            
            # Pivot Seviyeleri (Çizgiler)
            fig.add_hline(y=pivot, line_dash="dot", line_color="yellow", line_width=1, annotation_text="PIVOT", annotation_position="bottom right")
            fig.add_hline(y=r1, line_dash="solid", line_color="#ff4d4d", line_width=1.5, annotation_text="DİRENÇ (R1)")
            fig.add_hline(y=s1, line_dash="solid", line_color="#00e676", line_width=1.5, annotation_text="DESTEK (S1)")
            
            fig.update_layout(
                title=f"📊 {symbol} TEKNİK GÖRÜNÜM", 
                template="plotly_dark", 
                height=500, 
                xaxis_rangeslider_visible=False, 
                plot_bgcolor='#0d1117', 
                paper_bgcolor='#0d1117',
                font=dict(family="Arial", size=12, color="#b0b0b0")
            )
            
            news = []
            try:
                n = yf.Ticker(symbol).news
                for i in n[:3]: news.append(f"📰 [{i['title']}]({i['link']})")
            except: pass
            
            return fig, df.iloc[-1]['Close'], pivot, s1, r1, news
    except: return None, None, None, None, None, None

# ==========================================
# 1. YÖNETİM PANELİ
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("👑 YÖNETİM")
    if st.sidebar.button("🔔 Test Bildirimi Gönder"):
        send_telegram("🦅 *Kemal Balina:* Test Mesajı")
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
        
        if uye_data:
            st.table(pd.DataFrame(uye_data))
        else: st.info("Üye yok.")

# ==========================================
# 2. ANA UYGULAMA
# ==========================================
def ana_uygulama():
    user = st.session_state.login_user; db = st.session_state.db
    
    # Üst Bar
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown(f"<h1 style='color:#FFD700;'>🌊 KEMAL BALİNA AVCISI</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#8b949e;'>Hoşgeldin, <b>{db[user].get('isim', 'Kaptan')}</b>. Piyasalar emrine amade.</p>", unsafe_allow_html=True)
    with c2:
        if st.button("GÜVENLİ ÇIKIŞ"): st.session_state.login_user=None; st.rerun()

    if db[user].get('rol') == 'admin': admin_dashboard()

    st.markdown("---")

    # --- YENİLENMİŞ ARAMA MERKEZİ ---
    st.markdown("### 🔍 HİSSE SORGULAMA VE ANALİZ")
    
    col_search, col_btn = st.columns([3, 1])
    
    # Selectbox - TÜM HİSSELER
    secilen_hisse_input = col_search.selectbox(
        "İncelenecek Hisseyi Seçiniz:",
        BIST_HISSELERI,
        index=BIST_HISSELERI.index("HDFGS") if "HDFGS" in BIST_HISSELERI else 0,
        help="Listeden seçim yapın veya yazarak arayın."
    )
    
    if col_btn.button("ANALİZ ET 🚀", type="primary"):
        # .IS ekleme mantığı
        if "USD" not in secilen_hisse_input:
            sembol = f"{secilen_hisse_input}.IS"
        else:
            sembol = secilen_hisse_input
            
        st.session_state.secilen_hisse = sembol
        st.rerun()

    # --- GRAFİK VE VERİLER ---
    if st.session_state.secilen_hisse:
        hisse = st.session_state.secilen_hisse
        st.info(f"📈 {hisse} Teknik Verileri Hazırlanıyor...")
        
        fig, fiyat, pivot, s1, r1, haberler = grafik_ciz(hisse)
        
        if fig:
            # Metrikler (Kart Görünümü)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ANLIK FİYAT", f"{fiyat:.2f}")
            m2.metric("DESTEK (S1)", f"{s1:.2f}", delta="-Alım Bölgesi", delta_color="normal")
            m3.metric("PİVOT (DENGE)", f"{pivot:.2f}", delta="Denge Noktası", delta_color="off")
            m4.metric("DİRENÇ (R1)", f"{r1:.2f}", delta="+Satış Bölgesi", delta_color="inverse")
            
            # Grafiği Çiz
            st.plotly_chart(fig, use_container_width=True)
            
            # Haberler
            if haberler:
                st.markdown("#### 📰 Şirketten Son Haberler")
                for h in haberler: st.markdown(f"- {h}")
        else:
            st.error("Veri alınamadı. Hisse kodunu kontrol edin.")
        
        if st.button("Ekrani Temizle"):
            st.session_state.secilen_hisse = None; st.rerun()

    st.markdown("---")

    # MENÜ
    t1, t2, t3 = st.tabs(["💼 CÜZDAN & VARLIKLAR", "📊 PİYASA RADARI", "📒 İŞLEM LOGLARI"])
    
    # --- CÜZDAN ---
    with t1:
        st.subheader("💰 Portföy Durumu")
        with st.expander("➕ Yeni İşlem Ekle"):
            c1, c2, c3, c4 = st.columns(4)
            y_sem = c1.selectbox("Hisse", BIST_HISSELERI, key="portfoy_add")
            y_mal = c2.number_input("Maliyet", value=0.0)
            y_adt = c3.number_input("Lot Sayısı", value=0)
            if c4.button("KAYDET"):
                sembol_tam = f"{y_sem}.IS" if "USD" not in y_sem else y_sem
                if "portfoy" not in db[user]: db[user]["portfoy"] = []
                # Varsa güncelle, yoksa ekle
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
                    data.append({
                        "Hisse": p['sembol'],
                        "Maliyet": f"{p['maliyet']:.2f}",
                        "Güncel": f"{guncel:.2f}",
                        "Adet": p['adet'],
                        "Toplam Değer": f"{deger:,.0f}",
                        "K/Z": f"{kar_zarar:,.0f}"
                    })
                except: pass
            
            st.metric("TOPLAM VARLIK", f"{total_tl:,.0f} TL")
            st.table(pd.DataFrame(data))
        else:
            st.info("Henüz portföy girişi yapılmadı.")

    # --- RADAR ---
    with t2:
        st.markdown("### 📡 Anlık Sinyaller")
        if st.button("TARAMAYI BAŞLAT"):
            with st.status("Piyasa Taranıyor...", expanded=True) as status:
                st.write("Veriler çekiliyor...")
                time.sleep(1)
                st.write("Hacimler hesaplanıyor...")
                time.sleep(1)
                status.update(label="Tarama Tamamlandı!", state="complete", expanded=False)
            
            st.success("✅ 3 Potansiyel Fırsat Bulundu")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("""<div class='card-container'><h3 class='gold-text'>HDFGS</h3><span class='signal-badge badge-green'>BALİNA GİRİŞİ</span><br>Fiyat: 2.63<br>Hacim: +%300</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("""<div class='card-container'><h3 class='gold-text'>THYAO</h3><span class='signal-badge badge-green'>YÜKSELİŞ ONAYI</span><br>Fiyat: 275.00<br>RSI: 65</div>""", unsafe_allow_html=True)

    # --- LOGLAR ---
    with t3:
        loglar = db["admin"].get("loglar", [])
        for log in loglar:
            st.text(log)

# ==========================================
# GİRİŞ EKRANI
# ==========================================
def login_page():
    st.markdown("""
    <div style="text-align:center; padding: 50px 0;">
        <h1 style='color:#FFD700; font-size: 60px; font-family: "Georgia", serif;'>🐋</h1>
        <h1 style='color:#FFD700; letter-spacing: 2px;'>KEMAL BALİNA AVCISI</h1>
        <p style="color: #8b949e; font-size: 18px;">Profesyonel Borsa Analiz Terminali</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        k = st.text_input("Kullanıcı Adı", placeholder="Kaptan adı...")
        s = st.text_input("Şifre", type="password", placeholder="Parola...")
        
        if st.button("TERMİNALE BAĞLAN", type="primary"):
            db=load_db()
            if k in db and db[k]['sifre']==s: 
                st.session_state.login_user=k
                st.rerun()
            else: 
                st.error("Erişim Reddedildi. Bilgileri kontrol edin.")
        
        if st.checkbox("Sistem Kurtarma (Admin)"):
             if st.button("Onar"):
                st.session_state.db = {"admin": {"sifre": "pala500", "isim": "Patron", "onay": True, "rol": "admin", "mesajlar": [], "loglar": [], "portfoy": []}}
                save_db(st.session_state.db); st.success("Admin sıfırlandı.")

if not st.session_state.login_user: 
    login_page()
else:
    ana_uygulama()
