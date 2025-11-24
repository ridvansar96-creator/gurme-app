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
    st.error("API Anahtarı bulunamadı! Secrets ayarlarını kontrol et.")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. HAZIR YEMEK LİSTESİ ---
TURK_YEMEKLERI = [
    "Adana Kebap", "Ayran", "Baklava", "Balık Izgara", "Barbunya", "Beyti", 
    "Biber Dolması", "Cacık", "Çiğ Köfte", "Çoban Salata", "Döner (Ekmek Arası)", 
    "Döner (Porsiyon)", "Elma", "Ezogelin Çorbası", "Fasulye (Kuru)", "Fırın Sütlaç", 
    "Hamburger", "Haşlanmış Yumurta", "Hünkar Beğendi", "İçli Köfte", 
    "İskender Kebap", "Karnıyarık", "Kaşarlı Tost", "Kebap (Karışık)", 
    "Kısır", "Köfte (Izgara)", "Künefe", "Lahmacun", "Mantı", "Menemen", 
    "Mercimek Çorbası", "Musakka", "Makarna (Sade)", "Makarna (Kıymalı)", "Muz",
    "Omlet", "Patates Kızartması", "Pide (Kaşarlı)", "Pide (Kıymalı)", 
    "Pilav (Bulgur)", "Pilav (Pirinç)", "Pizza (Dilim)", "Sarma (Yaprak)", 
    "Simit", "Su Böreği", "Tantuni", "Tavuk Döner", "Tavuk Haşlama", 
    "Tavuk Sote", "Taze Fasulye", "Tost (Karışık)", "Urfa Kebap", "Yayla Çorbası", 
    "Yoğurt (Kase)", "Zeytinyağlı Enginar"
]

# --- 3. VERİ TABANI ---
DOSYA_ADI = "kalori_takibi.json"

