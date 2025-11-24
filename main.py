import streamlit as st
import google.generativeai as genai
import PIL.Image

# --- GÜVENLİK AYARI (Secrets'tan alır) ---
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol et.")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.title("⚙️ Ayarlar / Settings")

# 1. Dil Seçeneği
secilen_dil = st.sidebar.selectbox(
    "Dil Seçin / Select Language",
    ["Türkçe", "English", "Deutsch", "Español", "Français", "العربية"]
)

# 2. Şef Modu (Dile Göre Değişen Seçenekler)
# Önce seçenekleri dile göre hazırlayalım
if secilen_dil == "English":
    mod_basligi = "What is your goal?"
    secenekler = [
        "👨‍🍳 Standard Taste (Just feed me)", 
        "🥗 Dietitian (Low calorie, healthy)", 
        "💪 Athlete (High protein, energy)"
    ]
elif secilen_dil == "Deutsch":
    mod_basligi = "Was ist dein Ziel?"
    secenekler = [
        "👨‍🍳 Standardgeschmack", 
        "🥗 Ernährungsberater", 
        "💪 Sportler"
    ]
else: # Varsayılan Türkçe
    mod_basligi = "Hedefiniz Nedir?"
    secenekler = [
        "👨‍🍳 Standart Lezzet (Sadece doyur)", 
        "🥗 Diyetisyen (Düşük kalori, sağlıklı)", 
        "💪 Sporcu (Yüksek protein, enerji)"
    ]

# Radyo butonunu oluşturuyoruz
sef_modu = st.sidebar.radio(mod_basligi, secenekler)

st.sidebar.info("💡 " + ("Modu değiştirerek tarifleri özelleştir." if secilen_dil == "Türkçe" else "Change mode to customize recipes."))

# --- ANA EKRAN ---
st.title("🥗 Buzdolabı Gurmesi v2.1")

# Başlıklar
if secilen_dil == "English":
    st.write("Upload your fridge photo, get the best recipes!")
    upload_text = "Upload Image"
    button_text = "Analyze & Find Recipes! 🚀"
    loading_text = "AI is thinking..."
    result_text = "✅ Result:"
elif secilen_dil == "Deutsch":
    st.write("Lade ein Foto deines Kühlschranks hoch!")
    upload_text = "Bild hochladen"
    button_text = "Analysieren & Rezepte finden! 🚀"
    loading_text = "KI denkt nach..."
    result_text = "✅ Ergebnis:"
else:
    st.write("Dolabın fotoğrafını yükle, sana en uygun tarifi vereyim!")
    upload_text = "Resmi buraya bırak veya seç"
    button_text = "Analiz Et ve Tarif Bul! 🚀"
    loading_text = "Yapay zeka hesaplama yapıyor..."
    result_text = "✅ Sonuç:"

# Resim Yükleme
yuklenen_resim = st.file_uploader(upload_text, type=["jpg", "jpeg", "png"])

if yuklenen_resim is not None:
    image = PIL.Image.open(yuklenen_resim)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(image, caption='...', use_column_width=True)
    
    if st.button(button_text, type="primary"):
        with st.spinner(loading_text):
            try:
                # --- prompt (EMİR) HAZIRLAMA ---
                # EMOJİ TAKTİĞİ: Kelimeye değil, emojiye bakıyoruz.
                # Böylece dil İngilizce olsa bile "🥗" emojisini görünce diyetisyen olduğunu anlıyor.
                
                ana_komut = f"Bu resimdeki yiyecekleri analiz et. Bana {secilen_dil} dilinde cevap ver."
                
                if "🥗" in sef_modu: # Diyetisyen Emojisi
                    ozel_istek = "Sen uzman bir diyetisyensin. Bana kalorisi düşük, sağlıklı ve kilo aldırmayan 2 tarif ver. Her tarifin yaklaşık kalori değerini yaz."
                elif "💪" in sef_modu: # Sporcu Emojisi
                    ozel_istek = "Sen profesyonel bir sporcu koçusun. Bana kas gelişimini destekleyen, yüksek proteinli 2 tarif ver."
                else: # Standart (Aşçı Emojisi 👨‍🍳)
                    ozel_istek = "Sen samimi bir şefsin. Elimizdekilerle yapılabilecek en lezzetli 2 tarifi ver."
                
                final_prompt = [f"{ana_komut} {ozel_istek} Eksik malzeme varsa söyle.", image]
                
                cevap = model.generate_content(final_prompt)
                
                st.success(result_text)
                st.write(cevap.text)
                
                st.divider()
                st.link_button("🛒 " + ("Shop Ingredients" if secilen_dil == "English" else "Eksikleri Getir"), "https://www.getir.com")
                
            except Exception as e:
                st.error(f"Error: {e}")