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

# --- 2. ÇOK DİLLİ YEMEK LİSTESİ ---
YEMEK_SOZLUGU = {
    "Türkçe": [
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
        "Tavuk Sote", "Taze Fasulye", "Tost (Karışık)", "Urfa Kebap", "Yayla Çorbası"
    ],
    "English": [
        "Apple", "Bagel", "Banana", "BBQ Ribs", "Beef Stew", "Boiled Egg", "Brownie",
        "Burger", "Caesar Salad", "Cheesecake", "Chicken Curry", "Chicken Nuggets",
        "Chicken Soup", "Chicken Wings", "Chocolate Cake", "Coffee", "Donuts",
        "Fish and Chips", "French Fries", "Fried Chicken", "Grilled Cheese",
        "Grilled Chicken", "Grilled Salmon", "Hot Dog", "Ice Cream", "Lasagna",
        "Mac and Cheese", "Mashed Potatoes", "Omelette", "Pancakes", "Pasta (Alfredo)",
        "Pasta (Bolognese)", "Pizza (Slice)", "Potato Salad", "Rice", "Roast Beef",
        "Sandwich (Club)", "Sandwich (Tuna)", "Smoothie", "Spaghetti", "Steak",
        "Sushi (Roll)", "Tacos", "Toast", "Waffles", "Yogurt"
    ],
    "Deutsch": [
        "Apfel", "Apfelstrudel", "Bier", "Bratkartoffeln", "Bratwurst", "Brezel",
        "Brot", "Burger", "Currywurst", "Döner Kebab", "Eisbein", "Frikadelle",
        "Gemüsesuppe", "Gulasch", "Hähnchen (Gebraten)", "Hamburger", "Kaffee",
        "Kartoffelsalat", "Kartoffelsuppe", "Käsekuchen", "Knödel", "Leberkäse",
        "Marmelade", "Maultaschen", "Omelett", "Pfannkuchen", "Pizza", "Pommes Frites",
        "Rinderroulade", "Sauerbraten", "Sauerkraut", "Schnitzel", "Spätzle",
        "Spiegelei", "Steak", "Toast", "Wurstsalat"
    ],
    "Français": [
        "Baguette", "Boeuf Bourguignon", "Brioche", "Café", "Camembert", "Cassoulet",
        "Champagne", "Chocolat", "Confit de Canard", "Coq au Vin", "Crème Brûlée",
        "Crêpe", "Croissant", "Éclair", "Escargots", "Foie Gras", "Fondue",
        "Frites", "Fromage", "Gratin Dauphinois", "Hamburger", "Macaron", "Madeleine",
        "Mousse au Chocolat", "Omelette", "Pain au Chocolat", "Pâtes", "Pizza",
        "Pot-au-feu", "Poulet Rôti", "Quiche Lorraine", "Ratatouille", "Salade Niçoise",
        "Sandwich Jambon-Beurre", "Soufflé", "Soupe à l'oignon", "Steak Frites",
        "Tarte Tatin", "Vin Rouge", "Yaourt"
    ],
    "العربية": [
        "فلافل (Falafel)", "شاورما (Shawarma)", "كبسة (Kabsa)", "hummus (حمص)", 
        "تبولة (Tabbouleh)", "منسف (Mansaf)", "فتوش (Fattoush)", "ورق عنب (Dolma)",
        "كباب (Kebab)", "كفتة (Kofta)", "مسخن (Musakhan)", "شكشوكة (Shakshouka)",
        "بامية (Okra)", "مقلوبة (Maqluba)", "مجدرة (Mujaddara)", "سمبوسك (Sambousek)",
        "مناقيش (Manakish)", "فول مدمس (Ful Medames)", "كنافة (Kunafa)", "بقلاوة (Baklava)",
        "برجر (Burger)", "بيتزا (Pizza)", "دجاج مشوي (Grilled Chicken)", "أرز (Rice)",
        "سلطة (Salad)", "بيض مسلوق (Boiled Egg)", "بيض مقلي (Fried Egg)", "خبز (Bread)",
        "بطاطس مقلية (French Fries)", "شوربة عدس (Lentil Soup)"
    ]
}

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

# --- 5. YAN MENÜ (DİL SEÇİMİ) ---
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

# --- 6. DİL AYARLARI (SÖZLÜK) ---
# Her dil için bütün metinleri burada ayarlıyoruz
if secilen_dil == "English":
    menu_baslik, nav_baslik = "📱 Menu", "Where to go?"
    sayfa_isimleri = ["📸 Fridge Chef", "📊 Calorie Tracker"]
    
    # Sayfa 1 Metinleri
    chef_settings, goal_title = "⚙️ Chef Settings", "What is your goal?"
    goals = ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"]
    upload_text, analyze_btn, result_txt = "Upload Image", "Analyze! 🚀", "✅ Result:"
    main_title_1, sub_title_1 = "📸 Fridge Chef", "Upload fridge photo, get recipes."
    
    # Sayfa 2 Metinleri
    tracker_title, add_meal_title = "📊 Daily Tracker", "➕ Add Meal"
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    labels = ["Calories", "Protein", "Carb", "Fat"]
    portion_label, add_btn_txt, summary_txt = "Portion", "Add to List 💾", "📅 Summary"
    reset_btn, ai_btn = "🗑️ Reset Day", "✨ Calculate with AI"

