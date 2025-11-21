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
    sabah = "2 Haşlanmış Yumurta, 1 dilim peynir, 5 zeytin, yeşillik, 1 dilim tam buğday ekmeği."
    ogle = "1 porsiyon ızgara tavuk/köfte (150g), bol salata, 1 kase yoğurt."
    ara = "1 porsiyon meyve (Elma/Muz) + 10 adet çiğ badem."
    aksam = "8 yemek kaşığı sebze yemeği (susuz), 1 kase cacık, 1 dilim ekmek."
    
    # Tercihlere Göre Değiştir (Yapay Zeka Taklidi)
    if "Yumurta" in tercihler:
        sabah = "2 dilim beyaz peynir, 2 ceviz, bol domates/salatalık, 1 dilim ekmek (Yumurta yerine)."
    if "Et/Tavuk" in tercihler:
        ogle = "1 kase mercimek çorbası veya kurubaklagil yemeği, bol salata, yoğurt."
    if "Süt/Peynir" in tercihler:
        ogle = ogle.replace(", 1 kase yoğurt", "")
        sabah = sabah.replace("1 dilim peynir", "5-6 adet zeytin daha ekle")
    if "Gluten/Ekmek" in tercihler:
        sabah = sabah.replace("1 dilim tam buğday ekmeği", "1 avuç ceviz/badem")
        aksam = aksam.replace("1 dilim ekmek", "Ekstra salata")

    # Kaloriye Göre Porsiyon Ayarı
    if kalori > 2500:
        sabah += " + 1 kase yulaf lapası."
        aksam += " + 1 kase çorba."
    elif kalori < 1500:
        aksam = "1 kase çorba ve bol salata (Hafif Akşam)."
        ara = "1 adet yeşil elma."

    return sabah, ogle, ara, aksam

# --- BUTON ---
if st.button("ANALİZ ET VE LİSTE OLUŞTUR 🚀"):
    with st.spinner('Vücut verilerin işleniyor...'):
        time.sleep(1.5) # Hesaplama efekti
        
        kalori, vki, durum = hesapla_ve_olustur()
        sabah, ogle, ara, aksam = liste_yaz(kalori, ozel_tercih)
        
        # SONUÇLARI GÖSTER
        st.success("✅ Analiz Tamamlandı!")
        
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='bilgi-karti'>VKİ: {vki:.1f}<br>({durum})</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='bilgi-karti'>Günlük Alman Gereken:<br>{kalori} kcal</div>", unsafe_allow_html=True)
        
        # LİSTE KUTUSU
        st.markdown(f"""
        <div class='sonuc-kutusu'>
            <h3 style='text-align:center; color:#27ae60;'>Sana Özel 1 Günlük Örnek Menü</h3>
            <div class='ogun-baslik'>🍳 SABAH</div>
            {sabah}
            
            <div class='ogun-baslik'>🍗 ÖĞLE</div>
            {ogle}
            
            <div class='ogun-baslik'>🍏 ARA ÖĞÜN</div>
            {ara}
            
            <div class='ogun-baslik'>🥗 AKŞAM</div>
            {aksam}
            
            <hr>
            <small>Not: Bu liste otomatik oluşturulmuştur. Lütfen doktorunuza danışmadan uygulamayın. 
            Günde en az 2.5 litre su içmeyi unutma! 💧</small>
        </div>
        """, unsafe_allow_html=True)
