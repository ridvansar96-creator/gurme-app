import streamlit as st
import google.generativeai as genai
import PIL.Image

# --- AYARLAR ---
# BURAYA KENDİ UZUN ŞİFRENİ YAPIŞTIR
genai.configure(api_key="AIzaSyA40KR2_2i7nlw44bKWO670j7MDcxC2Ees")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- SAYFA TASARIMI ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

# --- YAN MENÜ (SIDEBAR) ---
# Kullanıcının seçim yapacağı yer burası
st.sidebar.title("⚙️ Ayarlar / Settings")

# 1. Dil Seçeneği
secilen_dil = st.sidebar.selectbox(
    "Dil Seçin / Select Language",
    ["Türkçe", "English", "Deutsch", "Español", "Français", "العربية"]
)

# 2. Şef Modu (Kişilik)
sef_modu = st.sidebar.radio(
    "Hedefiniz Nedir?",
    ["👨‍🍳 Standart Lezzet (Sadece doyur)", 
     "🥗 Diyetisyen (Düşük kalori, sağlıklı)", 
     "💪 Sporcu (Yüksek protein, enerji)"]
)

st.sidebar.info("💡 Modu değiştirerek tariflerin içeriğini değiştirebilirsiniz.")

# --- ANA EKRAN ---
st.title("🥗 Buzdolabı Gurmesi v2.0")

# Başlık dile göre değişsin istersen basit bir if yapısı:
if secilen_dil == "English":
    st.write("Upload your fridge photo, get the best recipes!")
else:
    st.write("Dolabın fotoğrafını yükle, sana en uygun tarifi vereyim!")

# Resim Yükleme
yuklenen_resim = st.file_uploader("Resmi buraya bırak / Upload Image", type=["jpg", "jpeg", "png"])

if yuklenen_resim is not None:
    image = PIL.Image.open(yuklenen_resim)
    # Resmi ortalayarak gösterelim
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(image, caption='Analiz Ediliyor...', use_column_width=True)
    
    # Buton
    buton_metni = "Analiz Et ve Tarif Bul! 🚀"
    if secilen_dil == "English": buton_metni = "Analyze & Find Recipes! 🚀"
    
    if st.button(buton_metni, type="primary"):
        with st.spinner('Yapay zeka hesaplama yapıyor... / AI is thinking...'):
            try:
                # --- prompt (EMİR) HAZIRLAMA ---
                # Burası çok önemli. Seçilen moda göre emri değiştiriyoruz.
                
                ana_komut = f"Bu resimdeki yiyecekleri analiz et. Bana {secilen_dil} dilinde cevap ver."
                
                if "Diyetisyen" in sef_modu:
                    ozel_istek = "Sen uzman bir diyetisyensin. Bana kalorisi düşük, sağlıklı ve kilo aldırmayan 2 tarif ver. Her tarifin yaklaşık kalori değerini ve sağlık faydalarını mutlaka yaz."
                elif "Sporcu" in sef_modu:
                    ozel_istek = "Sen profesyonel bir sporcu koçusun. Bana kas gelişimini destekleyen, yüksek proteinli 2 tarif ver. Antrenman öncesi mi sonrası mı yenmeli belirt."
                else: # Standart
                    ozel_istek = "Sen samimi bir Türk şefisin. Elimizdekilerle yapılabilecek en lezzetli, en pratik 2 tarifi ver. Dünya mutfağından da olabilir."
                
                final_prompt = [f"{ana_komut} {ozel_istek} Eksik malzeme varsa söyle.", image]
                
                # Yapay Zekaya Gönder
                cevap = model.generate_content(final_prompt)
                
                # Cevabı Yazdır
                st.success("✅ Sonuç / Result:")
                st.write(cevap.text)
                
                # --- PARA KAZANMA BÖLÜMÜ ---
                st.divider()
                st.info("🛒 Market / Shopping")
                st.link_button("Eksikleri Getir'den Söyle", "https://www.getir.com")
                
            except Exception as e:
                st.error(f"Hata / Error: {e}")