elif secilen_dil == "Deutsch":
    menu_baslik, nav_baslik = "📱 Menü", "Wohin gehen?"
    sayfa_isimleri = ["📸 Kühlschrank-Chef", "📊 Kalorien-Tracker"]
    
    chef_settings, goal_title = "⚙️ Einstellungen", "Ziel?"
    goals = ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"]
    upload_text, analyze_btn, result_txt = "Bild hochladen", "Analysieren! 🚀", "✅ Ergebnis:"
    main_title_1, sub_title_1 = "📸 Kühlschrank-Chef", "Lade ein Foto hoch."
    
    tracker_title, add_meal_title = "📊 Kalorien-Tracker", "➕ Mahlzeit hinzufügen"
    meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
    labels = ["Kalorien", "Eiweiß", "Kohlenhydrate", "Fett"]
    portion_label, add_btn_txt, summary_txt = "Portion", "Hinzufügen 💾", "📅 Zusammenfassung"
    reset_btn, ai_btn = "🗑️ Zurücksetzen", "✨ KI-Berechnung"

elif secilen_dil == "Français":
    menu_baslik, nav_baslik = "📱 Menu", "Où aller ?"
    sayfa_isimleri = ["📸 Chef Frigo", "📊 Suivi Calories"]
    
    chef_settings, goal_title = "⚙️ Paramètres", "Quel objectif ?"
    goals = ["👨‍🍳 Standard", "🥗 Diététicien", "💪 Athlète"]
    upload_text, analyze_btn, result_txt = "Télécharger une image", "Analyser ! 🚀", "✅ Résultat :"
    main_title_1, sub_title_1 = "📸 Chef Frigo", "Téléchargez une photo, obtenez des recettes."
    
    tracker_title, add_meal_title = "📊 Suivi Quotidien", "➕ Ajouter un repas"
    meals = ["Petit-déjeuner", "Déjeuner", "Dîner", "Collation"]
    labels = ["Calories", "Protéines", "Glucides", "Lipides"]
    portion_label, add_btn_txt, summary_txt = "Portion", "Ajouter 💾", "📅 Résumé"
    reset_btn, ai_btn = "🗑️ Réinitialiser", "✨ Calculer avec IA"

elif secilen_dil == "العربية":
    menu_baslik, nav_baslik = "📱 القائمة", "إلى أين؟"
    sayfa_isimleri = ["📸 شيف الثلاجة", "📊 متتبع السعرات"]
    
    chef_settings, goal_title = "⚙️ الإعدادات", "ما هو هدفك؟"
    goals = ["👨‍🍳 قياسي", "🥗 أخصائي تغذية", "💪 رياضي"]
    upload_text, analyze_btn, result_txt = "تحميل صورة", "تحليل! 🚀", "✅ النتيجة:"
    main_title_1, sub_title_1 = "📸 شيف الثلاجة", "حمل صورة ثلاجتك واحصل على وصفات."
    
    tracker_title, add_meal_title = "📊 التتبع اليومي", "➕ أضف وجبة"
    meals = ["إفطار", "غداء", "عشاء", "وجبة خفيفة"]
    labels = ["سعرات", "بروتين", "كربوهيدرات", "دهون"]
    portion_label, add_btn_txt, summary_txt = "الكمية", "إضافة للقائمة 💾", "📅 ملخص"
    reset_btn, ai_btn = "🗑️ إعادة تعيين", "✨ حساب بالذكاء الاصطناعي"

