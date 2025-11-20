import streamlit as st
import random
import time
import requests
from streamlit_lottie import st_lottie

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Fatoş Hoca ile Bilim", page_icon="🚀", layout="centered")

# --- ANIMASYON YÜKLEME ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Animasyonlar (Bilim İnsanı, Konfeti, Üzgün Surat)
lottie_bilim = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_w51pcehl.json")
lottie_dogru = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_l4xxt7fk.json")
lottie_yanlis = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json")

# --- TASARIM (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@700&display=swap');
    
    .stApp {
        background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
        color: white;
        font-family: 'Comic Neue', cursive;
    }
    h1, h2, h3 {
        color: #FFD700 !important;
        text-shadow: 2px 2px 4px #000;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 70px;
        background: linear-gradient(to bottom, #4facfe 0%, #00f2fe 100%);
        color: white;
        font-weight: bold;
        font-size: 20px;
        border: 3px solid white;
        box-shadow: 0 5px #005cbf;
    }
    .stButton>button:hover {
         background: linear-gradient(to bottom, #ff9a44 0%, #fc6076 100%);
         transform: scale(1.02);
    }
    .bilgi-kutusu {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        text-align: center;
        font-size: 20px;
        margin-bottom: 15px;
    }
    /* Yanlış Cevap Titreme Efekti */
    .shake { animation: shake 0.5s; }
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-5px); }
        100% { transform: translateX(0); }
    }
    </style>
""", unsafe_allow_html=True)

# --- SORULAR ---
sorular = [
    {"soru": "Güneş sistemindeki EN BÜYÜK gezegen hangisidir? 🪐", "secenekler": ["Mars", "Jüpiter", "Satürn", "Dünya"], "cevap": "Jüpiter"},
    {"soru": "Hücrenin enerji santrali neresidir? ⚡", "secenekler": ["Ribozom", "Çekirdek", "Mitokondri", "Koful"], "cevap": "Mitokondri"},
    {"soru": "Kuvvetin birimi nedir? 💪", "secenekler": ["Newton", "Pascal", "Joule", "Watt"], "cevap": "Newton"},
    {"soru": "Işık en hızlı nerede yayılır? 🏃‍♂️💨", "secenekler": ["Camda", "Suda", "Boşlukta", "Havada"], "cevap": "Boşlukta"},
    {"soru": "Limonun tadı nasıldır? 🍋", "secenekler": ["Ekşi", "Acı", "Tatlı", "Tuzlu"], "cevap": "Ekşi"},
    {"soru": "Dünya'nın doğal uydusu nedir? 🌕", "secenekler": ["Güneş", "Ay", "Titan", "Mars"], "cevap": "Ay"},
    {"soru": "Hangi gezegen halkalarıyla ünlüdür? 🪐", "secenekler": ["Mars", "Venüs", "Satürn", "Merkür"], "cevap": "Satürn"},
    {"soru": "Bitkilerde fotosentez nerede olur? 🌿", "secenekler": ["Kloroplast", "Mitokondri", "Hücre Duvarı", "Sitoplazma"], "cevap": "Kloroplast"},
    {"soru": "DNA nerede bulunur? 🧬", "secenekler": ["Hücre Zarı", "Sitoplazma", "Çekirdek", "Koful"], "cevap": "Çekirdek"},
    {"soru": "Hangisi yenilenebilir enerjidir? ☀️", "secenekler": ["Kömür", "Doğalgaz", "Güneş", "Petrol"], "cevap": "Güneş"}
]

# --- OYUN MOTORU ---
if 'soru_index' not in st.session_state:
    st.session_state.soru_index = 0
    st.session_state.bakiye = 0
    st.session_state.joker_kullanildi = False
    st.session_state.oyun_bitti = False
    random.shuffle(sorular)
    st.session_state.sorular = sorular

# --- YAN MENÜ ---
with st.sidebar:
    if lottie_bilim:
        st_lottie(lottie_bilim, height=150)
    st.markdown("### 👩‍🏫 Fatoş Hoca")
    st.info(f"💰 KASA: **{st.session_state.bakiye} TL**")
    if st.button("🔄 Oyunu Sıfırla"):
        st.session_state.soru_index = 0
        st.session_state.bakiye = 0
        st.session_state.joker_kullanildi = False
        st.session_state.oyun_bitti = False
        st.rerun()

# --- ANA EKRAN ---
st.title("🚀 FATOŞ HOCA İLE BİLİM")

if st.session_state.oyun_bitti:
    st.balloons()
    if lottie_dogru: st_lottie(lottie_dogru, height=200)
    st.success(f"🎉 OYUN BİTTİ! KAZANCIN: {st.session_state.bakiye} TL")
    if st.button("TEKRAR OYNA"):
        st.session_state.soru_index = 0
        st.session_state.bakiye = 0
        st.session_state.oyun_bitti = False
        st.rerun()
else:
    soru = st.session_state.sorular[st.session_state.soru_index]
    no = st.session_state.soru_index + 1
    
    # İlerleme
    st.progress(no / len(sorular))
    st.markdown(f"<div class='bilgi-kutusu'>❓ SORU {no}: {soru['soru']}</div>", unsafe_allow_html=True)
    
    # Joker
    if not st.session_state.joker_kullanildi:
        if st.button("🃏 %100 JOKER KULLAN"):
            st.session_state.joker_kullanildi = True
            st.toast(f"💡 Cevap: {soru['cevap']}", icon="🤫")
    else:
        st.warning("🚫 Joker Kullanıldı")

    # Şıklar
    c1, c2 = st.columns(2)
    secenekler = soru['secenekler']
    
    def kontrol(secim):
        if secim == soru['cevap']:
            st.session_state.bakiye += 1000
            st.toast("✅ DOĞRU! +1000 TL", icon="🎉")
            time.sleep(0.5)
        else:
            st.session_state.bakiye -= 500
            st.toast("❌ YANLIŞ! -500 TL", icon="⚠️")
            time.sleep(0.5)
        st.session_state.soru_index += 1
        st.rerun()

    with c1:
        if st.button(f"A) {secenekler[0]}"): kontrol(secenekler[0])
        st.write("")
        if st.button(f"C) {secenekler[2]}"): kontrol(secenekler[2])
    with c2:
        if st.button(f"B) {secenekler[1]}"): kontrol(secenekler[1])
        st.write("")
        if st.button(f"D) {secenekler[3]}"): kontrol(secenekler[3])
