import streamlit as st
from gtts import gTTS
import os
from PIL import Image

# --- SESLİ OKUMA FONKSİYONU ---
def metni_oku(metin):
    """Metni sese çevirir ve oynatır"""
    try:
        tts = gTTS(text=metin, lang='tr')
        tts.save("ses.mp3")
        st.audio("ses.mp3", format="audio/mp3")
    except Exception as e:
        st.error("Ses oluşturulurken hata oluştu.")

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Engelsiz Asistan Pro", page_icon="🦮", layout="centered")

# --- YÜKSEK KONTRAST TASARIM (Sarı/Siyah - Az Görenler İçin) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFD700; }
    h1, h2, h3, p, label, .stMarkdown { color: #FFD700 !important; font-family: sans-serif; }
    .stButton>button {
        width: 100%;
        height: 80px;
        background-color: #FFD700;
        color: black;
        font-size: 24px;
        font-weight: bold;
        border: 3px solid white;
        border-radius: 15px;
    }
    .stButton>button:hover {
        background-color: white;
        color: black;
    }
    .stTextInput>div>div>input { font-size: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🦮 ENGELSİZ ASİSTAN PRO")
st.write("Görme ve Okuma Zorluğu Çekenler İçin Yapay Zeka Desteği")

# --- MENÜ ---
secim = st.radio("Ne Yapmak İstersin?", ["📸 Fotoğrafı Anlat (AI Göz)", "📜 Haklarımı Sesli Oku", "🆘 Acil Durum"], horizontal=True)

# --- MODÜL 1: AI GÖZ (Fotoğraf Analizi) ---
if secim == "📸 Fotoğrafı Anlat (AI Göz)":
    st.header("Ne Gördüğümü Anlat")
    st.info("Bir ilaç kutusu, fatura veya önünüzdeki manzaranın fotoğrafını yükleyin.")
    
    uploaded_file = st.file_uploader("Fotoğraf Seçin...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Yüklenen Fotoğraf', use_column_width=True)
        
        if st.button("BU NEDİR? (SESLİ ANLAT) 🔊"):
            with st.spinner('Görüntü inceleniyor...'):
                # BURADA NORMALDE OPENAI VISION API KULLANILIR
                # Şimdilik simülasyon yapıyoruz (Demo olduğu için)
                
                ornek_cevap = "Bu fotoğrafta bir ilaç kutusu görünüyor. Üzerinde 'Parol' yazıyor. Ağrı kesici ve ateş düşürücü olarak kullanılır. Günde 2 tabletten fazla alınmaması öneriliyor."
                
                st.success("Analiz Tamamlandı:")
                st.write(f"🗣️ **Asistan:** {ornek_cevap}")
                metni_oku(ornek_cevap)

# --- MODÜL 2: HAKLARI SESLİ OKU ---
elif secim == "📜 Haklarımı Sesli Oku":
    st.header("Haklarınızı Dinleyin")
    
    konu = st.selectbox("Hangi Konuyu Merak Ediyorsun?", 
                        ["ÖTV İndirimi", "Engelli Maaşı", "Ücretsiz Ulaşım", "Su İndirimi"])
    
    bilgi_metni = ""
    if konu == "ÖTV İndirimi":
        bilgi_metni = "Yüzde 90 ve üzeri raporunuz varsa, ÖTV ödemeden araba alabilirsiniz. Eğer engeliniz ortopedik ise oran şartı aranmaz, özel tertibatlı araç alabilirsiniz."
    elif konu == "Engelli Maaşı":
        bilgi_metni = "Engelli maaşı alabilmek için, hanedeki kişi başına düşen gelirin asgari ücretin üçte birinden az olması gerekir. Rapor oranınız en az yüzde 40 olmalıdır."
    elif konu == "Ücretsiz Ulaşım":
        bilgi_metni = "Şehir içi otobüs, metro ve vapurlara ücretsiz binebilirsiniz. Şehirler arası trenlerde de ücret ödemezsiniz."
    elif konu == "Su İndirimi":
        bilgi_metni = "Belediyelerin çoğunda su faturalarında yüzde 50 indirim hakkınız vardır. Bunun için su idaresine raporunuzla başvurmalısınız."
        
    st.info(bilgi_metni)
    
    if st.button("🔊 SESLİ OKU"):
        metni_oku(bilgi_metni)

# --- MODÜL 3: ACİL DURUM ---
elif secim == "🆘 Acil Durum":
    st.header("Acil Durum Butonu")
    st.warning("Bu butona basarsanız ekran kırmızı yanıp söner ve sesli uyarı verir (Demo).")
    
    if st.button("🚨 YARDIM ÇAĞIR"):
        st.markdown("""
            <style>
            .stApp { animation: blinker 1s linear infinite; background-color: red; }
            @keyframes blinker { 50% { opacity: 0.5; } }
            </style>
            <h1 style='text-align:center; font-size:100px;'>YARDIM EDİN!</h1>
        """, unsafe_allow_html=True)
        metni_oku("Acil durum! Lütfen yardım edin! Konumum paylaşılıyor.")

# --- ALT BİLGİ ---
st.write("---")
st.caption("Bu uygulama Engelsiz Yaşam için geliştirilmiştir.")
