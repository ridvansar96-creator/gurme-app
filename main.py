import streamlit as st
import google.generativeai as genai
import PIL.Image

# --- AYARLAR ---
# BURAYA KENDİ UZUN ŞİFRENİ YAPIŞTIR
genai.configure(api_key="AIzaSyA40KR2_2i7nlw44bKWO670j7MDcxC2Ees")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- SAYFA TASARIMI ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🍳")

st.title("🍳 Buzdolabı Gurmesi")
st.write("Dolabın fotoğrafını yükle, sana krallar gibi tarif vereyim!")

# 1. Resim Yükleme
yuklenen_resim = st.file_uploader("Resmi buraya bırak veya seç", type=["jpg", "jpeg", "png"])

# 2. Resim Yüklendiyse
if yuklenen_resim is not None:
    image = PIL.Image.open(yuklenen_resim)
    st.image(image, caption='Senin Dolap', use_column_width=True)
    
    # 3. Butona Basılınca
    if st.button('Bana Yemek Bul! 🚀', type="primary"):
        with st.spinner('Şef malzemeleri inceliyor, tarif hazırlanıyor...'):
            try:
                # Yapay Zekaya Soruyoruz
                prompt = "Bu resimdeki malzemeleri analiz et. Bana bu malzemelerle yapabileceğim Dünya Mutfağından (Türk, İtalyan, Asya, Amerikan vb.) en lezzetli 2-3 farklı tarif seçeneği sun. Hangisi daha kolaysa onu öne çıkar. Samimi bir dil kullan."
                cevap = model.generate_content([prompt, image])
                
                # Cevabı Yazdırıyoruz
                st.success("👨‍🍳 İşte Şefin Önerisi:")
                st.write(cevap.text)
                
                # --- PARA KAZANMA BÖLÜMÜ ---
                st.divider() 
                st.info("💡 Tarifteki malzemeler evde yok mu?")
                st.link_button("🛒 Eksik Malzemeleri Hemen Söyle", "https://www.getir.com")
                st.caption("Bu butona tıklayarak yapacağınız alışverişlerden uygulamamız komisyon kazanabilir. Afiyet olsun! 😉")
                
            except Exception as e:
                st.error(f"Hata oluştu usta: {e}")