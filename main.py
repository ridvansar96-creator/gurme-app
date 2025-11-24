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
# 2. LOGLAMA SİSTEMİ (CASUSLUK)
# ==========================================================
LOG_DOSYASI = "sistem_loglari.json"

def log_kaydet(islem, detay):
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yeni_kayit = {"zaman": zaman, "islem": islem, "detay": detay}
    kayitlar = []
    if os.path.exists(LOG_DOSYASI):
        try:
            with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
        except: pass
    kayitlar.append(yeni_kayit)
    with open(LOG_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=4)

# ==========================================================
# 3. VERİ FONKSİYONLARI
# ==========================================================
DOSYA_ADI = "kalori_takibi.json"
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
# 4. YAN MENÜ
# ==========================================================
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

# --- GİZLİ KAPI MANTIĞI ---
# Sadece linkin sonunda ?patron=1 varsa kutuyu gösterir
query_params = st.query_params
is_admin = False

if "patron" in query_params:
    with st.sidebar.expander("🔒 Yönetici Girişi"):
        admin_pass = st.text_input("Şifre", type="password")
        if "admin_password" in st.secrets:
            if admin_pass == st.secrets["admin_password"]:
                is_admin = True
                st.sidebar.success("Giriş Başarılı!")

# METİNLER
if secilen_dil == "English":
    menu_title, nav_options = "📱 Menu", ["👤 Profile & Goals", "📸 Fridge Chef", "📊 Calorie Tracker"]
    prof_txt = {"title": "👤 Profile", "calc": "Calculate 🚀", "advice": "💡 AI Advice"}
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"], "upload": "Upload", "btn": "Analyze! 🚀"}
    track_txt = {"title": "📊 Tracker", "add": "➕ Add Meal", "meal": "Meal", "food": "Food", "portion": "Portion", "calc_ai": "✨ AI Calc", "save": "Save 💾"}
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    act_lvls = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
    txt_gender, txt_age, txt_weight, txt_height, txt_target = "Gender", "Age", "Weight", "Height", "Target"
    
elif secilen_dil == "Deutsch":
    menu_title, nav_options = "📱 Menü", ["👤 Profil & Ziele", "📸 Kühlschrank-Chef", "📊 Kalorien-Tracker"]
    prof_txt = {"title": "👤 Profil", "calc": "Berechnen 🚀", "advice": "💡 KI-Rat"}
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"], "upload": "Bild hochladen", "btn": "Analysieren! 🚀"}
    track_txt = {"title": "📊 Tracker", "add": "➕ Mahlzeit", "meal": "Mahlzeit", "food": "Essen", "portion": "Portion", "calc_ai": "✨ KI-Berechnung", "save": "Speichern 💾"}
    meals = ["Frühstück", "Mittagessen", "Abendessen", "Snack"]
    act_lvls = ["Sitzend", "Leicht aktiv", "Mäßig aktiv", "Sehr aktiv"]
    txt_gender, txt_age, txt_weight, txt_height, txt_target = "Geschlecht", "Alter", "Gewicht", "Größe", "Ziel"