else: # Varsayılan Türkçe
    menu_baslik, nav_baslik = "📱 Menü", "Gitmek İstediğin Yer:"
    sayfa_isimleri = ["📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]
    
    chef_settings, goal_title = "⚙️ Şef Ayarları", "Hedef?"
    goals = ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"]
    upload_text, analyze_btn, result_txt = "Resim Yükle", "Analiz Et! 🚀", "✅ Sonuç:"
    main_title_1, sub_title_1 = "📸 Buzdolabı Şefi", "Dolabın fotoğrafını yükle, tarifini al."
    
    tracker_title, add_meal_title = "📊 Günlük Takip", "➕ Ne Yedin?"
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
    labels = ["Kalori (kcal)", "Protein (gr)", "Karb (gr)", "Yağ (gr)"]
    portion_label, add_btn_txt, summary_txt = "Porsiyon", "Listeye Ekle 💾", "📅 Gün Özeti"
    reset_btn, ai_btn = "🗑️ Günü Sıfırla", "✨ Değerleri AI ile Getir"

st.sidebar.title(menu_baslik)
secilen_sayfa = st.sidebar.radio(nav_baslik, sayfa_isimleri)
st.sidebar.divider()

# --- SAYFA 1: BUZDOLABI ŞEFİ ---
if secilen_sayfa == sayfa_isimleri[0]:
    sef_modu = st.sidebar.radio(goal_title, goals)
    st.title(main_title_1)
    st.caption(sub_title_1)

    yuklenen_resim = st.file_uploader(upload_text, type=["jpg", "jpeg", "png"])

    if yuklenen_resim is not None:
        image = PIL.Image.open(yuklenen_resim)
        st.image(image, caption='...', use_column_width=True)
        
        if st.button(analyze_btn, type="primary"):
            with st.spinner("..."):
                try:
                    ana_komut = f"Analyze these food ingredients. Answer in {secilen_dil} language."
                    besin_komutu = "At the end, provide estimated Calories, Protein, Carb, and Fat for 1 portion in a colored box."
                    if "🥗" in sef_modu: ozel_istek = "Act as a Dietitian. Low calorie recipes."
                    elif "💪" in sef_modu: ozel_istek = "Act as a Sports Coach. High protein recipes."
                    else: ozel_istek = "Act as a Chef. Delicious recipes."
                    final_prompt = [f"{ana_komut} {ozel_istek} {besin_komutu}", image]
                    cevap = model.generate_content(final_prompt)
                    st.success(result_txt)
                    st.markdown(cevap.text, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- SAYFA 2: KALORİ TAKİBİ ---
elif secilen_sayfa == sayfa_isimleri[1]:
    st.title(tracker_title)
    
    veri_tabani = verileri_yukle()
    tarih_str = str(st.date_input("📅", date.today()))
    if tarih_str not in veri_tabani: veri_tabani[tarih_str] = {"1": [], "2": [], "3": [], "4": []}
    gunluk_veri = veri_tabani[tarih_str]

    st.subheader(add_meal_title)
    
    if 'kalori_degeri' not in st.session_state: st.session_state['kalori_degeri'] = 0
    if 'protein_degeri' not in st.session_state: st.session_state['protein_degeri'] = 0
    if 'karbon_degeri' not in st.session_state: st.session_state['karbon_degeri'] = 0
    if 'yag_degeri' not in st.session_state: st.session_state['yag_degeri'] = 0

    col1, col2 = st.columns([1, 1])

    with col1:
        # ÖĞÜN SEÇİMİ (İsimler dile göre değişiyor)
        secilen_ogun_isim = st.selectbox(meals[0] if secilen_dil=="English" else "Select", meals)
        ogun_kodu = str(meals.index(secilen_ogun_isim) + 1)
        
        # YEMEK LİSTESİ (Dile Göre Yükleniyor)
        # Eğer listede olmayan bir şey gelirse, varsayılan olarak Türkçe listeyi gösterelim.
        aktif_liste = YEMEK_SOZLUGU.get(secilen_dil, YEMEK_SOZLUGU["Türkçe"])
        
        c1, c2 = st.columns([2, 1])
        with c1:
            secilen_yemek = st.selectbox("Food / Yemek", aktif_liste)
        with c2:
            miktar = st.number_input(portion_label, min_value=0.5, step=0.5, value=1.0)
        
        if st.button(f"{ai_btn}"):
            with st.spinner("..."):
                try:
                    prompt = f"Estimate Calories, Protein, Carb, Fat for {miktar} portion of '{secilen_yemek}'. Return ONLY numbers separated by comma (e.g. 350,20,40,15)."
                    ai_cevap = model.generate_content(prompt).text.strip()
                    degerler = ai_cevap.split(',')
                    st.session_state['kalori_degeri'] = int(float(degerler[0]))
                    st.session_state['protein_degeri'] = int(float(degerler[1]))
                    st.session_state['karbon_degeri'] = int(float(degerler[2]))
                    st.session_state['yag_degeri'] = int(float(degerler[3]))
                    st.success("OK!")
                except:
                    st.error("Error")

    with col2:
        kalori = st.number_input(labels[0], value=st.session_state['kalori_degeri'], step=10)
        protein = st.number_input(labels[1], value=st.session_state['protein_degeri'], step=1)
        karbon = st.number_input(labels[2], value=st.session_state['karbon_degeri'], step=1)
        yag = st.number_input(labels[3], value=st.session_state['yag_degeri'], step=1)

    if st.button(add_btn_txt, type="primary"):
        kayit_adi = f"{miktar}x {secilen_yemek}"
        yeni_kayit = {"yemek": kayit_adi, "kalori": kalori, "protein": protein, "karbon": karbon, "yag": yag}
        gunluk_veri[ogun_kodu].append(yeni_kayit)
        veri_tabani[tarih_str] = gunluk_veri
        veriyi_kaydet(veri_tabani)
        st.session_state['kalori_degeri'] = 0
        st.success("✅")
        st.rerun()

    st.divider()
    st.subheader(summary_txt)
    
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
                st.text(f"- {yemek['yemek']}: {yemek['kalori']} kcal")
            st.divider()
            
    if st.button(reset_btn):
        del veri_tabani[tarih_str]
        veriyi_kaydet(veri_tabani)
        st.rerun()