import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- SAYFA AYARLARI (Dark & Whale Tema) ---
st.set_page_config(page_title="BIST Balina Avcısı", layout="wide", page_icon="🐳")

# Özel CSS (O ekran görüntüsündeki gibi havalı olsun)
st.markdown("""
    <style>
    .stApp {
        background-color: #0a0e17;
        color: white;
    }
    .stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    h1, h2, h3 {
        color: #38bdf8 !important; /* Parlak Mavi */
    }
    .balina-karti {
        background: linear-gradient(90deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #38bdf8;
        margin-bottom: 10px;
    }
    .signal-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .buy { background-color: #059669; color: white; }
    .sell { background-color: #dc2626; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- BAŞLIK ---
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("# 🐳")
with col2:
    st.title("BIST Balina Avcısı (Whale Hunter)")
    st.caption("Yapay Zeka Destekli Hacim ve Momentum Tarayıcısı")

# --- HİSSE LİSTESİ (BIST 30'dan bazıları + HDFGS) ---
hisseler = [
    "HDFGS.IS", "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", 
    "EREGL.IS", "KCHOL.IS", "AKBNK.IS", "TUPRS.IS", "SASA.IS", 
    "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS"
]

# --- BALİNA TARAMA MOTORU ---
def balina_tara():
    sinyaller = []
    
    my_bar = st.progress(0)
    step = 1.0 / len(hisseler)
    current_step = 0.0

    for symbol in hisseler:
        try:
            # Son 5 günlük veriyi çek (Saatlik bazda)
            df = yf.download(symbol, period="5d", interval="1h", progress=False)
            
            if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
            
            if len(df) > 20:
                son_mum = df.iloc[-1]
                
                # 1. HACİM ANALİZİ (Balina Tespiti)
                son_hacim = son_mum['Volume']
                ort_hacim = df['Volume'].rolling(20).mean().iloc[-1] # 20 saatlik ortalama
                
                hacim_kati = son_hacim / ort_hacim if ort_hacim > 0 else 0
                
                # 2. FİYAT ANALİZİ
                fiyat = son_mum['Close']
                degisim = ((fiyat - df['Open'].iloc[-1]) / df['Open'].iloc[-1]) * 100
                
                # 3. RSI (Momentum)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs)).iloc[-1]

                # --- SİNYAL ALGORİTMASI ---
                durum = "NÖTR"
                renk = "gray"
                sebep = ""

                # Kural: Hacim 2 katına çıkmışsa VE Fiyat Artıyorsa -> BALİNA GİRDİ
                if hacim_kati > 2.0 and degisim > 0:
                    durum = "WHALE BUY 🚀"
                    renk = "buy"
                    sebep = f"Hacim Patlaması ({hacim_kati:.1f}x)"
                
                # Kural: Hacim patlamış ama Fiyat Düşüyorsa -> BALİNA SATIYOR
                elif hacim_kati > 2.0 and degisim < 0:
                    durum = "WHALE DUMP 🔻"
                    renk = "sell"
                    sebep = f"Panik Satış ({hacim_kati:.1f}x)"
                
                # Kural: RSI Dipteyse
                elif rsi < 30:
                    durum = "DİP ALIMI 🌱"
                    renk = "buy"
                    sebep = "Aşırı Ucuz (RSI < 30)"

                if durum != "NÖTR":
                    sinyaller.append({
                        "Hisse": symbol.replace(".IS", ""),
                        "Fiyat": fiyat,
                        "Değişim": degisim,
                        "Hacim_Katı": hacim_kati,
                        "Sinyal": durum,
                        "Renk": renk,
                        "Sebep": sebep
                    })
        except:
            pass
        
        current_step += step
        my_bar.progress(min(current_step, 1.0))
    
    my_bar.empty()
    return sinyaller

# --- ARAYÜZ ---

if st.button("RADARI ÇALIŞTIR 📡", type="primary"):
    with st.spinner('Okyanus taranıyor... Balinalar aranıyor...'):
        sonuclar = balina_tara()
        
        if len(sonuclar) > 0:
            st.success(f"Radar {len(sonuclar)} adet sinyal yakaladı!")
            
            for veri in sonuclar:
                # HTML Kart Tasarımı
                html_kod = f"""
                <div class="balina-karti">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h2 style="margin:0; color:white;">{veri['Hisse']}</h2>
                            <p style="margin:0; font-size:18px;">{veri['Fiyat']:.2f} TL <span style="color:{'#4ade80' if veri['Değişim']>0 else '#f87171'}">(%{veri['Değişim']:.2f})</span></p>
                        </div>
                        <div style="text-align:right;">
                            <div class="signal-box {veri['Renk']}">{veri['Sinyal']}</div>
                            <p style="margin:5px 0 0 0; font-size:12px; color:#cbd5e1;">{veri['Sebep']}</p>
                        </div>
                    </div>
                </div>
                """
                st.markdown(html_kod, unsafe_allow_html=True)
        else:
            st.info("Şu an deniz sakin. Herhangi bir balina hareketi (Hacim patlaması) görülmedi.")

# --- BİLGİ KUTUSU ---
with st.sidebar:
    st.header("Nasıl Çalışır?")
    st.info("""
    **1. Hacim Analizi:**
    Son 20 saatin ortalamasına bakar. Eğer anlık hacim, ortalamanın 2 katına çıkarsa 'Balina' var demektir.
    
    **2. Whale Buy (Alım):**
    Hacim yüksek + Fiyat Yükseliyorsa = Biri topluyor.
    
    **3. Whale Dump (Satış):**
    Hacim yüksek + Fiyat Düşüyorsa = Biri mal boşaltıyor.
    """)
    st.warning("Not: Veriler 15dk gecikmeli olabilir.")
