import streamlit as st
import yfinance as yf
import pandas as pd
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="BIST Pro Analiz", layout="wide", page_icon="📊")

# --- CSS TASARIMI ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Kart Tasarımı */
    .analiz-karti {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #374151;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .hdfgs-ozel { border: 2px solid #FFD700; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2); }
    
    /* Etiketler */
    .etiket {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 5px;
    }
    .yukselir { background-color: #065f46; color: #34d399; border: 1px solid #34d399; }
    .duser { background-color: #7f1d1d; color: #f87171; border: 1px solid #f87171; }
    .notr { background-color: #374151; color: #9ca3af; }
    
    /* Para Barı */
    .para-bar-bg { width: 100%; height: 10px; background-color: #374151; border-radius: 5px; margin-top: 8px; overflow: hidden; }
    .para-bar-doluluk { height: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 AYLIK POPÜLER HİSSE ANALİZİ")
st.caption("Para Giriş/Çıkışı • AI Tahmini • HDFGS Özel Takip")

# --- HİSSE LİSTESİ (BIST En Popülerler) ---
hisseler = [
    "HDFGS.IS", # <-- KRAL
    "THYAO.IS", "ASELS.IS", "GARAN.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS", "AKBNK.IS", 
    "TUPRS.IS", "SASA.IS", "HEKTS.IS", "PETKM.IS", "BIMAS.IS", "EKGYO.IS", "ODAS.IS", 
    "KONTR.IS", "GUBRF.IS", "FROTO.IS", "TTKOM.IS", "ISCTR.IS", "YKBNK.IS", "SAHOL.IS",
    "ASTOR.IS", "EUPWR.IS", "GESAN.IS", "SMRTG.IS", "ALFAS.IS", "CANTE.IS", "REEDR.IS",
    "CVKMD.IS", "KCAER.IS", "OYAKC.IS", "EGEEN.IS", "DOAS.IS", "MGROS.IS", "TOASO.IS"
]

# --- ANALİZ MOTORU ---
def hisse_analiz_et(symbol):
    try:
        # 1 Aylık veri çek (Trendi görmek için)
        df = yf.download(symbol, period="1mo", interval="1d", progress=False)
        if hasattr(df.columns, 'levels'): df.columns = df.columns.get_level_values(0)
        
        if len(df) < 14: return None # Yetersiz veri
        
        son = df.iloc[-1]
        fiyat = son['Close']
        
        # --- 1. PARA GİRİŞ/ÇIKIŞ HESABI (MFI) ---
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        raw_money = typical_price * df['Volume']
        
        pos_flow = []
        neg_flow = []
        
        for i in range(1, len(typical_price)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                pos_flow.append(raw_money.iloc[i])
                neg_flow.append(0)
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                pos_flow.append(0)
                neg_flow.append(raw_money.iloc[i])
            else:
                pos_flow.append(0)
                neg_flow.append(0)
        
        # Son 14 günün toplamı
        pos_sum = sum(pos_flow[-14:])
        neg_sum = sum(neg_flow[-14:])
        
        if neg_sum == 0: mfi = 100
        else:
            ratio = pos_sum / neg_sum
            mfi = 100 - (100 / (1 + ratio))
            
        # Tahmini Para Giriş Tutarı (Sanal Hesap)
        net_para_akisi = pos_sum - neg_sum
        para_durumu_str = f"+{net_para_akisi/1000000:.1f} Milyon TL" if net_para_akisi > 0 else f"{net_para_akisi/1000000:.1f} Milyon TL"
        
        # --- 2. AI TAHMİN MOTORU ---
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        
        puan = 0
        # Trend Puanı
        if fiyat > sma20: puan += 1
        else: puan -= 1
        
        # Para Puanı
        if mfi > 50: puan += 1
        else: puan -= 1
        
        # Karar
        if puan >= 2:
            ai_oneri = "YÜKSELİŞ BEKLENİYOR 🚀"
            ai_class = "yukselir"
            ai_yorum = "Trend pozitif ve güçlü para girişi var."
        elif puan <= -2:
            ai_oneri = "DÜŞÜŞ RİSKİ 🔻"
            ai_class = "duser"
            ai_yorum = "Para çıkışı var ve trend desteğin altında."
        else:
            ai_oneri = "YATAY / İZLE ⏸️"
            ai_class = "notr"
            ai_yorum = "Kararsız bölge. Kırılım beklenmeli."
            
        return {
            "Sembol": symbol.replace(".IS", ""),
            "Fiyat": fiyat,
            "MFI": mfi,
            "ParaYazi": para_durumu_str,
            "Oneri": ai_oneri,
            "Class": ai_class,
            "Yorum": ai_yorum
        }

    except:
        return None

# --- ARAYÜZ ---
if st.button("PİYASAYI ANALİZ ET 🧠", type="primary"):
    bar = st.progress(0, text="Yapay Zeka Hisseleri Tarıyor...")
    
    cols = st.columns(2)
    
    for i, sembol in enumerate(hisseler):
        veri = hisse_analiz_et(sembol)
        
        # İlerleme çubuğu
        bar.progress((i + 1) / len(hisseler))
        time.sleep(0.05) # Anti-ban beklemesi
        
        if veri:
            col = cols[0] if i % 2 == 0 else cols[1]
            
            with col:
                ozel_style = "hdfgs-ozel" if "HDFGS" in veri['Sembol'] else ""
                
                # Bar Rengi
                bar_renk = "#10b981" if veri['MFI'] > 50 else "#ef4444"
                
                st.markdown(f"""
                <div class="analiz-karti {ozel_style}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h3 style="margin:0; color:#e5e7eb;">{veri['Sembol']}</h3>
                        <span style="font-size:20px; font-weight:bold; color:white;">{veri['Fiyat']:.2f} TL</span>
                    </div>
                    
                    <div style="margin-bottom:10px;">
                        <span class="etiket {veri['Class']}">{veri['Oneri']}</span>
                        <span class="etiket" style="background-color:#374151; color:#d1d5db;">MFI: {veri['MFI']:.0f}</span>
                    </div>
                    
                    <div style="font-size:13px; color:#9ca3af; margin-bottom:5px;">
                        <i>🤖 AI: {veri['Yorum']}</i>
                    </div>
                    
                    <div style="font-size:12px; color:#d1d5db; display:flex; justify-content:space-between;">
                        <span>Para Akışı Gücü:</span>
                        <span>{veri['ParaYazi']} (Tahmini)</span>
                    </div>
                    <div class="para-bar-bg">
                        <div class="para-bar-doluluk" style="width: {veri['MFI']}%; background-color: {bar_renk};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    bar.empty()
    st.success("Tüm Pazar Analiz Edildi!")
else:
    st.info("Analizi başlatmak için butona basın.")
