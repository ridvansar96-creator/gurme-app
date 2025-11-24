import streamlit as st
import google.generativeai as genai
import PIL.Image
import json
import os
from datetime import datetime

# ==========================================================
# 1. AYARLAR VE GÜVENLİK
# ==========================================================
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ API Anahtarı bulunamadı!")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================================
# 2. LOGLAMA VE VERİ
# ==========================================================
LOG_DOSYASI = "sistem_loglari.json"
DOSYA_ADI = "kalori_takibi.json"

# YEMEK LİSTESİ
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

def log_kaydet(islem, detay):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yeni = {"zaman": zaman, "islem": islem, "detay": detay}
    logs = []
    if os.path.exists(LOG_DOSYASI):
        try:
            with open(LOG_DOSYASI, "r", encoding="utf-8") as f: logs = json.load(f)
        except: pass
    logs.append(yeni)
    with open(LOG_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)

# Makyaj
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
# 3. DİL VE MENÜ AYARLARI
# ==========================================================
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

# Gizli Admin Girişi (?patron=1)
if "patron" in st.query_params:
    with st.sidebar.expander("🔒 Admin"):
        if st.text_input("Pass", type="password") == st.secrets.get("admin_password", ""):
            st.session_state['is_admin'] = True
            st.sidebar.success("OK!")

# --- DİL SÖZLÜĞÜ (BURASI DÜZELTİLDİ) ---
if secilen_dil == "English":
    menu_t = "📱 Menu"
    nav = ["👤 Profile", "📸 Chef", "📊 Tracker"]
    prof = {"ti": "👤 Profile", "gen": "Gender", "m": "Male", "f": "Female", "age": "Age", "h": "Height (cm)", "w": "Weight (kg)", "tar": "Target (kg)", "act": "Activity", "btn": "Calculate 🚀", "adv": "💡 AI Advice"}
    chef = {"goals": ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"], "up": "Upload", "btn": "Analyze! 🚀", "res": "✅ Result:"}
    track = {"ti": "📊 Tracker", "add": "➕ Add", "meal": "Meal", "food": "Food", "por": "Portion", "ai": "✨ AI Calc", "save": "Save 💾", "sum": "Summary"}
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    acts = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]

