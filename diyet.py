import streamlit as st
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Diyetisyen Pro", page_icon="🥑", layout="centered")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #fdfbf7; color: #2c3e50; }
    h1 { color: #27ae60; text-align: center; font-family: 'Helvetica', sans-serif; }
    
    /* Buton */
    .stButton>button {
        width: 100%;
        background: linear-gradient(to right, #11998e, #38ef7d);
        color: white;
        border-radius: 12px;
        height: 55px;
        font-size: 20px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover { transform: scale(1.02); }
    
    /* Sonuç Kartları */
    .menu-karti {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 8px solid #f39c12; /* Turuncu Sabah */
        margin-bottom: 15px;
    }
    .ogle { border-left-color: #27ae60; } /* Yeşil Öğle */
    .aksam { border-left-color: #2980b9; } /* Mavi Akşam */
    .ara { border-left-color: #8e44ad; } /* Mor Ara */
    
    .baslik { font-size: 18px; font-weight: bold; color: #555; margin-bottom: 5px; }
    .vitamin-notu { font-size: 12px; color: #e74c3c; font-style: italic; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🥑 AI Beslenme & Vitamin Uzmanı")
st.caption("Alerji, Vitamin ve Kalori Odaklı Akıllı Planlayıcı")

# --- KULLANICI GİRİŞİ ---
with st.expander("📋 KİŞİSEL BİLGİLERİNİZ", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        yas = st.number_input("Yaş", 10, 90, 30)
        boy = st.number_input("Boy (cm)", 100, 230, 175)
        kilo = st.number_input("Kilo (kg)", 30, 200, 80)
    with col2:
        cinsiyet = st.selectbox("Cinsiyet", ["Erkek", "Kadın"])
        aktivite = st.selectbox("Hareket", ["Hareketsiz", "Az Hareketli", "Aktif", "Sporcu"])
        hedef = st.selectbox("Hedef", ["Kilo Vermek", "Kilo Almak", "Form Korumak"])

st.divider()

col3, col4 = st.columns(2)
with col3:
    st.subheader("🚫 Alerji & Hassasiyet")
    alerjiler = st.multiselect("Uzak durduklarınız:", 
                               ["Gluten (Ekmek/Makarna)", "Laktoz (Süt/Yoğurt)", "Yumurta", "Kuruyemiş", "Deniz Ürünleri"])

with col4:
    st.subheader("💊 Vitamin Odağı")
    vitamin_hedefi = st.selectbox("Neye İhtiyacın Var?", 
                                  ["Genel Sağlık", "Enerji & Zindelik (B12, Demir)", "Bağışıklık Güçlendirici (C Vit, Çinko)", "Kemik & Eklem (Kalsiyum)"])

# --- HESAPLAMA MOTORU ---
def hesapla():
    # BMR Hesapla
    bmr = (10 * kilo) + (6.25 * boy) - (5 * yas) + (5 if cinsiyet == "Erkek" else -161)
    
    # Aktivite
    carpan = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Aktif": 1.55, "Sporcu": 1.725}
    gunluk = bmr * carpan[aktivite]
    
    # Hedef
    if hedef == "Kilo Vermek": hedef_kal = gunluk - 500
    elif hedef == "Kilo Almak": hedef_kal = gunluk + 400
    else: hedef_kal = gunluk
    
    return int(hedef_kal)

# --- MENÜ OLUŞTURUCU (Algoritmik Zeka) ---
def menu_hazirla(kalori, alerji_list, vitamin_tipi):
    # 1. STANDART İSKELET MENÜ
    sabah = "2 Adet Haşlanmış Yumurta, 1 Dilim Ezine Peyniri, Bol Yeşillik, 1 Dilim Tam Buğday Ekmeği."
    ogle = "120g Izgara Tavuk Göğsü, 4 Yemek Kaşığı Bulgur Pilavı, 1 Kase Yoğurt, Mevsim Salata."
    aksam = "8 Yemek Kaşığı Zeytinyağlı Sebze Yemeği (Susuz), 1 Kase Cacık, 1 Dilim Tam Buğday Ekmeği."
    ara = "1 Adet Yeşil Elma + 10 Adet Çiğ Badem."
    
    # 2. ALERJİ FİLTRESİ (Yer Değiştirme)
    if "Gluten (Ekmek/Makarna)" in alerji_list:
        sabah = sabah.replace("Tam Buğday Ekmeği", "Karabuğday Patlağı veya Glutensiz Ekmek")
        aksam = aksam.replace("Tam Buğday Ekmeği", "Ekstra Salata")
        ogle = ogle.replace("Bulgur Pilavı", "Kinoa veya Karabuğday")
        
    if "Laktoz (Süt/Yoğurt)" in alerji_list:
        sabah = sabah.replace("Ezine Peyniri", "Yarım Avokado (Sağlıklı Yağ)")
        ogle = ogle.replace("Yoğurt", "Söğüş Domates/Salatalık")
        aksam = aksam.replace("Cacık", "Bol Limonlu Roka Salatası")
        
    if "Yumurta" in alerji_list:
        sabah = sabah.replace("2 Adet Haşlanmış Yumurta", "3 Kaşık Lor Peyniri + 2 Ceviz")
        
    if "Kuruyemiş" in alerji_list:
        ara = ara.replace("10 Adet Çiğ Badem", "1 Bardak Kefir/Süt")
        
    if "Deniz Ürünleri" in alerji_list:
        # Akşam menüsü balık gelirse diye önlem (Şu an sebze ama çeşitlendirebiliriz)
        pass 

    # 3. VİTAMİN GÜÇLENDİRİCİ (Booster)
    vitamin_notu = ""
    if vitamin_tipi == "Enerji & Zindelik (B12, Demir)":
        sabah += " (Üzerine Limon Sıkılmış Maydanoz ekle - Demir emilimi için)"
        ogle = ogle.replace("Tavuk Göğsü", "Izgara Köfte/Et (Demir Deposu)")
        vitamin_notu = "⚡ Enerji için Kırmızı Et ve C Vitamini (Limon) birleştirildi."
        
    elif vitamin_tipi == "Bağışıklık Güçlendirici (C Vit, Çinko)":
        ara += " + 1 Adet Kivi (C Vitamini Deposu)"
        sabah += " + 1 Adet Kırmızı Kapya Biber"
        vitamin_notu = "🛡️ Bağışıklık için menüye Kivi ve Biber eklendi."
        
    elif vitamin_tipi == "Kemik & Eklem (Kalsiyum)":
        if "Laktoz (Süt/Yoğurt)" not in alerji_list:
            ara = ara.replace("Yeşil Elma", "1 Bardak Süt + Muz")
            aksam += " (Yoğurduna keten tohumu ekle)"
        else:
            aksam += " (Bol Brokoli/Ispanak ekle - Bitkisel Kalsiyum)"
        vitamin_notu = "🦴 Kemikler için Kalsiyum artırıldı."

    # 4. KALORİ AYARI (Ara Öğün Yönetimi)
    ara_ogun_var = True
    if kalori < 1500:
        ara_ogun_var = False # Düşük kaloride ara öğünü kaldır
        vitamin_notu += " (Düşük kalori hedefi için ara öğün çıkarıldı)"
    elif kalori > 2500:
        ara += " + 1 Dilim Peynir + Galeta" # Yüksek kaloride ekle

    return sabah, ogle, aksam, ara, ara_ogun_var, vitamin_notu

# --- İŞLEM ---
if st.button("ANALİZ ET VE MENÜYÜ OLUŞTUR 🚀"):
    with st.spinner("Vücut analizi yapılıyor ve menü hazırlanıyor..."):
        time.sleep(1.5)
        
        hedef_kal = hesapla()
        sabah, ogle, aksam, ara, ara_var, notu = menu_hazirla(hedef_kal, alerjiler, vitamin_hedefi)
        
        # SONUÇLAR
        st.success(f"✅ Plan Oluşturuldu! Günlük Hedef: **{hedef_kal} kcal**")
        
        if notu:
            st.info(notu)
        
        st.markdown(f"""
        <div class="menu-karti">
            <div class="baslik">🍳 SABAH (Kahvaltı)</div>
            {sabah}
        </div>
        
        <div class="menu-karti ogle">
            <div class="baslik">🍗 ÖĞLE</div>
            {ogle}
        </div>
        """, unsafe_allow_html=True)
        
        if ara_var:
            st.markdown(f"""
            <div class="menu-karti ara">
                <div class="baslik">🍏 ARA ÖĞÜN</div>
                {ara}
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class="menu-karti aksam">
            <div class="baslik">🥗 AKŞAM</div>
            {aksam}
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("⚠️ Önemli: Günde en az 2.5 - 3 Litre su içmeyi unutmayın!")
