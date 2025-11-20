import streamlit as st
import yfinance as yf

# Başlık
st.title("Cep Borsa Analizi 📱")

# Giriş Kısmı
hisse = st.text_input("Hisse Kodu", "THYAO").upper()
if ".IS" not in hisse: hisse += ".IS"

if st.button("Analiz Et"):
    try:
        # Veri Çek
        df = yf.download(hisse, period="6mo")
        
        # Veri Hatası Düzeltme (Önemli)
        if hasattr(df.columns, 'levels'): 
            df.columns = df.columns.get_level_values(0)
            
        if not df.empty:
            # Hesaplamalar
            son_fiyat = df['Close'].iloc[-1]
            ort = df['Close'].rolling(20).mean().iloc[-1]
            sapma = df['Close'].rolling(20).std().iloc[-1]
            
            destek = ort - (2 * sapma)
            direnc = ort + (2 * sapma)
            
            # Ekrana Yaz
            st.metric("FİYAT", f"{son_fiyat:.2f} TL")
            st.metric("ALIM YERİ (Destek)", f"{destek:.2f} TL")
            st.metric("SATIM YERİ (Direnç)", f"{direnc:.2f} TL")
            
            # Grafik
            st.line_chart(df['Close'])
            
            # Basit Yorum
            if son_fiyat < destek * 1.03:
                st.success("✅ HİSSE UCUZLADI (ALIM FIRSATI OLABİLİR)")
            elif son_fiyat > direnc * 0.97:
                st.error("🔻 HİSSE PAHALI (SATIŞ GELEBİLİR)")
            else:
                st.info("⏸️ HİSSE YATAY SEYİRDE (BEKLE)")
                
        else:
            st.error("Hisse bulunamadı!")
            
    except Exception as e:
        st.error(f"Hata: {e}")
