import streamlit as st
import google.generativeai as genai
import PIL.Image
import json
import os
from datetime import date

# --- 1. AYARLAR ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

# Güvenlik
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol et.")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. VERİ TABANI ---
DOSYA_ADI = "kalori_takibi.json"

def verileri_yukle():
    if not os.path.exists(DOSYA_ADI): return {}
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def veriyi_kaydet(data):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. MAKYAJ ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { margin-top: -80px; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 4. YAN MENÜ (GLOBAL AYARLAR) ---
# DİL SEÇİMİNİ EN BAŞA ALDIK Kİ MENÜLER DE DEĞİŞSİN
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox(
    "Seç / Select",
    ["Türkçe", "English", "Deutsch", "Español", "Français", "العربية"]
)

st.sidebar.divider()

# --- MENÜ METİNLERİNİ DİLE GÖRE AYARLA ---
if secilen_dil == "English":
    menu_baslik = "📱 Menu"
    nav_baslik = "Where to go?"
    sayfa_isimleri = ["📸 Fridge Chef", "📊 Calorie Tracker"]
elif secilen_dil == "Deutsch":
    menu_baslik = "📱 Menü"
    nav_baslik = "Wohin gehen?"
    sayfa_isimleri = ["📸 Kühlschrank-Chef", "📊 Kalorien-Tracker"]
else: # Varsayılan Türkçe
    menu_baslik = "📱 Menü"
    nav_baslik = "Gitmek İstediğin Yer:"
    sayfa_isimleri = ["📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]

st.sidebar.title(menu_baslik)

# Sayfa Seçimi (Artık isimler dinamik)
secilen_sayfa = st.sidebar.radio(nav_baslik, sayfa_isimleri)

st.sidebar.divider()

# --- SAYFA 1: BUZDOLABI ŞEFİ ---
# (Burada sayfa isminin 0. indeksine yani "Şef" sayfasına bakıyoruz)
if secilen_sayfa == sayfa_isimleri[0]:
    
    # Şef Modu Ayarları (Dile Göre)
    if secilen_dil == "English":
        st.sidebar.header("⚙️ Chef Settings")
        mod_basligi = "What is your goal?"
        secenekler = ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"]
        upload_text = "Upload Image"
        button_text = "Analyze! 🚀"
        loading_text = "Calculating..."
        result_text = "✅ Result:"
        main_title = "📸 Fridge Chef"
        sub_title = "Upload fridge photo, get recipes."
    elif secilen_dil == "Deutsch":
        st.sidebar.header("⚙️ Chef Einstellungen")
        mod_basligi = "Ziel?"
        secenekler = ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"]
        upload_text = "Bild hochladen"
        button_text = "Analysieren! 🚀"
        loading_text = "Berechnung..."
        result_text = "✅ Ergebnis:"
        main_title = "📸 Kühlschrank-Chef"
        sub_title = "Lade ein Foto hoch."
    else:
        st.sidebar.header("⚙️ Şef Ayarları")
        mod_basligi = "Hedef?"
        secenekler = ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"]
        upload_text = "Resmi buraya bırak veya seç"
        button_text = "Analiz Et! 🚀"
        loading_text = "Hesaplanıyor..."
        result_text = "✅ Sonuç:"
        main_title = "📸 Buzdolabı Şefi"
        sub_title = "Dolabın fotoğrafını yükle, tarifini al."

    sef_modu = st.sidebar.radio(mod_basligi, secenekler)

    # Ana İçerik
    st.title(main_title)
    st.caption(sub_title)

    yuklenen_resim = st.file_uploader(upload_text, type=["jpg", "jpeg", "png"])

    if yuklenen_resim is not None:
        image = PIL.Image.open(yuklenen_resim)
        st.image(image, caption='...', use_column_width=True)
        
        if st.button(button_text, type="primary"):
            with st.spinner(loading_text):
                try:
                    ana_komut = f"Bu resimdeki yiyecekleri analiz et. Bana {secilen_dil} dilinde cevap ver."
                    besin_komutu = "Her tarifin sonunda renkli bir kutu içinde 1 porsiyon için: Kalori, Protein, Karbonhidrat ve Yağ değerlerini yaz."
                    
                    if "🥗" in sef_modu: ozel_istek = "Diyetisyen modu: Düşük kalorili tarifler."
                    elif "💪" in sef_modu: ozel_istek = "Sporcu modu: Yüksek proteinli tarifler."
                    else: ozel_istek = "Şef modu: Lezzetli tarifler."
                    
                    final_prompt = [f"{ana_komut} {ozel_istek} {besin_komutu}", image]
                    cevap = model.generate_content(final_prompt)
                    
                    st.success(result_text)
                    st.markdown(cevap.text, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

# --- SAYFA 2: KALORİ TAKİBİ ---
# (Burada sayfa isminin 1. indeksine yani "Takip" sayfasına bakıyoruz)
elif secilen_sayfa == sayfa_isimleri[1]:
    
    # Başlıkları Dile Göre Ayarla
    if secilen_dil == "English":
        page_title = "📊 Daily Tracker"
        add_meal_title = "➕ Add Meal"
        meal_select = "Select Meal"
        meal_name = "Food Name"
        add_button = "Add to List 💾"
        summary_title = "📅 Summary"
        details_title = "📋 Details"
        meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    elif secilen_dil == "Deutsch":
        page_title = "📊 Täglicher Tracker"
        add_meal_title = "➕ Mahlzeit hinzufügen"
        meal_select = "Mahlzeit wählen"
        meal_name = "Essensname"
        add_button = "Hinzufügen 💾"
        summary_title = "📅 Zusammenfassung"
        details_title = "📋 Einzelheiten"
        meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
    else:
        page_title = "📊 Günlük Takip"
        add_meal_title = "➕ Ne Yedin?"
        meal_select = "Öğün Seç"
        meal_name = "Yemek Adı"
        add_button = "Listeye Ekle 💾"
        summary_title = "📅 Gün Özeti"
        details_title = "📋 Öğün Detayları"
        meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]

    st.title(page_title)
    
    veri_tabani = verileri_yukle()
    
    bugun = str(date.today())
    secilen_tarih = st.date_input("📅", date.today())
    tarih_str = str(secilen_tarih)
    
    # Veritabanı yapısı (Dilden bağımsız olması için İngilizce key kullanıyoruz)
    # Ama ekranda gösterirken dile göre çevireceğiz.
    if tarih_str not in veri_tabani:
        veri_tabani[tarih_str] = {"1": [], "2": [], "3": [], "4": []}
        # 1: Sabah, 2: Öğle, 3: Akşam, 4: Ara
    
    gunluk_veri = veri_tabani[tarih_str]

    st.subheader(add_meal_title)
    
    col1, col2 = st.columns(2)
    with col1:
        # Öğün seçimi (Ekranda görünen)
        secilen_ogun_isim = st.selectbox(meal_select, meals)
        # Veritabanı için kod karşılığını bul
        ogun_kodu = str(meals.index(secilen_ogun_isim) + 1) 
        
        yemek_adi = st.text_input(meal_name)
    
    with col2:
        kalori = st.number_input("Kalori (kcal)", min_value=0, step=10)
        protein = st.number_input("Protein (gr)", min_value=0, step=1)
        karbon = st.number_input("Carb (gr)", min_value=0, step=1)
        yag = st.number_input("Fat (gr)", min_value=0, step=1)

    if st.button(add_button):
        if yemek_adi:
            yeni_kayit = {
                "yemek": yemek_adi,
                "kalori": kalori,
                "protein": protein,
                "karbon": karbon,
                "yag": yag
            }
            gunluk_veri[ogun_kodu].append(yeni_kayit)
            veri_tabani[tarih_str] = gunluk_veri
            veriyi_kaydet(veri_tabani)
            st.success("✅")
            st.rerun()

    st.divider()

    # ÖZET
    st.subheader(f"{summary_title} ({tarih_str})")
    
    toplam_kalori = sum(item['kalori'] for k in gunluk_veri for item in gunluk_veri[k])
    toplam_protein = sum(item['protein'] for k in gunluk_veri for item in gunluk_veri[k])
    toplam_karbon = sum(item['karbon'] for k in gunluk_veri for item in gunluk_veri[k])
    toplam_yag = sum(item['yag'] for k in gunluk_veri for item in gunluk_veri[k])

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🔥 Kcal", toplam_kalori)
    k2.metric("🥩 Protein", f"{toplam_protein}g")
    k3.metric("🍞 Carb", f"{toplam_karbon}g")
    k4.metric("💧 Fat", f"{toplam_yag}g")

    st.write(f"### {details_title}")
    
    # Listeleme
    for i, ogun_ismi in enumerate(meals):
        kod = str(i + 1)
        if len(gunluk_veri[kod]) > 0:
            st.markdown(f"**{ogun_ismi}**")
            for yemek in gunluk_veri[kod]:
                st.text(f"- {yemek['yemek']}: {yemek['kalori']} kcal")
            st.divider()
            
    if st.button("🗑️ Reset"):
        del veri_tabani[tarih_str]
        veriyi_kaydet(veri_tabani)
        st.rerun()