import streamlit as st
from gtts import gTTS
from io import BytesIO
from PIL import Image

# --- SESLİ OKUMA MOTORU (RAM TABANLI - HIZLI) ---
def metni_oku(metin):
    """Metni dosyaya kaydetmeden direkt hafızadan okur"""
    try:
        # Sesi oluştur
        tts = gTTS(text=metin, lang='tr')
        
        # Hafızada bir dosya gibi tut (BytesIO)
        ses_verisi = BytesIO()
        tts.write_to_fp(ses_verisi)
        
        # Oynatıcıyı göster
        st.audio(ses_verisi, format='audio/mp3')
        
    except Exception as e:
        st.error(f"Ses motorunda hata oluştu: {e}")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Engelsiz Asistan Pro", page_icon="🦮", layout="centered")

# --- YÜKSEK KONTRAST TASARIM ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFD700; }
    h1, h2, h3, p, label, .stMarkdown, .stRadio label { color: #FFD700 !important; font-family: sans-serif; font-weight: bold; }
    
    /* Butonlar */
    .stButton>button {
        width: 100%;
        height: 70px;
        background-color: #FFD700;
        color: black;
        font-size: 22px;
        font-weight: bold;
        border: 3px solid white;
        border-radius: 12px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
        border-color: #FFD700;
    }
    
    /* Ses Oynatıcıyı Görünür Yap */
    audio { width: 100%; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🦮 ENGELSİZ ASİSTAN")
st.info("Lütfen telefonunuzun sesini açın ve 'Sessiz Mod' anahtarını kontrol edin.")

# --- MENÜ ---
secim = st.radio("MOD SEÇİN:", ["📸 FOTOĞRAF ANLAT", "📜 HAKLARI OKU", "🆘 ACİL DURUM"])

st.write("---")

# --- MODÜL 1: AI GÖZ ---
if secim == "📸 FOTOĞRAF ANLAT":
    st.header("Ne Gördüğümü Anlat")
    
    uploaded_file = st.file_uploader("Fotoğraf Çek / Yükle", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        if st.button("SESLİ ANLAT 🔊"):
            with st.spinner('Görüntü inceleniyor...'):
                # Simülasyon Cevabı
                cevap = "Bu fotoğrafta bir ilaç kutusu görünüyor. Üzerinde 'Ağrı Kesici' yazıyor. Günde 2 defa tok karna içilmesi önerilir."
                
                st.success(f"🗣️ {cevap}")
                metni_oku(cevap)

# --- MODÜL 2: HAKLAR ---
elif secim == "📜 HAKLARI OKU":
    st.header("Haklarını Dinle")
    
    konu = st.selectbox("Konu Seç:", 
                        ["ÖTV İndirimi", "Engelli Maaşı", "Ücretsiz Ulaşım", "Su İndirimi"])
    
    metin = ""
    if konu == "ÖTV İndirimi":
        metin = "Yüzde 90 ve üzeri raporunuz varsa, ÖTV ödemeden araba alabilirsiniz. Eğer engeliniz ortopedik ise oran şartı aranmaz, özel tertibatlı araç alabilirsiniz."
    elif konu == "Engelli Maaşı":
        metin = "Engelli maaşı alabilmek için, hanedeki kişi başına düşen gelirin asgari ücretin üçte birinden az olması gerekir."
    elif konu == "Ücretsiz Ulaşım":
        metin = "Şehir içi otobüs, metro ve vapurlara ücretsiz binebilirsiniz. Şehirler arası trenlerde de ücret ödemezsiniz."
    elif konu == "Su İndirimi":
        metin = "Belediyelerin çoğunda su faturalarında yüzde 50 indirim hakkınız vardır. Su idaresine raporunuzla başvurmalısınız."
        
    st.info(metin)
    
    if st.button("SESLİ OKU 🔊"):
        metni_oku(metin)

# --- MODÜL 3: ACİL DURUM ---
elif secim == "🆘 ACİL DURUM":
    st.header("YARDIM BUTONU")
    
    if st.button("🚨 YARDIM ÇAĞIR (DEMO)"):
        st.error("YARDIM SİNYALİ GÖNDERİLDİ!")
        metni_oku("Dikkat! Acil durum sinyali gönderildi. Konumunuz paylaşılıyor. Lütfen sakin olun, yardım yolda.")
