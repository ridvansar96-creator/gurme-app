import streamlit as st
import google.generativeai as genai
import PIL.Image
import json
import os
from datetime import date

# ==========================================================
# 1. AYARLAR VE GÜVENLİK
# ==========================================================
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

# API Anahtarı Kontrolü (Secrets'tan alır)
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ API Anahtarı bulunamadı! Lütfen Streamlit 'Secrets' ayarlarını kontrol et.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================================
# 2. VERİ VE YARDIMCI FONKSİYONLAR
# ==========================================================
DOSYA_ADI = "kalori_takibi.json"

# Çok Dilli Yemek Listesi (Autocomplete İçin)
YEMEK_SOZLUGU = {
    "Türkçe": ["Adana Kebap", "Ayran", "Baklava", "Balık", "Döner", "Elma", "Fasulye", "Hamburger", "İskender", "Kahve", "Köfte", "Lahmacun", "Makarna", "Menemen", "Muz", "Omlet", "Pilav", "Pizza", "Salata", "Simit", "Tavuk", "Tost", "Yumurta", "Zeytin"],
    "English": ["Apple", "Banana", "Burger", "Chicken", "Coffee", "Donut", "Egg", "Fish", "Fries", "Hot Dog", "Omelette", "Pasta", "Pizza", "Rice", "Salad", "Sandwich", "Steak", "Sushi", "Toast", "Yogurt"],
    "Deutsch": ["Apfel", "Bier", "Bratwurst", "Brot", "Burger", "Döner", "Ei", "Fisch", "Hähnchen", "Kaffee", "Kartoffeln", "Kuchen", "Nudeln", "Pizza", "Pommes", "Salat", "Schnitzel", "Wurst"],
    "Français": ["Baguette", "Café", "Croissant", "Fromage", "Frites", "Hamburger", "Omelette", "Pain", "Pâtes", "Pizza", "Poisson", "Poulet", "Salade", "Sandwich", "Steak", "Vin", "Yaourt"],
    "العربية": ["فلافل", "شاورما", "كبسة", "دجاج", "لحم", "سمك", "أرز", "خبز", "بيض", "سلطة", "بيتزا", "برجر", "قهوة", "شاي", "فول", "حمص"]
}

def verileri_yukle():
    if not os.path.exists(DOSYA_ADI): return {}
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def veriyi_kaydet(data):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Uygulama Makyajı (Streamlit yazılarını gizle)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { margin-top: -80px; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================================
# 3. YAN MENÜ (DİL VE NAVİGASYON)
# ==========================================================
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

# DİL AYARLARI (TÜM METİNLER)
if secilen_dil == "English":
    menu_title = "📱 Menu"
    nav_options = ["👤 Profile & Goals", "📸 Fridge Chef", "📊 Calorie Tracker"]
    # Profil Metinleri
    prof_txt = {"title": "👤 Profile & Goal Settings", "gender": "Gender", "male": "Male", "female": "Female", "age": "Age", "height": "Height (cm)", "weight": "Weight (kg)", "target": "Target Weight (kg)", "act": "Activity Level", "calc": "Calculate Plan 🚀", "res_cal": "Target Calories", "res_prot": "Target Protein", "advice": "💡 AI Coach Advice"}
    act_lvls = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
    # Şef Metinleri
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"], "upload": "Upload Image", "btn": "Analyze! 🚀", "res": "✅ Result:"}
    # Takip Metinleri
    track_txt = {"title": "📊 Daily Tracker", "add": "➕ Add Meal", "meal": "Meal", "food": "Food Name", "portion": "Portion", "calc_ai": "✨ Calculate with AI", "save": "Add to List 💾", "sum": "📅 Summary", "reset": "🗑️ Reset Day"}
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]

