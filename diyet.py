import streamlit as st
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Akıllı Diyetisyen (Ücretsiz)", page_icon="🥗", layout="centered")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f9f4; color: #2c3e50; }
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
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 6px solid #27ae60;
        margin-top: 20px;
    }
    .bilgi-karti {
        background-color: #e8f8f5;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: #16a085;
        margin-bottom: 10px;
    }
    .ogun-baslik {
        color: #d35400;
        font-size: 20px;
        font-weight: bold;
        margin-top: 15px;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🥗 Akıllı Diyetisyen")
st.caption("Yapay Zeka Yok, Saf Bilim Var. (Anahtar Gerektirmez)")

# --- KULLANICI BİLGİLERİ ---
col1, col2 = st.columns(2)
with col1:
    yas = st.number_input("Yaşınız", 10, 90, 25)
    boy = st.number_input("Boyunuz (cm)", 100, 250, 175)
    kilo = st.number_input("Kilonuz (kg)", 30, 200, 70)

with col2:
    cinsiyet = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
    aktivite = st.selectbox("Hareket Seviyesi", ["Hareketsiz (Masa başı)", "Az Hareketli (Haftada 1-2)", "Aktif (Haftada 3-5)", "Sporcu"])
    hedef = st.selectbox("Hedefiniz", ["Kilo Vermek", "Kilo Almak", "Formu Korumak"])

ozel_tercih = st.multiselect("Neleri Yemezsin?", ["Yumurta", "Süt/Peynir", "Et/Tavuk", "Gluten/Ekmek"])

# --- HESAPLAMA MOTORU ---
def hesapla_ve_olustur():
    # 1. Bazal Metabolizma (Mifflin-St Jeor)
    if cinsiyet == "Erkek":
        bmr = (10 * kilo) + (6.25 * boy) - (5 * yas) + 5
    else:
        bmr = (10 * kilo) + (6.25 * boy) - (5 * yas) - 161
    
    # 2. Aktivite Çarpanı
    carpanlar = {"Hareketsiz (Masa başı)": 1.2, "Az Hareketli (Haftada 1-2)": 1.375, "Aktif (Haftada 3-5)": 1.55, "Sporcu": 1.725}
    gunluk_kalori = bmr * carpanlar[aktivite]
    
    # 3. Hedef Ayarı
    if hedef == "Kilo Vermek": hedef_kalori = gunluk_kalori - 500
    elif hedef == "Kilo Almak": hedef_kalori = gunluk_kalori + 400
    else: hedef_kalori = gunluk_kalori
    
    # 4. VKİ
    vki = kilo / ((boy/100)**2)
    vki_durum = "Normal"
    if vki > 25: vki_durum = "Fazla Kilolu"
    elif vki > 30: vki_durum = "Obez"
    elif vki < 18.5: vki_durum = "Zayıf"

    return int(hedef_kalori), vki, vki_durum

# --- DİYET LİSTESİ OLUŞTURUCU (Algoritmik) ---
def liste_yaz(kalori, tercihler):
    sabah = "2 Haşlanmış Yumurta, 1 dilim peynir, 5 zeytin, yeşillik, 1 dilim tam buğday ek
