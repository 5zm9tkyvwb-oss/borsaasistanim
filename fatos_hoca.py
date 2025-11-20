import streamlit as st
import random
import time

# --- SAYFA AYARLARI VE MAVİ TEMA ---
st.set_page_config(page_title="Fatoş Hoca ile Fen Bilimleri", layout="centered")

# Özel CSS (Mavi Tema ve Butonlar)
st.markdown("""
    <style>
    .stApp {
        background-color: #1E3D59;
        color: white;
    }
    h1, h2, h3 {
        color: #F5F0E1 !important;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 60px;
        background-color: #F5F0E1;
        color: #1E3D59;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FF6F61;
        color: white;
    }
    .bilgi-kutusu {
        background-color: #112D4E;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #F5F0E1;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- SORU HAVUZU (Ortaokul Fen Bilimleri) ---
# Buraya istediğin kadar soru ekleyebilirsin. Formatı bozma yeter.
sorular = [
    {"soru": "Güneş sistemindeki en büyük gezegen hangisidir?", "secenekler": ["Mars", "Jüpiter", "Satürn", "Dünya"], "cevap": "Jüpiter"},
    {"soru": "Hücrenin enerji üretim merkezi neresidir?", "secenekler": ["Ribozom", "Çekirdek", "Mitokondri", "Koful"], "cevap": "Mitokondri"},
    {"soru": "Kuvvetin birimi nedir?", "secenekler": ["Newton", "Pascal", "Joule", "Watt"], "cevap": "Newton"},
    {"soru": "Maddenin hallerinden hangisinde tanecikler arası boşluk en fazladır?", "secenekler": ["Katı", "Sıvı", "Gaz", "Plazma"], "cevap": "Gaz"},
    {"soru": "Aşağıdakilerden hangisi yenilenebilir enerji kaynağıdır?", "secenekler": ["Kömür", "Doğalgaz", "Rüzgar", "Petrol"], "cevap": "Rüzgar"},
    {"soru": "Işığın en hızlı yayıldığı ortam hangisidir?", "secenekler": ["Cam", "Su", "Boşluk", "Hava"], "cevap": "Boşluk"},
    {"soru": "Asitlerin tadı nasıldır?", "secenekler": ["Ekşi", "Acı", "Tatlı", "Tuzlu"], "cevap": "Ekşi"},
    {"soru": "Dünya'nın tek doğal uydusu nedir?", "secenekler": ["Güneş", "Ay", "Titan", "Mars"], "cevap": "Ay"},
    {"soru": "Elektrik akımını ölçen aletin adı nedir?", "secenekler": ["Voltmetre", "Ampermetre", "Termometre", "Barometre"], "cevap": "Ampermetre"},
    {"soru": "İnsan vücudundaki en uzun kemik hangisidir?", "secenekler": ["Kaval Kemiği", "Kafatası", "Uyluk Kemiği", "Kaburga"], "cevap": "Uyluk Kemiği"},
    {"soru": "PH cetvelinde 7-14 arası hangi özelliği gösterir?", "secenekler": ["Asidik", "Bazik", "Nötr", "Tuzlu"], "cevap": "Bazik"},
    {"soru": "Hangi gezegenin halkalarıyla ünlüdür?", "secenekler": ["Mars", "Venüs", "Satürn", "Merkür"], "cevap": "Satürn"},
    {"soru": "Sıvı basıncı hangisine bağlı değildir?", "secenekler": ["Derinlik", "Sıvının Yoğunluğu", "Kabın Şekli", "Yerçekimi"], "cevap": "Kabın Şekli"},
    {"soru": "Bitkilerde fotosentez nerede gerçekleşir?", "secenekler": ["Kloroplast", "Mitokondri", "Hücre Duvarı", "Sitoplazma"], "cevap": "Kloroplast"},
    {"soru": "Atomun çekirdeğinde hangi parçacıklar bulunur?", "secenekler": ["Proton ve Elektron", "Proton ve Nötron", "Sadece Elektron", "Nötron ve Elektron"], "cevap": "Proton ve Nötron"},
    {"soru": "Aşağıdakilerden hangisi bir elementtir?", "secenekler": ["Su", "Hava", "Demir", "Tuz"], "cevap": "Demir"},
    {"soru": "Sürtünme kuvveti hareketi nasıl etkiler?", "secenekler": ["Hızlandırır", "Yavaşlatır", "Yönünü Değiştirir", "Etkilemez"], "cevap": "Yavaşlatır"},
    {"soru": "DNA nerede bulunur?", "secenekler": ["Hücre Zarı", "Sitoplazma", "Çekirdek", "Koful"], "cevap": "Çekirdek"},
    {"soru": "Ses boşlukta yayılır mı?", "secenekler": ["Evet, çok hızlı", "Hayır, yayılmaz", "Sadece sıcakta yayılır", "Az yayılır"], "cevap": "Hayır, yayılmaz"},
    {"soru": "Güneş tutulması sırasında hangisi ortada bulunur?", "secenekler": ["Dünya", "Ay", "Güneş", "Mars"], "cevap": "Ay"},
]

# --- OYUN MOTORU ---

# Hafızayı Başlat
if 'soru_index' not in st.session_state:
    st.session_state.soru_index = 0
    st.session_state.bakiye = 0
    st.session_state.joker_kullanildi = False
    st.session_state.oyun_bitti = False
    random.shuffle(sorular) # Her açılışta sorular karışsın
    st.session_state.sorular = sorular

# Başlık
st.title("🧪 FATOŞ HOCA İLE YARIŞA VAR MISIN?")
st.write("---")

# Oyun Bitti mi?
if st.session_state.soru_index >= len(st.session_state.sorular):
    st.session_state.oyun_bitti = True

if st.session_state.oyun_bitti:
    st.balloons()
    st.success(f"🎉 TEBRİKLER! YARIŞMAYI TAMAMLADINIZ.")
    st.metric("TOPLAM KAZANILAN ÖDÜL", f"{st.session_state.bakiye} TL")
    
    if st.button("TEKRAR OYNA 🔄"):
        st.session_state.soru_index = 0
        st.session_state.bakiye = 0
        st.session_state.joker_kullanildi = False
        st.session_state.oyun_bitti = False
        random.shuffle(sorular)
        st.session_state.sorular = sorular
        st.rerun()

else:
    # Mevcut Soru Verileri
    suanki_soru = st.session_state.sorular[st.session_state.soru_index]
    
    # Bilgi Paneli
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.metric("SORU", f"{st.session_state.soru_index + 1} / {len(sorular)}")
    with col2:
        st.markdown(f"<div class='bilgi-kutusu'>💰 KASA: {st.session_state.bakiye} TL</div>", unsafe_allow_html=True)
    with col3:
        if st.session_state.joker_kullanildi:
            st.warning("Joker Bitti")
        else:
            if st.button("🃏 JOKER"):
                st.session_state.joker_kullanildi = True
                st.toast(f"💡 CEVAP: {suanki_soru['cevap']}", icon="🤫")

    # SORU ALANI
    st.markdown(f"### ❓ {suanki_soru['soru']}")
    st.write("") # Boşluk

    # ŞIKLAR (2x2 Düzen)
    secenekler = suanki_soru['secenekler']
    # Şıkları her seferinde karıştırmak istersen: random.shuffle(secenekler)
    
    c1, c2 = st.columns(2)
    
    # Butonlara tıklanınca ne olacak?
    def cevap_ver(secilen_sik):
        if secilen_sik == suanki_soru['cevap']:
            st.session_state.bakiye += 1000
            st.toast("✅ DOĞRU CEVAP! +1000 TL", icon="🎉")
            time.sleep(1) # Kutlama görünsün diye az bekle
        else:
            st.session_state.bakiye -= 500
            st.toast(f"❌ YANLIŞ! Doğrusu: {suanki_soru['cevap']} (-500 TL)", icon="⚠️")
            time.sleep(2) # Yanlışı görsün diye bekle
        
        # Sonraki soruya geç
        st.session_state.soru_index += 1
        st.rerun()

    with c1:
        if st.button(f"A) {secenekler[0]}"): cevap_ver(secenekler[0])
        st.write("")
        if st.button(f"C) {secenekler[2]}"): cevap_ver(secenekler[2])
        
    with c2:
        if st.button(f"B) {secenekler[1]}"): cevap_ver(secenekler[1])
        st.write("")
        if st.button(f"D) {secenekler[3]}"): cevap_ver(secenekler[3])
