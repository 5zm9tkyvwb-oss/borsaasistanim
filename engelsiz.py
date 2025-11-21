import streamlit as st

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Engelsiz Haklar Rehberi", layout="centered", page_icon="♿")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; color: #333; }
    h1, h2, h3 { color: #2c3e50; text-align: center; }
    .hak-kutu {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #3498db;
    }
    .maas-kutu {
        background-color: #e8f6f3;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #1abc9c;
        text-align: center;
    }
    .uyari-kutu {
        background-color: #fdf2e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e67e22;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("♿ Engelsiz Yaşam ve Haklar Rehberi")
st.caption("Engel oranınıza göre devletin sağladığı tüm hakları anında öğrenin.")

# --- SABİT DEĞERLER (2024-2025 Tahmini Güncel Rakamlar) ---
# Not: Bu rakamlar asgari ücret değiştikçe güncellenmelidir.
NET_ASGARI_UCRET = 17002  # TL (Varsayılan)
MUHTAC_SINIRI = NET_ASGARI_UCRET / 3
BAKIM_MUHTAC_SINIRI = (NET_ASGARI_UCRET * 2) / 3

# --- YAN MENÜ: KİŞİSEL BİLGİLER ---
with st.sidebar:
    st.header("📋 Profil Bilgileri")
    
    oran = st.slider("Engel Oranı (%)", 0, 100, 40)
    
    st.write("---")
    st.header("💰 Gelir Testi (Maaş İçin)")
    hane_geliri = st.number_input("Haneye Giren Toplam Aylık Gelir (TL)", value=0, step=500)
    kisi_sayisi = st.number_input("Hanedeki Kişi Sayısı", value=1, min_value=1)
    
    st.write("---")
    rapor_turu = st.checkbox("Raporumda 'Tam Bağımlı' ifadesi var mı?")
    ortopedik = st.checkbox("Engeliniz Ortopedik mi?")

# --- HESAPLAMA MOTORU ---
kisi_basi_gelir = hane_geliri / kisi_sayisi

# --- SEKME SİSTEMİ ---
tab1, tab2, tab3 = st.tabs(["📜 HAKLARIM NELER?", "💸 MAAŞ SORGULA", "🚗 ÖTV & ARAÇ"])

# --- SEKME 1: GENEL HAKLAR ---
with tab1:
    st.header(f"%{oran} Engel Oranı İçin Haklar")
    
    if oran < 40:
        st.warning("⚠️ Yasal olarak engelli haklarından yararlanabilmek için rapor oranının en az **%40** olması gerekmektedir.")
    else:
        st.markdown("""
        <div class="hak-kutu">
            <h4>🚌 Ücretsiz Ulaşım</h4>
            <ul>
                <li>Şehir içi otobüs, metro ve vapurlar <strong>ÜCRETSİZ</strong>.</li>
                <li>Şehirlerarası trenlerde ve YHT'de <strong>ÜCRETSİZ</strong>.</li>
                <li>Şehirlerarası otobüslerde <strong>%30 İNDİRİM</strong>.</li>
                <li>THY uçuşlarında <strong>%20-%25 İNDİRİM</strong>.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="hak-kutu">
            <h4>💧 Fatura İndirimleri</h4>
            <ul>
                <li>Su Faturası: Belediyeye göre değişmekle birlikte genelde <strong>%50 İNDİRİM</strong>.</li>
                <li>Digiturk / Türksat / İnternet: Özel <strong>%25 engelli indirimi</strong> tarifeleri.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="hak-kutu">
            <h4>🏛️ Vergi ve İş Hayatı</h4>
            <ul>
                <li><strong>EKPSS:</strong> Engelli Kamu Personeli Seçme Sınavı'na girme hakkı.</li>
                <li><strong>Erken Emeklilik:</strong> Yıpranma payı ile daha erken emeklilik hakkı.</li>
                <li><strong>Emlak Vergisi:</strong> Tek evi olanlar (200 m² altı) için <strong>MUAFİYET</strong> (Vergi ödemez).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# --- SEKME 2: MAAŞ HESAPLAMA ---
with tab2:
    st.header("Maaş Bağlanabilir mi?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Hane Kişi Başı Geliriniz:\n# {kisi_basi_gelir:.2f} TL")
    with col2:
        st.warning(f"2022 Maaşı İçin Sınır:\n# {MUHTAC_SINIRI:.2f} TL")

    st.divider()

    # 1. 2022 Engelli Aylığı (Kaymakamlık)
    st.subheader("1. Engelli Aylığı (2022 Sayılı Kanun)")
    
    if oran >= 40 and oran < 70:
        if kisi_basi_gelir < MUHTAC_SINIRI:
            st.success("✅ **UYGUN GÖRÜNÜYOR:** Gelir kriteriniz tutuyor. Oranınız %40-69 arası olduğu için **Engelli Aylığı** alabilirsiniz.")
        else:
            st.error("❌ **ALAMAZSINIZ:** Hane kişi başı geliriniz sınırı aştığı için maaş bağlanmaz.")
    elif oran >= 70:
        if kisi_basi_gelir < MUHTAC_SINIRI:
            st.success("✅ **UYGUN GÖRÜNÜYOR:** Gelir kriteriniz tutuyor. Oranınız %70+ olduğu için **Başkasının Yardımı Olmaksızın Hayatını Devam Ettiremez Aylığı** (Daha yüksek tutar) alabilirsiniz.")
        else:
            st.error("❌ **ALAMAZSINIZ:** Gelir kriteri sınırın üzerinde.")
    else:
        st.error("❌ **ALAMAZSINIZ:** Engel oranı %40'ın altında.")

    st.write("")
    
    # 2. Evde Bakım Aylığı
    st.subheader("2. Evde Bakım Maaşı")
    st.caption(f"Bakım Maaşı Gelir Sınırı: {BAKIM_MUHTAC_SINIRI:.2f} TL")
    
    if rapor_turu: # Tam bağımlı ise
        if kisi_basi_gelir < BAKIM_MUHTAC_SINIRI:
             st.success("✅ **UYGUN GÖRÜNÜYOR:** Raporunuz 'Tam Bağımlı' ve geliriniz sınırın altında. Bakıcı maaşı bağlanabilir.")
        else:
             st.error("❌ **ALAMAZSINIZ:** Raporunuz tutuyor ancak hane geliriniz yüksek.")
    else:
        st.warning("⚠️ **RAPOR UYUMSUZ:** Evde bakım maaşı alabilmek için raporda **'Tam Bağımlı'** ifadesi işaretli olmalıdır.")

# --- SEKME 3: ÖTV VE ARAÇ ---
with tab3:
    st.header("🚗 Araç Alımında ÖTV Muafiyeti")
    
    if oran >= 90:
        st.success("""
        ### ✅ ÖTV'siz Araç Alabilirsiniz!
        * Rapor oranınız %90 ve üzeri olduğu için **hiçbir koşul aranmaksızın** ÖTV (Özel Tüketim Vergisi) ödemeden sıfır araç alabilirsiniz.
        * Aracı engelli kişinin kendisi kullanmak zorunda değildir (1. derece yakınları kullanabilir).
        * 5 yıl satmama şartı vardır.
        """)
    elif oran >= 40 and ortopedik:
        st.success("""
        ### ✅ ÖTV İndirimi Alabilirsiniz (Şartlı)
        * Oranınız %90 altı olsa bile, engeliniz **ORTOPEDİK** olduğu için ve aracı hareket ettirici özel tertibat (gaz-fren elle kontrol vb.) gerekiyorsa ÖTV'siz araç alabilirsiniz.
        * **DİKKAT:** Raporunuzda "Sadece hareket ettirici aksamda özel tertibatlı araç kullanması gerekir" ibaresi olmalıdır.
        * Bu aracı sadece **engelli kişinin kendisi** kullanabilir.
        """)
    else:
        st.error("""
        ### ❌ ÖTV Muafiyeti Yok
        * %90 altı oranlarda, eğer engeliniz ortopedik değilse (örneğin işitme, görme, kronik hastalık, zihinsel vb.) maalesef ÖTV indirimli araç alma hakkı bulunmamaktadır.
        """)

    st.info("💡 **MTV Muafiyeti:** ÖTV'siz alınan araçlar için Motorlu Taşıtlar Vergisi (MTV) de ödenmez.")

# --- YASAL UYARI ---
st.divider()
st.markdown("""
<div class="uyari-kutu">
    <strong>⚠️ Yasal Uyarı:</strong> Bu uygulama bilgilendirme amaçlıdır. Maaş ve hak kazanımları için son kararı Sosyal Yardımlaşma ve Dayanışma Vakıfları (SYDV) veya ilgili kurumlar verir.
    Mevzuatlar ve asgari ücret değiştikçe kriterler değişebilir.
</div>
""", unsafe_allow_html=True)
