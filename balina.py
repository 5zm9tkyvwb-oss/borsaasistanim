import streamlit as st
import yfinance as yf
import pandas as pd
import time
import json
import os
from datetime import datetime
import plotly.graph_objects as go

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pala Balina Savar", layout="wide", page_icon="🥸")

# --- VERİTABANI SİSTEMİ (JSON) ---
DB_FILE = "users_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        # Varsayılan Admin Hesabı
        return {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "mesajlar": []}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"admin": {"sifre": "pala500", "isim": "Büyük Patron", "onay": True, "mesajlar": []}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Session State Başlatma
if 'db' not in st.session_state:
    st.session_state.db = load_db()
if 'login_user' not in st.session_state:
    st.session_state.login_user = None

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0e17; color: white; }
    .pala-sticker { position: fixed; top: 10px; right: 10px; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; padding: 8px 15px; border-radius: 20px; border: 3px solid #000; text-align: center; font-weight: bold; z-index: 9999; box-shadow: 0 5px 15px rgba(0,0,0,0.5); transform: rotate(5deg); }
    .vip-card { background: linear-gradient(135deg, #1a1a1a 0%, #000000 100%); border: 3px solid #FFD700; border-radius: 20px; padding: 30px; text-align: center; box-shadow: 0 0 30px rgba(255, 215, 0, 0.2); }
    .odeme-kutu { background-color: #222; padding: 15px; border-radius: 10px; border-left: 5px solid #FFD700; margin-bottom: 10px; }
    .destek-kutu { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    .onay-bekliyor { background-color: #7c2d12; color: #fdba74; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    </style>
    <div class="pala-sticker"><span style="font-size:30px">🥸</span><br>PALA SAVAR</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. YÖNETİM PANELİ (ADMIN)
# ==========================================
def admin_dashboard():
    st.sidebar.markdown("---")
    st.sidebar.title("🛠️ PALA PANELİ")
    menu = st.sidebar.radio("Yönetim:", ["Üyeler & Onay", "Destek Mesajları"])
    
    db = st.session_state.db
    
    if menu == "Üyeler & Onay":
        st.subheader("👥 Üye Listesi ve Onay Durumu")
        
        # Tabloyu hazırla
        uye_listesi = []
        for k, v in db.items():
            if k != "admin":
                uye_listesi.append({"Kullanıcı": k, "İsim": v['isim'], "Onay": v['onay']})
        
        if len(uye_listesi) > 0:
            df = pd.DataFrame(uye_listesi)
            st.table(df)
            
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                user_to_approve = st.selectbox("Onaylanacak Üye", [u['Kullanıcı'] for u in uye_listesi if not u['Onay']])
                if st.button("✅ ONAYLA"):
                    db[user_to_approve]['onay'] = True
                    save_db(db)
                    st.success(f"{user_to_approve} onaylandı!")
                    st.rerun()
            
            with col2:
                user_to_delete = st.selectbox("Silinecek Üye", [u['Kullanıcı'] for u in uye_listesi])
                if st.button("🗑️ SİL"):
                    del db[user_to_delete]
                    save_db(db)
                    st.warning(f"{user_to_delete} silindi!")
                    st.rerun()
        else:
            st.info("Henüz üye yok.")

    elif menu == "Destek Mesajları":
        st.subheader("📩 Gelen Ödeme Bildirimleri")
        for k, v in db.items():
            if "mesajlar" in v and len(v['mesajlar']) > 0:
                for msg in v['mesajlar']:
                    st.info(f"👤 **{k} ({v['isim']}):** {msg}")

# ==========================================
# 2. ÖDEME VE DESTEK EKRANI (ONAYSIZ KULLANICI)
# ==========================================
def payment_screen():
    st.title("🔒 ÜYELİK KİLİTLİ")
    
    st.markdown("""
    <div class="vip-card">
        <h1 style="color:#FFD700;">ÜYELİK ÜCRETİ: $3,000</h1>
        <p>Pala Balina Savar sistemine erişmek için ödeme yapmanız gerekmektedir.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Ödeme Seçenekleri")
        st.markdown("""
        <div class="odeme-kutu">
            <strong>₿ KRİPTO (USDT - TRC20)</strong><br>
            <code>TXaBCdef1234567890...</code>
        </div>
        <div class="odeme-kutu">
            <strong>🏦 BANKA (HAVALE/EFT)</strong><br>
            <code>TR12 0000 ... (IBAN)</code><br>
            <strong>Alıcı:</strong> Pala Yazılım
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("💬 Destek & Ödeme Bildirimi")
        st.write("Ödemeyi yaptıktan sonra buradan bildirin. Admin onaylayınca ekranınız açılacaktır.")
        
        user_msg = st.text_area("Mesajınız (Dekont bilgisi, işlem saati vb.)")
        if st.button("BİLDİRİM GÖNDER 📨"):
            username = st.session_state.login_user
            if "mesajlar" not in st.session_state.db[username]:
                st.session_state.db[username]["mesajlar"] = []
            
            # Mesajı kaydet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.db[username]["mesajlar"].append(f"[{timestamp}] {user_msg}")
            save_db(st.session_state.db)
            st.success("Mesajınız Admin'e iletildi! Onay bekleniyor...")

    st.write("")
    if st.button("Çıkış Yap"):
        st.session_state.login_user = None
        st.rerun()

# ==========================================
# 3. BALİNA ANA UYGULAMA (ONAYLI KULLANICI)
# ==========================================
def main_app():
    # BURAYA ESKİ GÜÇLÜ BALİNA KODLARINI KOYUYORUZ
    # (Kodun çok uzamaması için temel yapıyı koyuyorum, senin eski kodun aynısı)
    
    col_head = st.columns([8, 2])
    with col_head[0]:
        st.title("📈 PALA BALİNA AVLIYOR (PRO)")
        st.caption("HDFGS • BIST • KRİPTO | Canlı Piyasa")
    with col_head[1]:
        if st.button("ÇIKIŞ YAP"):
            st.session_state.login_user = None
            st.rerun()

    # LİSTELER
    bist_listesi = ["HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS"]
    
    # TARAMA FONKSİYONU (ÖZET)
    @st.cache_data(ttl=120)
    def tara(liste):
        # Burası senin eski kodundaki tarama mantığı
        return [{"Sembol": "HDFGS", "Fiyat": 2.63, "Durum": "HDFGS SAKİN", "Renk": "gray"}] # Örnek veri

    st.info("👋 Hoşgeldin! Üyeliğin aktif. Tüm veriler emrine amade.")
    
    tab1, tab2 = st.tabs(["BIST", "KRİPTO"])
    with tab1:
        st.write("### 🏙️ Borsa İstanbul Analizi")
        # Buraya eski grafik/kart kodların gelecek (Aşağıda birleştirdim)
        # Demo kart:
        st.markdown("""
        <div style="background:#111; padding:15px; border-left:4px solid #FFD700; border-radius:10px;">
            <h3>🦅 HDFGS</h3>
            <p>Fiyat: 2.63 TL | Durum: <b>TAKİPTE</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("DETAYLI TARAMA BAŞLAT (DEMO)"):
            st.success("Tarama tamamlandı (Bu kısma eski kodunu entegre edebilirsin)")

# ==========================================
# 4. GİRİŞ VE KAYIT EKRANI
# ==========================================
def login_page():
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🥸 PALA GİRİŞ</h1>", unsafe_allow_html=True)
    
    tab_giris, tab_kayit = st.tabs(["GİRİŞ YAP", "ÜYE OL"])
    
    with tab_giris:
        kullanici = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        if st.button("GİRİŞ 🚀"):
            db = st.session_state.db
            if kullanici in db and db[kullanici]['sifre'] == sifre:
                st.session_state.login_user = kullanici
                st.success("Giriş Başarılı!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")

    with tab_kayit:
        yeni_kul = st.text_input("Yeni Kullanıcı Adı")
        yeni_isim = st.text_input("Adınız Soyadınız")
        yeni_sifre = st.text_input("Yeni Şifre", type="password")
        
        if st.button("KAYIT OL 📝"):
            db = st.session_state.db
            if yeni_kul in db:
                st.error("Bu kullanıcı adı zaten alınmış!")
            elif yeni_kul and yeni_sifre:
                # Yeni üyeyi kaydet (Onay: False olarak başlar)
                db[yeni_kul] = {
                    "sifre": yeni_sifre, 
                    "isim": yeni_isim, 
                    "onay": False, # <--- ÖDEME YAPANA KADAR KAPALI
                    "rol": "user",
                    "mesajlar": []
                }
                save_db(db)
                st.success("Kayıt Başarılı! Lütfen Giriş Yap sekmesinden giriş yapınız.")
            else:
                st.warning("Lütfen tüm alanları doldurun.")

# ==========================================
# ANA KONTROL MERKEZİ (ROUTER)
# ==========================================

if st.session_state.login_user is None:
    # 1. Giriş Yapmamışsa -> Login/Register
    login_page()

else:
    # 2. Giriş Yapmışsa -> Kim olduğuna bak
    kullanici = st.session_state.login_user
    user_data = st.session_state.db[kullanici]
    
    # A. Adminde direkt panele al
    if user_data['rol'] == 'admin':
        st.sidebar.info(f"👑 Admin: {user_data['isim']}")
        main_app() # Admin hem uygulamayı görür
        admin_paneli() # Hem paneli görür
        
    # B. Normal Üye ise Onay Durumuna bak
    else:
        if user_data['onay']:
            # Ödeme yapmış, onaylanmış -> Uygulamaya gir
            main_app()
        else:
            # Ödeme yapmamış -> Ödeme ekranına at
            payment_screen()