elif secilen_dil == "Deutsch":
    menu_t = "📱 Menü"
    nav = ["👤 Profil", "📸 Chef", "📊 Tracker"]
    prof = {"ti": "👤 Profil", "gen": "Geschlecht", "m": "Männlich", "f": "Weiblich", "age": "Alter", "h": "Größe (cm)", "w": "Gewicht (kg)", "tar": "Ziel (kg)", "act": "Aktivität", "btn": "Berechnen 🚀", "adv": "💡 KI-Rat"}
    chef = {"goals": ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"], "up": "Bild hochladen", "btn": "Analysieren! 🚀", "res": "✅ Ergebnis:"}
    track = {"ti": "📊 Tracker", "add": "➕ Mahlzeit", "meal": "Mahlzeit", "food": "Essen", "por": "Portion", "ai": "✨ KI-Calc", "save": "Speichern 💾", "sum": "Zusammenfassung"}
    meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
    acts = ["Sitzend", "Leicht aktiv", "Mäßig aktiv", "Sehr aktiv"]

elif secilen_dil == "Français":
    menu_t = "📱 Menu"
    nav = ["👤 Profil", "📸 Chef", "📊 Suivi"]
    prof = {"ti": "👤 Profil", "gen": "Genre", "m": "Homme", "f": "Femme", "age": "Âge", "h": "Taille", "w": "Poids", "tar": "Objectif", "act": "Activité", "btn": "Calculer 🚀", "adv": "💡 Conseil IA"}
    chef = {"goals": ["👨‍🍳 Standard", "🥗 Diététicien", "💪 Athlète"], "up": "Image", "btn": "Analyser! 🚀", "res": "✅ Résultat:"}
    track = {"ti": "📊 Suivi", "add": "➕ Ajouter", "meal": "Repas", "food": "Aliment", "por": "Portion", "ai": "✨ Calcul IA", "save": "Ajouter 💾", "sum": "Résumé"}
    meals = ["Petit-déj", "Déjeuner", "Dîner", "Collation"]
    acts = ["Sédentaire", "Légèrement actif", "Modérément actif", "Très actif"]

elif secilen_dil == "العربية":
    menu_t = "📱 القائمة"
    nav = ["👤 الملف الشخصي", "📸 شيف الثلاجة", "📊 التتبع"]
    prof = {"ti": "👤 الملف الشخصي", "gen": "الجنس", "m": "ذكر", "f": "أنثى", "age": "العمر", "h": "الطول", "w": "الوزن", "tar": "الهدف", "act": "النشاط", "btn": "احسب 🚀", "adv": "💡 نصيحة"}
    chef = {"goals": ["👨‍🍳 قياسي", "🥗 صحي", "💪 رياضي"], "up": "صورة", "btn": "تحليل! 🚀", "res": "✅ النتيجة:"}
    track = {"ti": "📊 التتبع", "add": "➕ إضافة", "meal": "وجبة", "food": "طعام", "por": "الكمية", "ai": "✨ حساب ذكي", "save": "حفظ 💾", "sum": "ملخص"}
    meals = ["إفطار", "غداء", "عشاء", "وجبة خفيفة"]
    acts = ["خامل", "نشط قليلاً", "نشط متوسط", "نشط جداً"]

else: # Türkçe
    menu_t = "📱 Menü"
    nav = ["👤 Profil & Hedef", "📸 Buzdolabı Şefi", "📊 Kalori Takibi"]
    prof = {"ti": "👤 Profil & Hedef", "gen": "Cinsiyet", "m": "Erkek", "f": "Kadın", "age": "Yaş", "h": "Boy (cm)", "w": "Kilo (kg)", "tar": "Hedef (kg)", "act": "Hareket", "btn": "Hesapla 🚀", "adv": "💡 AI Tavsiyesi"}
    chef = {"goals": ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"], "up": "Resim Yükle", "btn": "Analiz Et! 🚀", "res": "✅ Sonuç:"}
    track = {"ti": "📊 Günlük Takip", "add": "➕ Ne Yedin?", "meal": "Öğün", "food": "Yemek", "por": "Porsiyon", "ai": "✨ AI ile Hesapla", "save": "Ekle 💾", "sum": "Gün Özeti"}
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
    acts = ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli"]

if st.session_state.get('is_admin'): nav.append("🕵️‍♂️ ADMİN")

st.sidebar.title(menu_t)
page = st.sidebar.radio("", nav)

# ==========================================================
# SAYFA 1: PROFİL (Cinsiyet Düzeltildi)
# ==========================================================
if page == nav[0]:
    st.title(prof["ti"])
    c1, c2 = st.columns(2)
    with c1:
        # BURASI DÜZELDİ: Artık değişken kullanıyor
        cin = st.radio(prof["gen"], [prof["m"], prof["f"]], horizontal=True)
        yas = st.number_input(prof["age"], 10, 100, 25)
        boy = st.number_input(prof["h"], 100, 250, 175)
    with c2:
        kilo = st.number_input(prof["w"], 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        hedef = st.number_input(prof["tar"], 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        akt = st.selectbox(prof["act"], acts)
    
    if st.button(prof["btn"], type="primary"):
        log_kaydet("Profil", f"{yas}y, {kilo}->{hedef}kg")
        bmr = 10*kilo + 6.25*boy - 5*yas + (5 if cin == prof["m"] else -161)
        tdee = bmr * [1.2, 1.375, 1.55, 1.725][acts.index(akt)]
        
        target_cal = tdee - 500 if hedef < kilo else (tdee + 400 if hedef > kilo else tdee)
        
        st.metric("Target Kcal", int(target_cal))
        with st.spinner("AI..."):
            try:
                res = model.generate_content(f"Diet plan for {yas}y, {kilo}kg to {hedef}kg. Lang: {secilen_dil}").text
                st.info(res)
            except: pass

# ==========================================================
# SAYFA 2: ŞEF
# ==========================================================
elif page == nav[1]:
    st.title(nav[1])
    mod = st.sidebar.radio("Mode", chef["goals"])
    img = st.file_uploader(chef["up"], type=["jpg","png","jpeg"])
    
    if img and st.button(chef["btn"], type="primary"):
        log_kaydet("Foto", str(mod))
        with st.spinner("..."):
            try:
                prm = f"Analyze fridge. Lang: {secilen_dil}. Goal: {mod}. Include Macros."
                res = model.generate_content([prm, PIL.Image.open(img)])
                st.markdown(res.text, unsafe_allow_html=True)
            except: pass

# ==========================================================
# SAYFA 3: TAKİP
# ==========================================================
elif page == nav[2]:
    st.title(track["ti"])
    db = verileri_yukle()
    d_str = str(st.date_input("📅", datetime.today()))
    if d_str not in db: db[d_str] = {"1":[],"2":[],"3":[],"4":[]}
    
    st.subheader(track["add"])
    if 'cal' not in st.session_state: st.session_state.update({'cal':0,'pro':0,'carb':0,'fat':0})
    
    c1, c2 = st.columns([1,1])
    with c1:
        ogun = st.selectbox(track["meal"], meals)
        oid = str(meals.index(ogun)+1)
        # Yemek listesi dile göre geliyor
        liste = YEMEK_SOZLUGU.get(secilen_dil, YEMEK_SOZLUGU["Türkçe"])
        ymk = st.selectbox(track["food"], liste)
        mik = st.number_input(track["por"], 0.5, 10.0, 1.0, 0.5)
        
        if st.button(track["ai"]):
            try:
                res = model.generate_content(f"Macros for {mik}x {ymk}. Only numbers: Cal,Pro,Carb,Fat").text.strip().split(',')
                st.session_state['cal'] = int(float(res[0]))
                st.session_state['pro'] = int(float(res[1]))
                st.session_state['carb'] = int(float(res[2]))
                st.session_state['fat'] = int(float(res[3]))
            except: pass
            
    with c2:
        cal = st.number_input("Kcal", value=st.session_state['cal'])
        pro = st.number_input("Pro", value=st.session_state['pro'])
        carb = st.number_input("Carb", value=st.session_state['carb'])
        fat = st.number_input("Fat", value=st.session_state['fat'])
        
    if st.button(track["save"], type="primary"):
        db[d_str][oid].append({"yemek":f"{mik}x {ymk}","kalori":cal,"protein":pro,"karbon":carb,"yag":fat})
        veriyi_kaydet(db)
        st.session_state['cal']=0
        st.rerun()

    st.divider()
    st.subheader(track["sum"])
    t_cal = sum(x['kalori'] for k in db[d_str] for x in db[d_str][k])
    st.metric("Total", t_cal)
    
    for i,m in enumerate(meals):
        if db[d_str][str(i+1)]:
            st.text(m)
            for y in db[d_str][str(i+1)]: st.caption(f"{y['yemek']} - {y['kalori']} kcal")

# ==========================================================
# SAYFA 4: ADMİN
# ==========================================================
elif st.session_state.get('is_admin') and page == "🕵️‍♂️ ADMİN":
    st.title("🕵️‍♂️ Admin Panel")
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI,"r",encoding="utf-8") as f: st.dataframe(json.load(f)[::-1])