def verileri_yukle():
    if not os.path.exists(DOSYA_ADI): return {}
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def veriyi_kaydet(data):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 4. MAKYAJ ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { margin-top: -80px; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 5. YAN MENÜ ---
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch"])
st.sidebar.divider()

if secilen_dil == "English":
    menu_baslik, nav_baslik = "📱 Menu", "Where to go?"
    sayfa_isimleri = ["📸 Fridge Chef", "📊 Calorie Tracker"]
elif secilen_dil == "Deutsch":
    menu_baslik, nav_baslik = "📱 Menü", "Wohin gehen?"
    sayfa_isimleri = ["📸 Kühlschrank-Chef", "📊 Kalorien-Tracker"]
else:
    menu_baslik, nav_baslik = "📱 Menü", "Gitmek İstediğin Yer:"
    sayfa_isimleri = ["📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]

st.sidebar.title(menu_baslik)
secilen_sayfa = st.sidebar.radio(nav_baslik, sayfa_isimleri)
st.sidebar.divider()

# --- SAYFA 1: BUZDOLABI ŞEFİ (Aynı Kalıyor) ---
if secilen_sayfa == sayfa_isimleri[0]:
    if secilen_dil == "English":
        mod_basligi, secenekler = "Goal?", ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"]
        upload_text, button_text, result_text = "Upload Image", "Analyze! 🚀", "✅ Result:"
        main_title, sub_title = "📸 Fridge Chef", "Upload fridge photo, get recipes."
    elif secilen_dil == "Deutsch":
        mod_basligi, secenekler = "Ziel?", ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"]
        upload_text, button_text, result_text = "Bild hochladen", "Analysieren! 🚀", "✅ Ergebnis:"
        main_title, sub_title = "📸 Kühlschrank-Chef", "Lade ein Foto hoch."
    else:
        mod_basligi, secenekler = "Hedef?", ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"]
        upload_text, button_text, result_text = "Resim Yükle", "Analiz Et! 🚀", "✅ Sonuç:"
        main_title, sub_title = "📸 Buzdolabı Şefi", "Dolabın fotoğrafını yükle, tarifini al."

    sef_modu = st.sidebar.radio(mod_basligi, secenekler)
    st.title(main_title)
    st.caption(sub_title)

    yuklenen_resim = st.file_uploader(upload_text, type=["jpg", "jpeg", "png"])

    if yuklenen_resim is not None:
        image = PIL.Image.open(yuklenen_resim)
        st.image(image, caption='...', use_column_width=True)
        
        if st.button(button_text, type="primary"):
            with st.spinner("AI thinking..."):
                try:
                    ana_komut = f"Bu resimdeki yiyecekleri analiz et. Bana {secilen_dil} dilinde cevap ver."
                    besin_komutu = "Her tarifin sonunda renkli bir kutu içinde 1 porsiyon için: Kalori, Protein, Karbonhidrat ve Yağ değerlerini yaz."
                    if "🥗" in sef_modu: ozel_istek = "Diyetisyen modu."
                    elif "💪" in sef_modu: ozel_istek = "Sporcu modu."
                    else: ozel_istek = "Şef modu."
                    final_prompt = [f"{ana_komut} {ozel_istek} {besin_komutu}", image]
                    cevap = model.generate_content(final_prompt)
                    st.success(result_text)
                    st.markdown(cevap.text, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Hata: {e}")

# --- SAYFA 2: KALORİ TAKİBİ (PORSİYON GÜNCELLEMESİ) ---
elif secilen_sayfa == sayfa_isimleri[1]:
    
    # Başlıklar
    if secilen_dil == "English":
        page_title, add_meal_title = "📊 Daily Tracker", "➕ Add Meal"
        meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
        labels = ["Calories", "Protein", "Carb", "Fat"]
        portion_label = "Portion / Count"
    elif secilen_dil == "Deutsch":
        page_title, add_meal_title = "📊 Täglicher Tracker", "➕ Mahlzeit hinzufügen"
        meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
        labels = ["Kalorien", "Eiweiß", "Kohlenhydrate", "Fett"]
        portion_label = "Portion / Stück"
    else:
        page_title, add_meal_title = "📊 Günlük Takip", "➕ Ne Yedin?"
        meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
        labels = ["Kalori (kcal)", "Protein (gr)", "Karb (gr)", "Yağ (gr)"]
        portion_label = "Porsiyon / Adet"

    st.title(page_title)
    
    veri_tabani = verileri_yukle()
    tarih_str = str(st.date_input("📅", date.today()))
    
    if tarih_str not in veri_tabani:
        veri_tabani[tarih_str] = {"1": [], "2": [], "3": [], "4": []}
    
    gunluk_veri = veri_tabani[tarih_str]

    # --- YEMEK EKLEME BÖLÜMÜ ---
    st.subheader(add_meal_title)
    
    # Session State (Hafıza)
    if 'kalori_degeri' not in st.session_state: st.session_state['kalori_degeri'] = 0
    if 'protein_degeri' not in st.session_state: st.session_state['protein_degeri'] = 0
    if 'karbon_degeri' not in st.session_state: st.session_state['karbon_degeri'] = 0
    if 'yag_degeri' not in st.session_state: st.session_state['yag_degeri'] = 0

    col1, col2 = st.columns([1, 1])

    with col1:
        secilen_ogun_isim = st.selectbox(meals[0] if secilen_dil=="English" else "Öğün Seç", meals)
        ogun_kodu = str(meals.index(secilen_ogun_isim) + 1)
        
        # YEMEK SEÇİMİ VE PORSİYON YAN YANA
        c1, c2 = st.columns([2, 1])
        with c1:
            secilen_yemek = st.selectbox("Yemek Seç / Yaz (Ara)", TURK_YEMEKLERI)
        with c2:
            # Porsiyon Kutusu (Varsayılan 1.0, Adım 0.5 yani 1.5, 2.5 girilebilir)
            miktar = st.number_input(portion_label, min_value=0.5, step=0.5, value=1.0)
        
        # SİHİRLİ BUTON
        if st.button(f"✨ {miktar} Porsiyon Hesapla"):
            with st.spinner("AI hesaplıyor..."):
                try:
                    # AI'dan 1 porsiyonu istiyoruz, çarpma işlemini biz yapacağız (Daha sağlıklı)
                    prompt = f"'{secilen_yemek}' yemeğinin STANDART 1 porsiyonu (veya 1 adeti) için tahmini Kalori, Protein, Karbonhidrat ve Yağ değerlerini sadece rakam olarak, virgülle ayırarak ver. Örnek: 350,20,40,15. Başka hiçbir şey yazma."
                    ai_cevap = model.generate_content(prompt).text.strip()
                    
                    degerler = ai_cevap.split(',')
                    
                    # Matematik: AI'dan gelen veriyi Miktar ile çarpıyoruz
                    st.session_state['kalori_degeri'] = int(float(degerler[0]) * miktar)
                    st.session_state['protein_degeri'] = int(float(degerler[1]) * miktar)
                    st.session_state['karbon_degeri'] = int(float(degerler[2]) * miktar)
                    st.session_state['yag_degeri'] = int(float(degerler[3]) * miktar)
                    
                    st.success(f"{miktar} porsiyon için hesaplandı!")
                except:
                    st.error("AI hesaplayamadı, elle girin.")

    with col2:
        kalori = st.number_input(labels[0], value=st.session_state['kalori_degeri'], step=10)
        protein = st.number_input(labels[1], value=st.session_state['protein_degeri'], step=1)
        karbon = st.number_input(labels[2], value=st.session_state['karbon_degeri'], step=1)
        yag = st.number_input(labels[3], value=st.session_state['yag_degeri'], step=1)

    # KAYDETME BUTONU
    if st.button("Listeye Ekle / Add 💾", type="primary"):
        # Listede görünürken miktarı da yazalım (Örn: 1.5x İskender)
        kayit_adi = f"{miktar}x {secilen_yemek}"
        
        yeni_kayit = {
            "yemek": kayit_adi,
            "kalori": kalori,
            "protein": protein,
            "karbon": karbon,
            "yag": yag
        }
        gunluk_veri[ogun_kodu].append(yeni_kayit)
        veri_tabani[tarih_str] = gunluk_veri
        veriyi_kaydet(veri_tabani)
        
        # Sıfırla
        st.session_state['kalori_degeri'] = 0
        st.session_state['protein_degeri'] = 0
        st.session_state['karbon_degeri'] = 0
        st.session_state['yag_degeri'] = 0
        st.success(f"✅ Eklendi!")
        st.rerun()

    st.divider()

    # ÖZET TABLOSU
    st.subheader("📅 Özet / Summary")
    
    toplam_kalori = sum(item['kalori'] for k in gunluk_veri for item in gunluk_veri[k])
    toplam_protein = sum(item['protein'] for k in gunluk_veri for item in gunluk_veri[k])
    
    k1, k2 = st.columns(2)
    k1.metric("🔥 Kcal", toplam_kalori)
    k2.metric("🥩 Protein", f"{toplam_protein}g")
    
    for i, ogun_ismi in enumerate(meals):
        kod = str(i + 1)
        if len(gunluk_veri[kod]) > 0:
            st.markdown(f"**{ogun_ismi}**")
            for yemek in gunluk_veri[kod]:
                st.text(f"- {yemek['yemek']}: {yemek['kalori']} kcal | P:{yemek['protein']}")
            st.divider()
            
    if st.button("🗑️ Reset Day"):
        del veri_tabani[tarih_str]
        veriyi_kaydet(veri_tabani)
        st.rerun()