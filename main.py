import streamlit as st
import google.generativeai as genai
import PIL.Image
import json
import os
from datetime import datetime

# ==========================================================
# 1. AYARLAR VE GÜVENLİK
# ==========================================================
st.set_page_config(page_title="Gurme Chef AI", page_icon="👨‍🍳", layout="wide")

if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ API Key Not Found! Check Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================================
# 2. LOGLAMA VE VERİ
# ==========================================================
LOG_DOSYASI = "system_logs.json"
DOSYA_ADI = "user_data.json"

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

# --- ATOM BOMBASI MAKYAJI (KESİN ÇÖZÜM) ---
hide_streamlit_style = """
<style>
    /* 1. Sağ Üstteki GitHub ve Seçenekler Menüsünü (Toolbar) KOMPLE YOK ET */
    [data-testid="stToolbar"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* 2. Alt Bilgiyi (Footer) YOK ET */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 3. Sağ Alttaki Kırmızı/Gri Yönetici Butonlarını YOK ET */
    .stDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    div[class*="viewerBadge"] {display:none !important;}
    
    /* 4. Üstteki Renkli Gökkuşağı Çizgisini YOK ET */
    [data-testid="stDecoration"] {display:none !important;}

    /* 5. Sol Üstteki Menü Butonuna DOKUNMA (Bu yüzden header'ı gizlemiyoruz) */
    
    /* 6. Mobilde üst boşluğu ayarla */
    .block-container {
        padding-top: 1rem;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ==========================================================
# 3. YAN MENÜ VE AYARLAR
# ==========================================================
st.sidebar.title("🌐 Language")
secilen_dil = st.sidebar.selectbox("Select", ["English", "Türkçe", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

if "patron" in st.query_params:
    with st.sidebar.expander("🔒 Admin Login"):
        if st.text_input("Password", type="password") == st.secrets.get("admin_password", ""):
            st.session_state['is_admin'] = True
            st.sidebar.success("Access Granted!")

# DİL AYARLARI
if secilen_dil == "English":
    menu_t = "📱 Menu"
    nav = ["👤 My Profile", "👨‍🍳 Gurme Chef AI", "📊 NutriTracker"]
    prof = {"ti": "👤 User Profile", "gen": "Gender", "m": "Male", "f": "Female", "age": "Age", "h": "Height (cm)", "w": "Weight (kg)", "tar": "Target Weight", "act": "Activity", "btn": "Create Plan 🚀", "adv": "💡 AI Coach Advice"}
    chef = {"goals": ["👨‍🍳 Standard Chef", "🥗 Diet Expert", "💪 Fitness Coach"], "up": "Upload Food Photo", "btn": "Gurme Analysis 🚀", "res": "✅ Gurme Chef Says:"}
    track = {"ti": "📊 NutriTracker", "add": "➕ Add Log", "meal": "Meal", "food": "Food Item", "por": "Portion", "ai": "✨ AI Estimate", "save": "Save Log 💾", "sum": "Daily Summary"}
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    acts = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]

elif secilen_dil == "Deutsch":
    menu_t = "📱 Menü"
    nav = ["👤 Mein Profil", "👨‍🍳 Gurme Chef KI", "📊 NutriTracker"]
    prof = {"ti": "👤 Benutzerprofil", "gen": "Geschlecht", "m": "Männlich", "f": "Weiblich", "age": "Alter", "h": "Größe", "w": "Gewicht", "tar": "Zielgewicht", "act": "Aktivität", "btn": "Plan erstellen 🚀", "adv": "💡 KI-Rat"}
    chef = {"goals": ["👨‍🍳 Standard", "🥗 Diät-Experte", "💪 Fitness-Coach"], "up": "Foto hochladen", "btn": "KI-Analyse 🚀", "res": "✅ Gurme Chef Ergebnis:"}
    track = {"ti": "📊 NutriTracker", "add": "➕ Hinzufügen", "meal": "Mahlzeit", "food": "Essen", "por": "Portion", "ai": "✨ KI-Schätzung", "save": "Speichern 💾", "sum": "Zusammenfassung"}
    meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
    acts = ["Sitzend", "Leicht aktiv", "Mäßig aktiv", "Sehr aktiv"]

elif secilen_dil == "Français":
    menu_t = "📱 Menu"
    nav = ["👤 Mon Profil", "👨‍🍳 Gurme Chef IA", "📊 NutriTracker"]
    prof = {"ti": "👤 Profil Utilisateur", "gen": "Genre", "m": "Homme", "f": "Femme", "age": "Âge", "h": "Taille", "w": "Poids", "tar": "Cible", "act": "Activité", "btn": "Créer un plan 🚀", "adv": "💡 Conseil IA"}
    chef = {"goals": ["👨‍🍳 Standard", "🥗 Expert Régime", "💪 Coach Fitness"], "up": "Télécharger photo", "btn": "Analyse IA 🚀", "res": "✅ Résultat Gurme Chef:"}
    track = {"ti": "📊 NutriTracker", "add": "➕ Ajouter", "meal": "Repas", "food": "Aliment", "por": "Portion", "ai": "✨ Estim. IA", "save": "Sauvegarder 💾", "sum": "Résumé"}
    meals = ["Petit-déj", "Déjeuner", "Dîner", "Collation"]
    acts = ["Sédentaire", "Légèrement actif", "Modérément actif", "Très actif"]

elif secilen_dil == "العربية":
    menu_t = "📱 القائمة"
    nav = ["👤 الملف الشخصي", "👨‍🍳 شيف جورميه", "📊 متتبع الغذاء"]
    prof = {"ti": "👤 الملف الشخصي", "gen": "الجنس", "m": "ذكر", "f": "أنثى", "age": "العمر", "h": "الطول", "w": "الوزن", "tar": "الهدف", "act": "النشاط", "btn": "إنشاء خطة 🚀", "adv": "💡 نصيحة الذكاء الاصطناعي"}
    chef = {"goals": ["👨‍🍳 قياسي", "🥗 خبير تغذية", "💪 مدرب لياقة"], "up": "رفع صورة", "btn": "تحليل ذكي 🚀", "res": "✅ نتيجة الشيف:"}
    track = {"ti": "📊 متتبع الغذاء", "add": "➕ إضافة", "meal": "وجبة", "food": "طعام", "por": "الكمية", "ai": "✨ تقدير ذكي", "save": "حفظ 💾", "sum": "ملخص"}
    meals = ["إفطار", "غداء", "عشاء", "وجبة خفيفة"]
    acts = ["خامل", "نشط قليلاً", "نشط متوسط", "نشط جداً"]

else: # Türkçe
    menu_t = "📱 Menü"
    nav = ["👤 Profilim", "👨‍🍳 Gurme Chef AI", "📊 NutriTracker"]
    prof = {"ti": "👤 Kullanıcı Profili", "gen": "Cinsiyet", "m": "Erkek", "f": "Kadın", "age": "Yaş", "h": "Boy (cm)", "w": "Kilo (kg)", "tar": "Hedef (kg)", "act": "Hareket", "btn": "Plan Oluştur 🚀", "adv": "💡 AI Koç Tavsiyesi"}
    chef = {"goals": ["👨‍🍳 Standart Şef", "🥗 Diyet Uzmanı", "💪 Fitness Koçu"], "up": "Yemek/Dolap Fotosu Yükle", "btn": "AI ile Analiz Et 🚀", "res": "✅ Gurme Chef Sonucu:"}
    track = {"ti": "📊 NutriTracker (Takip)", "add": "➕ Öğün Ekle", "meal": "Öğün", "food": "Yemek Seç", "por": "Porsiyon", "ai": "✨ AI ile Hesapla", "save": "Kaydet 💾", "sum": "Günlük Özet"}
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
    acts = ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli"]

if st.session_state.get('is_admin'): nav.append("🕵️‍♂️ ADMIN PANEL")

st.sidebar.title(menu_t)
page = st.sidebar.radio("", nav)

# ==========================================================
# SAYFA 1: PROFİL
# ==========================================================
if page == nav[0]:
    st.title(prof["ti"])
    c1, c2 = st.columns(2)
    with c1:
        cin = st.radio(prof["gen"], [prof["m"], prof["f"]], horizontal=True)
        yas = st.number_input(prof["age"], 10, 100, 25)
        boy = st.number_input(prof["h"], 100, 250, 175)
    with c2:
        kilo = st.number_input(prof["w"], 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        hedef = st.number_input(prof["tar"], 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        akt = st.selectbox(prof["act"], acts)
    
    if st.button(prof["btn"], type="primary"):
        log_kaydet("Profile Update", f"{yas}y, {kilo}->{hedef}kg")
        bmr = 10*kilo + 6.25*boy - 5*yas + (5 if cin == prof["m"] else -161)
        tdee = bmr * [1.2, 1.375, 1.55, 1.725][acts.index(akt)]
        target = tdee - 500 if hedef < kilo else (tdee + 400 if hedef > kilo else tdee)
        
        st.metric("Daily Calorie Target", int(target))
        with st.spinner("AI Generating Plan..."):
            try:
                res = model.generate_content(f"Create a diet roadmap. User: {yas}y, {kilo}kg, Goal: {hedef}kg. Lang: {secilen_dil}").text
                st.info(res)
            except: pass

# ==========================================================
# SAYFA 2: GURME CHEF
# ==========================================================
elif page == nav[1]:
    st.title(nav[1])
    mod = st.sidebar.radio("AI Mode", chef["goals"])
    img = st.file_uploader(chef["up"], type=["jpg","png","jpeg"])
    
    if img:
        st.image(img, caption="Scanning...", use_column_width=True)
        if st.button(chef["btn"], type="primary"):
            log_kaydet("Gurme Scan", str(mod))
            with st.spinner("Gurme Chef AI is analyzing..."):
                try:
                    prm = f"Analyze food image. Lang: {secilen_dil}. Persona: {mod}. Give Recipe & Macros Box."
                    res = model.generate_content([prm, PIL.Image.open(img)])
                    st.success(chef["res"])
                    st.markdown(res.text, unsafe_allow_html=True)
                except: pass

# ==========================================================
# SAYFA 3: NUTRITRACKER
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
        liste = YEMEK_SOZLUGU.get(secilen_dil, YEMEK_SOZLUGU["English"]) 
        ymk = st.selectbox(track["food"], liste)
        mik = st.number_input(track["por"], 0.5, 10.0, 1.0, 0.5)
        
        if st.button(track["ai"]):
            try:
                res = model.generate_content(f"Macros for {mik}x {ymk}. Numbers only: Cal,Pro,Carb,Fat").text.strip().split(',')
                st.session_state['cal'] = int(float(res[0]))
                st.session_state['pro'] = int(float(res[1]))
                st.session_state['carb'] = int(float(res[2]))
                st.session_state['fat'] = int(float(res[3]))
            except: pass
            
    with c2:
        cal = st.number_input("Kcal", value=st.session_state['cal'])
        pro = st.number_input("Protein", value=st.session_state['pro'])
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
    st.metric("Total Kcal", t_cal)
    
    for i,m in enumerate(meals):
        if db[d_str][str(i+1)]:
            st.text(m)
            for y in db[d_str][str(i+1)]: st.caption(f"{y['yemek']} - {y['kalori']} kcal")

# ==========================================================
# SAYFA 4: ADMIN (GİZLİ)
# ==========================================================
elif st.session_state.get('is_admin') and page == "🕵️‍♂️ ADMIN PANEL":
    st.title("🕵️‍♂️ Admin Dashboard")
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI,"r",encoding="utf-8") as f: st.dataframe(json.load(f)[::-1])