elif secilen_dil == "Deutsch":
    menu_title = "📱 Menü"
    nav_options = ["👤 Profil & Ziele", "📸 Kühlschrank-Chef", "📊 Kalorien-Tracker"]
    prof_txt = {"title": "👤 Profil & Ziele", "gender": "Geschlecht", "male": "Männlich", "female": "Weiblich", "age": "Alter", "height": "Größe (cm)", "weight": "Gewicht (kg)", "target": "Zielgewicht (kg)", "act": "Aktivität", "calc": "Berechnen 🚀", "res_cal": "Ziel-Kalorien", "res_prot": "Ziel-Protein", "advice": "💡 KI-Rat"}
    act_lvls = ["Sitzend", "Leicht aktiv", "Mäßig aktiv", "Sehr aktiv"]
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"], "upload": "Bild hochladen", "btn": "Analysieren! 🚀", "res": "✅ Ergebnis:"}
    track_txt = {"title": "📊 Tracker", "add": "➕ Mahlzeit", "meal": "Mahlzeit", "food": "Essen", "portion": "Portion", "calc_ai": "✨ KI-Berechnung", "save": "Speichern 💾", "sum": "📅 Zusammenfassung", "reset": "🗑️ Reset"}
    meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]

elif secilen_dil == "Français":
    menu_title = "📱 Menu"
    nav_options = ["👤 Profil & Objectifs", "📸 Chef Frigo", "📊 Suivi Calories"]
    prof_txt = {"title": "👤 Profil", "gender": "Genre", "male": "Homme", "female": "Femme", "age": "Âge", "height": "Taille", "weight": "Poids", "target": "Objectif", "act": "Activité", "calc": "Calculer 🚀", "res_cal": "Calories Cibles", "res_prot": "Protéines Cibles", "advice": "💡 Conseil IA"}
    act_lvls = ["Sédentaire", "Légèrement actif", "Modérément actif", "Très actif"]
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Diététicien", "💪 Athlète"], "upload": "Image", "btn": "Analyser! 🚀", "res": "✅ Résultat:"}
    track_txt = {"title": "📊 Suivi", "add": "➕ Ajouter", "meal": "Repas", "food": "Aliment", "portion": "Portion", "calc_ai": "✨ Calcul IA", "save": "Ajouter 💾", "sum": "📅 Résumé", "reset": "🗑️ Réinitialiser"}
    meals = ["Petit-déj", "Déjeuner", "Dîner", "Collation"]

elif secilen_dil == "العربية":
    menu_title = "📱 القائمة"
    nav_options = ["👤 الملف الشخصي", "📸 شيف الثلاجة", "📊 متتبع السعرات"]
    prof_txt = {"title": "👤 الملف الشخصي", "gender": "الجنس", "male": "ذكر", "female": "أنثى", "age": "العمر", "height": "الطول", "weight": "الوزن", "target": "الهدف", "act": "النشاط", "calc": "احسب 🚀", "res_cal": "السعرات المستهدفة", "res_prot": "البروتين المستهدف", "advice": "💡 نصيحة"}
    act_lvls = ["خامل", "نشط قليلاً", "نشط متوسط", "نشط جداً"]
    chef_txt = {"goals": ["👨‍🍳 قياسي", "🥗 صحي", "💪 رياضي"], "upload": "تحميل صورة", "btn": "تحليل! 🚀", "res": "✅ النتيجة:"}
    track_txt = {"title": "📊 التتبع", "add": "➕ إضافة", "meal": "وجبة", "food": "طعام", "portion": "الكمية", "calc_ai": "✨ حساب ذكي", "save": "حفظ 💾", "sum": "📅 ملخص", "reset": "🗑️ إعادة تعيين"}
    meals = ["إفطار", "غداء", "عشاء", "وجبة خفيفة"]

