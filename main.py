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

# API Anahtarı Kontrolü
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ API Anahtarı bulunamadı! Secrets ayarlarını kontrol et.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================================
# 2. CASUSLUK SİSTEMİ (LOGGING) 🕵️‍♂️
# ==========================================================
LOG_DOSYASI = "sistem_loglari.json"

def log_kaydet(islem, detay):
    """Kullanıcının yaptığı her hareketi kaydeder."""
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    yeni_kayit = {"zaman": zaman, "islem": islem, "detay": detay}
    
    # Mevcut logları yükle
    kayitlar = []
    if os.path.exists(LOG_DOSYASI):
        try:
            with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
                kayitlar = json.load(f)
        except: pass
    
    # Yeni kaydı ekle
    kayitlar.append(yeni_kayit)
    
    # Dosyaya yaz
    with open(LOG_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(kayitlar, f, ensure_ascii=False, indent=4)

# ==========================================================
# 3. DİĞER FONKSİYONLAR
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
# 4. YAN MENÜ VE ADMİN GİRİŞİ
# ==========================================================
st.sidebar.title("🌐 Dil / Language")
secilen_dil = st.sidebar.selectbox("Seç / Select", ["Türkçe", "English", "Deutsch", "Français", "العربية"])
st.sidebar.divider()

# --- GİZLİ ADMİN GİRİŞİ ---
with st.sidebar.expander("🔒 Yönetici / Admin"):
    admin_pass = st.text_input("Şifre", type="password")
    is_admin = False
    if "admin_password" in st.secrets:
        if admin_pass == st.secrets["admin_password"]:
            is_admin = True
            st.success("Hoş geldin Patron! 😎")
        elif admin_pass:
            st.error("Yanlış Şifre!")

# Dil Ayarları (Önceki kodun aynısı)
if secilen_dil == "English":
    menu_title = "📱 Menu"
    nav_options = ["👤 Profile & Goals", "📸 Fridge Chef", "📊 Calorie Tracker"]
    # ... (Diğer metinler yer kaplamasın diye özetlendi, önceki kodla aynı) ...
    prof_txt = {"title": "👤 Profile", "calc": "Calculate Plan 🚀", "advice": "💡 AI Advice"} 
    chef_txt = {"goals": ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"], "upload": "Upload", "btn": "Analyze! 🚀", "res": "✅ Result:"}
    track_txt = {"title": "📊 Tracker", "add": "➕ Add", "meal": "Meal", "food": "Food", "portion": "Portion", "calc_ai": "✨ AI Calc", "save": "Save 💾"}
    meals = ["Breakfast", "Lunch", "Dinner", "Snack"]
    act_lvls = ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
    
else: # Türkçe Varsayılan (Diğer diller de eklenebilir ama kod uzamasın diye özetledim)
    menu_title = "📱 Menü"
    nav_options = ["👤 Profil & Hedef", "📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]
    prof_txt = {"title": "👤 Profil & Hedef", "calc": "Hesapla & Planla 🚀", "advice": "💡 Yapay Zeka Tavsiyesi"}
    chef_txt = {"goals": ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"], "upload": "Resim Yükle", "btn": "Analiz Et! 🚀", "res": "✅ Sonuç:"}
    track_txt = {"title": "📊 Günlük Takip", "add": "➕ Ne Yedin?", "meal": "Öğün Seç", "food": "Yemek Seç", "portion": "Porsiyon", "calc_ai": "✨ AI ile Hesapla", "save": "Listeye Ekle 💾"}
    meals = ["Sabah", "Öğle", "Akşam", "Ara Öğün"]
    act_lvls = ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli"]

# Eğer Admin giriş yaptıysa ek bir seçenek göster!
if is_admin:
    nav_options.append("🕵️‍♂️ ADMİN PANELİ")

st.sidebar.title(menu_title)
secilen_sayfa = st.sidebar.radio("", nav_options)

# ==========================================================
# SAYFA 4: GİZLİ ADMİN PANELİ (YENİ)
# ==========================================================
if is_admin and secilen_sayfa == "🕵️‍♂️ ADMİN PANELİ":
    st.title("🕵️‍♂️ Patronun Kontrol Paneli")
    st.write("Siteye girenlerin ne yaptığını buradan görebilirsin.")
    
    if os.path.exists(LOG_DOSYASI):
        with open(LOG_DOSYASI, "r", encoding="utf-8") as f:
            loglar = json.load(f)
        
        # Logları tersten göster (En yeni en üstte)
        st.dataframe(loglar[::-1], use_container_width=True)
        
        # İstatistikler
        toplam_islem = len(loglar)
        st.metric("Toplam İşlem Sayısı", toplam_islem)
        
        if st.button("🗑️ Logları Temizle"):
            os.remove(LOG_DOSYASI)
            st.rerun()
    else:
        st.info("Henüz bir hareketlilik yok patron.")

# ==========================================================
# SAYFA 1: PROFİL (LOG EKLENDİ)
# ==========================================================
elif secilen_sayfa == nav_options[0]:
    st.title(prof_txt["title"])
    # ... (Giriş inputları buraya gelecek, önceki kodla aynı) ...
    # Kısaltma: Sadece butona basılınca LOG KAYDETME kısmını gösteriyorum
    
    col1, col2 = st.columns(2)
    with col1:
        cinsiyet = st.radio("Cinsiyet/Gender", ["Erkek/Male", "Kadın/Female"], horizontal=True)
        yas = st.number_input("Yaş/Age", 10, 100, 25)
        boy = st.number_input("Boy/Height", 100, 250, 175)
    with col2:
        kilo = st.number_input("Kilo/Weight", 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        hedef = st.number_input("Hedef/Target", 30.0, 200.0, 70.0, step=1.0, format="%.1f")
        akt = st.selectbox("Aktivite/Activity", act_lvls)

    if st.button(prof_txt["calc"], type="primary"):
        # CASUSLUK YAP: Log Kaydet
        log_kaydet("Profil Hesaplama", f"Kullanıcı: {yas}y, {kilo}kg -> {hedef}kg")
        
        # Hesaplama işlemleri...
        st.success("Hesaplandı! (Detaylar önceki kodla aynı)")
        # ... (Önceki matematiksel işlemler buraya gelecek) ...
        
        # AI Tavsiyesi
        with st.spinner("..."):
            prompt = f"Diet plan for {yas} years old, {kilo}kg to {hedef}kg."
            try:
                res = model.generate_content(prompt).text
                st.success(res)
            except: pass

# ==========================================================
# SAYFA 2: BUZDOLABI ŞEFİ (LOG EKLENDİ)
# ==========================================================
elif secilen_sayfa == nav_options[1]:
    st.title(nav_options[1])
    # ...
    mod = st.sidebar.radio("Mode", chef_txt["goals"])
    img = st.file_uploader(chef_txt["upload"], type=["jpg","png","jpeg"])
    
    if img and st.button(chef_txt["btn"], type="primary"):
        # CASUSLUK YAP
        log_kaydet("Fotoğraf Analizi", f"Mod: {mod}")
        
        with st.spinner("..."):
            try:
                prm = f"Analyze fridge. Lang:{secilen_dil}. Goal:{mod}"
                res = model.generate_content([prm, PIL.Image.open(img)])
                st.markdown(res.text, unsafe_allow_html=True)
            except: pass

# ==========================================================
# SAYFA 3: KALORİ TAKİBİ (LOG EKLENDİ)
# ==========================================================
elif secilen_sayfa == nav_options[2]:
    st.title(track_txt["title"])
    # ... (Veritabanı yükleme işlemleri) ...
    # Kısaltma: Sadece butona basılınca LOG KAYDETME kısmını gösteriyorum
    
    st.subheader(track_txt["add"])
    c1, c2 = st.columns(2)
    with c1:
        ymk = st.selectbox(track_txt["food"], YEMEK_SOZLUGU.get("Türkçe")) # Örnek
        mik = st.number_input(track_txt["portion"], 1.0)
        
        if st.button(track_txt["calc_ai"]):
            log_kaydet("Kalori Sorgulama", f"Yemek: {ymk}")
            # ... (AI Hesaplama kodu) ...
            
    with c2:
        # ... (Değerler) ...
        pass
        
    if st.button(track_txt["save"], type="primary"):
        log_kaydet("Yemek Yendi", f"{mik}x {ymk}")
        # ... (Kaydetme kodu) ...
        st.success("Kaydedildi")