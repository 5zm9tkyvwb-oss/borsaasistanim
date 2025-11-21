import streamlit as st
from openai import OpenAI

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Diyetisyenim", page_icon="🥗", layout="centered")

# --- CSS TASARIMI (Yeşil/Sağlıklı Tema) ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfbf7; color: #2c3e50; }
    h1 { color: #27ae60; text-align: center; font-family: 'Helvetica', sans-serif; }
    .stButton>button {
        width: 100%;
        background-color: #27ae60;
        color: white;
        border-radius: 10px;
        height: 50px;
        font-size: 18px;
        border: none;
    }
    .stButton>button:hover { background-color: #219150; }
    .sonuc-kutusu {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #27ae60;
        margin-top: 20px;
    }
    .vki-kutusu {
        text-align: center;
        padding: 10px;
        background-color: #e8f8f5;
        border-radius: 10px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #16a085;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥗 AI Diyetisyenim")
st.caption("Sana özel, bilimsel ve yapay zeka destekli beslenme programı.")

# --- YAN MENÜ (API KEY) ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    openai_api_key = st.text_input("OpenAI API Anahtarı", type="password", help="ChatGPT anahtarını buraya yapıştır.")
    st.info("Anahtarın yoksa sadece VKİ hesaplanır, diyet listesi oluşturulamaz.")

# --- KULLANICI BİLGİLERİ ---
col1, col2 = st.columns(2)
with col1:
    yas = st.number_input("Yaşınız", 10, 90, 25)
    boy = st.number_input("Boyunuz (cm)", 100, 250, 175)
    kilo = st.number_input("Kilonuz (kg)", 30, 200, 70)

with col2:
    cinsiyet = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
    aktivite = st.selectbox("Hareket Seviyesi", ["Hareketsiz (Masa başı)", "Az Hareketli (Haftada 1-2 spor)", "Aktif (Haftada 3-5 spor)", "Çok Aktif (Sporcu)"])
    hedef = st.selectbox("Hedefiniz Nedir?", ["Kilo Vermek", "Kilo Almak", "Kilomu Korumak"])

ozel_durum = st.text_area("Özel Durumlar (İsteğe Bağlı)", placeholder="Örn: Yumurta sevmem, Glutensiz besleniyorum, Şeker hastasıyım...")

# --- HESAPLAMA MOTORU ---
def vki_hesapla(kilo, boy):
    boy_m = boy / 100
    vki = kilo / (boy_m * boy_m)
    if vki < 18.5: durum = "Zayıf"
    elif vki < 25: durum = "Normal"
    elif vki < 30: durum = "Fazla Kilolu"
    else: durum = "Obez"
    return vki, durum

def kalori_hesapla(cinsiyet, kilo, boy, yas, aktivite):
    # Harris-Benedict Formülü
    if cinsiyet == "Erkek":
        bmr = 88.36 + (13.4 * kilo) + (4.8 * boy) - (5.7 * yas)
    else:
        bmr = 447.6 + (9.2 * kilo) + (3.1 * boy) - (4.3 * yas)
    
    # Aktivite Çarpanı
    carpanlar = {
        "Hareketsiz (Masa başı)": 1.2,
        "Az Hareketli (Haftada 1-2 spor)": 1.375,
        "Aktif (Haftada 3-5 spor)": 1.55,
        "Çok Aktif (Sporcu)": 1.725
    }
    
    gunluk_kalori = bmr * carpanlar[aktivite]
    return int(gunluk_kalori)

# --- BUTON VE İŞLEM ---
if st.button("Diyet Listemi Oluştur 📝"):
    # 1. Temel Hesaplamalar
    vki, durum = vki_hesapla(kilo, boy)
    bazal_kalori = kalori_hesapla(cinsiyet, kilo, boy, yas, aktivite)
    
    # Hedefe Göre Kalori Ayarı
    hedef_kalori = bazal_kalori
    if hedef == "Kilo Vermek":
        hedef_kalori -= 500 # Açık oluştur
    elif hedef == "Kilo Almak":
        hedef_kalori += 400 # Fazla al
        
    # Ekrana Yazdır
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"<div class='vki-kutusu'>Vücut Kitle İndeksi: {vki:.1f}<br>({durum})</div>", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"<div class='vki-kutusu'>Günlük Hedef Kalori:<br>{hedef_kalori} kcal</div>", unsafe_allow_html=True)

    # 2. Yapay Zeka Diyet Listesi
    if not openai_api_key:
        st.warning("⚠️ Yapay zeka listesi için sol menüden API anahtarı girmelisiniz. Yukarıdaki veriler matematiksel hesaptır.")
    else:
        try:
            client = OpenAI(api_key=openai_api_key)
            
            prompt = f"""
            Sen uzman bir diyetisyensin. Aşağıdaki kişiye özel 1 günlük örnek diyet listesi hazırla.
            
            Kişi Bilgileri:
            - Yaş: {yas}, Cinsiyet: {cinsiyet}, Kilo: {kilo}, Boy: {boy}
            - Hedef: {hedef} (Günlük alması gereken kalori yaklaşık {hedef_kalori} kcal olmalı)
            - Özel Durumlar/Tercihler: {ozel_durum if ozel_durum else "Yok"}
            
            Lütfen çıktıyı şu formatta ver:
            1. **Sabah:** (Menü ve yaklaşık kalori)
            2. **Ara Öğün:** (Opsiyonel)
            3. **Öğle:** (Menü ve yaklaşık kalori)
            4. **Ara Öğün:**
            5. **Akşam:**
            
            En alta da bu kişiye 3 tane önemli beslenme tavsiyesi ekle. Samimi ve motive edici bir dil kullan.
            """
            
            with st.spinner('Yapay zeka sana özel menüyü hazırlıyor... 🍳'):
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                diyet_listesi = response.choices[0].message.content
                
                st.markdown(f"<div class='sonuc-kutusu'>{diyet_listesi}</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