else: # Varsayılan Türkçe
    menu_title = "📱 Menü"
    nav_options = ["👤 Profil & Hedef", "📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]
    prof_txt = {"title": "👤 Profil & Hedef Belirleme", "gender": "Cinsiyet", "male": "Erkek", "female": "Kadın", "age": "Yaş", "height": "Boy (cm)", "weight": "Kilo (kg)", "target": "Hedef Kilo (kg)", "act": "Hareket Seviyesi", "calc": "Hesapla & Planla 🚀", "res_cal": "GÜNLÜK KALORİ HEDEFİ", "res_prot": "GÜNLÜK PROTEİN HEDEFİ", "advice": "💡 Yapay Zeka Koç Tavsiyesi"}
    act_lvls = ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli"]
    chef_txt = {"goals": ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"], "upload": "Resim Yükle", "btn": "Analiz Et! 🚀", "res": "✅ Sonuç:"}
    track_txt = {"title": "📊 Günlük Takip", "add": "➕ Ne Yedin?", "meal": "Öğün Seç", "food": "Yemek Seç / Ara", "portion": "Porsiyon / Adet", "calc_ai": "✨ Değerleri AI ile Getir", "save": "Listeye Ekle 💾", "sum": "📅 Gün Özeti", "reset": "🗑️ Günü Sıfırla"}
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]

st.sidebar.title(menu_title)
secilen_sayfa = st.sidebar.radio("", nav_options)

# ==========================================================
# SAYFA 1: PROFİL & HEDEF (KİŞİSEL PLAN)
# ==========================================================
if secilen_sayfa == nav_options[0]:
    st.title(prof_txt["title"])
    
    col1, col2 = st.columns(2)
    with col1:
        cinsiyet = st.radio(prof_txt["gender"], [prof_txt["male"], prof_txt["female"]], horizontal=True)
        yas = st.number_input(prof_txt["age"], 10, 100, 25)
        boy = st.number_input(prof_txt["height"], 100, 250, 175)
    with col2:
        kilo = st.number_input(prof_txt["weight"], 30.0, 200.0, 70.0)
        hedef_kilo = st.number_input(prof_txt["target"], 30.0, 200.0, 70.0)
        aktivite = st.selectbox(prof_txt["act"], act_lvls)

    if st.button(prof_txt["calc"], type="primary"):
        # Matematiksel Hesaplama (Mifflin-St Jeor)
        bmr = (10 * kilo) + (6.25 * boy) - (5 * yas) + (5 if cinsiyet == prof_txt["male"] else -161)
        katsayi = [1.2, 1.375, 1.55, 1.725][act_lvls.index(aktivite)]
        tdee = bmr * katsayi
        
        # Hedef Belirleme
        if hedef_kilo < kilo: # Zayıflama
            hedef_kalori = tdee - 500
            prot_factor = 1.8
        elif hedef_kilo > kilo: # Kilo Alma
            hedef_kalori = tdee + 400
            prot_factor = 2.0
        else: # Koruma
            hedef_kalori = tdee
            prot_factor = 1.4
            
        hedef_protein = kilo * prot_factor

        st.divider()
        c1, c2 = st.columns(2)
        c1.metric(prof_txt["res_cal"], f"{int(hedef_kalori)} kcal")
        c2.metric(prof_txt["res_prot"], f"{int(hedef_protein)} gr")
        
        # Yapay Zeka Tavsiyesi
        st.subheader(prof_txt["advice"])
        with st.spinner("..."):
            prompt = f"User: {yas} years, {kilo}kg, {boy}cm. Goal: {kilo}->{hedef_kilo}kg. Calculated Calorie Target: {int(hedef_kalori)}. Give motivation and diet roadmap in {secilen_dil}."
            try:
                advice = model.generate_content(prompt).text
                st.success(advice)
            except: st.error("AI Error")

# ==========================================================
# SAYFA 2: BUZDOLABI ŞEFİ (TARİF & ANALİZ)
# ==========================================================
elif secilen_sayfa == nav_options[1]:
    st.title(nav_options[1])
    
    # Hedef Modu Seçimi
    sef_modu = st.sidebar.radio("Mode", chef_txt["goals"])
    
    # Resim Yükleme
    yuklenen_resim = st.file_uploader(chef_txt["upload"], type=["jpg", "jpeg", "png"])
    
    if yuklenen_resim is not None:
        image = PIL.Image.open(yuklenen_resim)
        st.image(image, caption='...', use_column_width=True)
        
        if st.button(chef_txt["btn"], type="primary"):
            with st.spinner("AI thinking..."):
                try:
                    prompt = f"Analyze fridge photo. Language: {secilen_dil}. User Goal: {sef_modu}. Output: Recipes + Macro Nutrients (Calories, Protein, Carb, Fat) in a colored box."
                    cevap = model.generate_content([prompt, image])
                    st.success(chef_txt["res"])
                    st.markdown(cevap.text, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================================
# SAYFA 3: KALORİ TAKİBİ (AKILLI HESAPLAMA)
# ==========================================================
elif secilen_sayfa == nav_options[2]:
    st.title(track_txt["title"])
    
    veri_tabani = verileri_yukle()
    tarih_str = str(st.date_input("📅", date.today()))
    if tarih_str not in veri_tabani: veri_tabani[tarih_str] = {"1": [], "2": [], "3": [], "4": []}
    gunluk_veri = veri_tabani[tarih_str]
    
    st.subheader(track_txt["add"])
    
    # Session State (Hafıza)
    if 'cal' not in st.session_state: st.session_state['cal'] = 0
    if 'pro' not in st.session_state: st.session_state['pro'] = 0
    if 'carb' not in st.session_state: st.session_state['carb'] = 0
    if 'fat' not in st.session_state: st.session_state['fat'] = 0
    
    col1, col2 = st.columns([1,1])
    
    with col1:
        ogun = st.selectbox(track_txt["meal"], meals)
        ogun_id = str(meals.index(ogun) + 1)
        
        # Dile göre yemek listesi
        aktif_liste = YEMEK_SOZLUGU.get(secilen_dil, YEMEK_SOZLUGU["Türkçe"])
        yemek = st.selectbox(track_txt["food"], aktif_liste)
        miktar = st.number_input(track_txt["portion"], 0.5, 10.0, 1.0, 0.5)
        
        if st.button(track_txt["calc_ai"]):
            with st.spinner("..."):
                try:
                    prm = f"Calculate macros for {miktar} portion of '{yemek}'. Output ONLY numbers: Calorie,Protein,Carb,Fat (e.g. 500,30,40,20)."
                    res = model.generate_content(prm).text.strip().split(',')
                    st.session_state['cal'] = int(float(res[0]))
                    st.session_state['pro'] = int(float(res[1]))
                    st.session_state['carb'] = int(float(res[2]))
                    st.session_state['fat'] = int(float(res[3]))
                    st.success("OK!")
                except: st.error("AI Error")
                
    with col2:
        cal = st.number_input("Kcal", value=st.session_state['cal'])
        pro = st.number_input("Protein (g)", value=st.session_state['pro'])
        carb = st.number_input("Carb (g)", value=st.session_state['carb'])
        fat = st.number_input("Fat (g)", value=st.session_state['fat'])
        
    if st.button(track_txt["save"], type="primary"):
        gunluk_veri[ogun_id].append({"yemek": f"{miktar}x {yemek}", "kalori": cal, "protein": pro, "karbon": carb, "yag": fat})
        veri_tabani[tarih_str] = gunluk_veri
        veriyi_kaydet(veri_tabani)
        st.session_state['cal'] = 0
        st.rerun()

    st.divider()
    st.subheader(track_txt["sum"])
    
    top_cal = sum(x['kalori'] for k in gunluk_veri for x in gunluk_veri[k])
    top_pro = sum(x['protein'] for k in gunluk_veri for x in gunluk_veri[k])
    
    k1, k2 = st.columns(2)
    k1.metric("🔥 Kcal", top_cal)
    k2.metric("🥩 Protein", f"{top_pro}g")
    
    for i, m in enumerate(meals):
        kod = str(i+1)
        if gunluk_veri[kod]:
            st.markdown(f"**{m}**")
            for y in gunluk_veri[kod]:
                st.text(f"- {y['yemek']}: {y['kalori']} kcal")
                
    if st.button(track_txt["reset"]):
        del veri_tabani[tarih_str]
        veriyi_kaydet(veri_tabani)
        st.rerun()