else: # Türkçe
    menu_title, nav_options = "📱 Menü", ["👤 Profil & Hedef", "📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]
    prof_txt = {"title": "👤 Profil & Hedef", "calc": "Hesapla & Planla 🚀", "advice": "💡 Yapay Zeka Tavsiyesi"}
    chef_txt = {"goals": ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"], "upload": "Resim Yükle", "btn": "Analiz Et! 🚀"}
    track_txt = {"title": "📊 Günlük Takip", "add": "➕ Ne Yedin?", "meal": "Öğün Seç", "food": "Yemek Seç", "portion": "Porsiyon", "calc_ai": "✨ AI ile Hesapla", "save": "Listeye Ekle 💾"}
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
    act_lvls = ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli"]
    txt_gender, txt_age, txt_weight, txt_height, txt_target = "Cinsiyet", "Yaş", "Kilo", "Boy", "Hedef"

if is_admin:
    nav_options.append("🕵️‍♂️ ADMİN PANELİ")

st.sidebar.title(menu_title)
secilen_sayfa = st.sidebar.radio("", nav_options)

# ==========================================================
# SAYFA 4: ADMİN PANELİ (GİZLİ)
# ==========================================================
if is_admin and secilen_sayfa == "🕵️‍♂️ ADMİN PANELİ":
    st.title("🕵️‍♂️ Patron Paneli")
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f: loglar = json.load(f)
        st.dataframe(loglar[::-1], use_container_width=True)
        st.metric("Toplam Hareket", len(loglar))
        if st.button("Logları Sil"):
            os.remove(LOG_DOSYASI)
            st.rerun()
    else: st.info("Hareket yok.")

# ==========================================================
# SAYFA 1: PROFİL
# ==========================================================
elif secilen_sayfa == nav_options[0]:
    st.title(prof_txt["title"])
    c1, c2 = st.columns(2)
    with c1:
        cin = st.radio(txt_gender, ["Male/Erkek", "Female/Kadın"], horizontal=True)
        yas = st.number_input(txt_age, 10, 100, 25)
        boy = st.number_input(txt_height, 100, 250, 175)
    with c2:
        kilo = st.number_input(txt_weight, 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        hedef = st.number_input(txt_target, 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        akt = st.selectbox("Activity", act_lvls)
    
    if st.button(prof_txt["calc"], type="primary"):
        log_kaydet("Profil Hesaplama", f"{yas}y, {kilo}kg -> {hedef}kg")
        
        # Basit BMR Hesaplama (Gösterim Amaçlı)
        bmr = 10*kilo + 6.25*boy - 5*yas + 5
        tdee = bmr * 1.4
        
        st.success(f"Günlük İhtiyaç: {int(tdee)} kcal")
        
        with st.spinner("AI..."):
            try:
                prompt = f"Diet plan for {yas} years, {kilo}kg to {hedef}kg. Lang: {secilen_dil}"
                res = model.generate_content(prompt).text
                st.info(res)
            except: pass

# ==========================================================
# SAYFA 2: ŞEF
# ==========================================================
elif secilen_sayfa == nav_options[1]:
    st.title(nav_options[1])
    mod = st.sidebar.radio("Mode", chef_txt["goals"])
    img = st.file_uploader(chef_txt["upload"], type=["jpg","png","jpeg"])
    
    if img and st.button(chef_txt["btn"], type="primary"):
        log_kaydet("Foto Analizi", str(mod))
        with st.spinner("AI..."):
            try:
                prompt = f"Analyze fridge. Lang: {secilen_dil}. Goal: {mod}. Add Macros box."
                res = model.generate_content([prompt, PIL.Image.open(img)])
                st.markdown(res.text, unsafe_allow_html=True)
            except: pass

# ==========================================================
# SAYFA 3: TAKİP
# ==========================================================
elif secilen_sayfa == nav_options[2]:
    st.title(track_txt["title"])
    db = verileri_yukle()
    date_str = str(st.date_input("📅", datetime.today()))
    if date_str not in db: db[date_str] = {"1":[],"2":[],"3":[],"4":[]}
    
    st.subheader(track_txt["add"])
    if 'cal' not in st.session_state: st.session_state.update({'cal':0,'pro':0,'carb':0,'fat':0})
    
    c1, c2 = st.columns([1,1])
    with c1:
        ogun = st.selectbox(track_txt["meal"], meals)
        oid = str(meals.index(ogun)+1)
        liste = YEMEK_SOZLUGU.get(secilen_dil, YEMEK_SOZLUGU["Türkçe"])
        ymk = st.selectbox(track_txt["food"], liste)
        mik = st.number_input(track_txt["portion"], 0.5, 10.0, 1.0, 0.5)
        
        if st.button(track_txt["calc_ai"]):
            log_kaydet("Kalori Sorgu", f"{ymk} x {mik}")
            try:
                res = model.generate_content(f"Calculate macros for {mik}x {ymk}. Numbers only: Cal,Pro,Carb,Fat").text.strip().split(',')
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
        
    if st.button(track_txt["save"], type="primary"):
        log_kaydet("Yemek Kayıt", f"{ymk}")
        db[date_str][oid].append({"yemek":f"{mik}x {ymk}","kalori":cal,"protein":pro,"karbon":carb,"yag":fat})
        veriyi_kaydet(db)
        st.session_state['cal']=0
        st.rerun()

    st.divider()
    top_cal = sum(x['kalori'] for k in db[date_str] for x in db[date_str][k])
    st.metric("Total Kcal", top_cal)
    
    # Listeleme
    for i,m in enumerate(meals):
        if db[date_str][str(i+1)]:
            st.text(m)
            for y in db[date_str][str(i+1)]: st.caption(f"{y['yemek']} - {y['kalori']} kcal")