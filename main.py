import streamlit as st
import google.generativeai as genai
import PIL.Image

# --- GÜVENLİK (Secrets'tan Şifreyi Al) ---
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol et.")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🍳", layout="wide")

# --- UYGULAMA MAKYAJI (MOBİL GÖRÜNÜM) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { margin-top: -80px; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- YAN MENÜ ---
st.sidebar.title("⚙️ Ayarlar / Settings")

# Dil Seçeneği
secilen_dil = st.sidebar.selectbox(
    "Dil Seçin / Select Language",
    ["Türkçe", "English", "Deutsch", "Español", "Français", "العربية"]
)

# Mod Seçeneği
if secilen_dil == "English":
    mod_basligi = "What is your goal?"
    secenekler = ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"]
elif secilen_dil == "Deutsch":
    mod_basligi = "Was ist dein Ziel?"
    secenekler = ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"]
else:
    mod_basligi = "Hedefiniz Nedir?"
    secenekler = ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"]

sef_modu = st.sidebar.radio(mod_basligi, secenekler)

# --- ANA EKRAN ---
st.title("🍳 Buzdolabı Gurmesi")

# Dile göre metinler
if secilen_dil == "English":
    upload_text = "Upload Image"
    button_text = "Analyze & Find Recipes! 🚀"
    loading_text = "AI is calculating macros..."
    result_text = "✅ Result:"
    st.write("Upload your fridge photo, get the best recipes with macros!")
elif secilen_dil == "Deutsch":
    upload_text = "Bild hochladen"
    button_text = "Analysieren! 🚀"
    loading_text = "KI berechnet Nährwerte..."
    result_text = "✅ Ergebnis:"
    st.write("Lade ein Foto hoch, erhalte Rezepte mit Nährwertangaben!")
else:
    upload_text = "Resmi buraya bırak veya seç"
    button_text = "Analiz Et ve Tarif Bul! 🚀"
    loading_text = "Yapay zeka besin değerlerini hesaplıyor..."
    result_text = "✅ Sonuç:"
    st.write("Dolabın fotoğrafını yükle, besin değerleriyle birlikte tarifini al!")

# Resim Yükleme
yuklenen_resim = st.file_uploader(upload_text, type=["jpg", "jpeg", "png"])

if yuklenen_resim is not None:
    image = PIL.Image.open(yuklenen_resim)
    st.image(image, caption='Analiz Ediliyor...', use_column_width=True)
    
    if st.button(button_text, type="primary"):
        with st.spinner(loading_text):
            try:
                # --- YENİ EMRİMİZ (PROMPT) ---
                ana_komut = f"Bu resimdeki yiyecekleri analiz et. Bana {secilen_dil} dilinde cevap ver."
                
                # İşte senin istediğin BESİN DEĞERİ komutu:
                besin_komutu = "Her tarifin sonunda mutlaka ayrı bir kutu veya liste içinde şunları yaz: 1 porsiyon için Tahmini Kalori (kcal), Protein (gr), Karbonhidrat (gr) ve Yağ (gr) miktarları."
                
                if "🥗" in sef_modu:
                    ozel_istek = "Sen uzman bir diyetisyensin. Düşük kalorili, sağlıklı 2 tarif ver."
                elif "💪" in sef_modu:
                    ozel_istek = "Sen sporcu koçusun. Kas gelişimi için Yüksek proteinli 2 tarif ver."
                else:
                    ozel_istek = "Sen samimi bir şefsin. En lezzetli ve pratik 2 tarif ver."
                
                final_prompt = [f"{ana_komut} {ozel_istek} {besin_komutu} Eksik malzeme varsa söyle.", image]
                
                cevap = model.generate_content(final_prompt)
                
                st.success(result_text)
                st.write(cevap.text)
                
                st.divider()
                
                # --- GİZLENEN LİNK ---
                # İleride buradaki '#' işaretlerini kaldırdığında buton geri gelecek.
                # buy_text = "Shop Ingredients" if secilen_dil == "English" else "Eksikleri Getir'den Söyle"
                # st.link_button(f"🛒 {buy_text}", "https://www.getir.com")
                
                # Şimdilik kullanıcıya boş görünmesin diye bir not (Opsiyonel):
                if secilen_dil == "Türkçe":
                    st.caption("💡 Afiyet olsun! Yakında market siparişi özelliği eklenecektir.")
                else:
                    st.caption("💡 Bon Appetit! Market ordering coming soon.")
                
            except Exception as e:
                st.error(f"Error: {e}")