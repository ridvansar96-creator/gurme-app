import streamlit as st
import google.generativeai as genai
import PIL.Image
import json
import os
from datetime import date

# --- 1. AYARLAR VE KURULUM ---
st.set_page_config(page_title="Buzdolabı Gurmesi", page_icon="🥗", layout="wide")

# Güvenlik (API Key)
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets ayarlarını kontrol et.")

model = genai.GenerativeModel('gemini-2.5-flash')

# --- 2. VERİ TABANI FONKSİYONLARI (JSON) ---
DOSYA_ADI = "kalori_takibi.json"

def verileri_yukle():
    if not os.path.exists(DOSYA_ADI):
        return {}
    try:
        with open(DOSYA_ADI, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def veriyi_kaydet(data):
    with open(DOSYA_ADI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 3. MAKYAJ (MOBİL GÖRÜNÜM) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { margin-top: -80px; }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 4. YAN MENÜ (NAVİGASYON) ---
st.sidebar.title("📱 Menü")

# Sayfa Seçimi (Sekmeler)
secilen_sayfa = st.sidebar.radio(
    "Gitmek İstediğin Yer:",
    ["📸 Buzdolabı Şefi", "📊 Kalori & Diyet Takibi"]
)

st.sidebar.divider()

# --- SAYFA 1: BUZDOLABI ŞEFİ (ESKİ KODLARIMIZ) ---
if secilen_sayfa == "📸 Buzdolabı Şefi":
    st.sidebar.title("⚙️ Şef Ayarları")
    
    # Dil Seçeneği
    secilen_dil = st.sidebar.selectbox(
        "Dil / Language",
        ["Türkçe", "English", "Deutsch", "Español", "Français", "العربية"]
    )

    # Mod Seçeneği
    if secilen_dil == "English":
        mod_basligi = "Goal?"
        secenekler = ["👨‍🍳 Standard", "🥗 Dietitian", "💪 Athlete"]
    elif secilen_dil == "Deutsch":
        mod_basligi = "Ziel?"
        secenekler = ["👨‍🍳 Standard", "🥗 Ernährungsberater", "💪 Sportler"]
    else:
        mod_basligi = "Hedef?"
        secenekler = ["👨‍🍳 Standart", "🥗 Diyetisyen", "💪 Sporcu"]

    sef_modu = st.sidebar.radio(mod_basligi, secenekler)

    # Başlık
    st.title("📸 Buzdolabı Şefi")
    
    # Metinler
    if secilen_dil == "English":
        upload_text, button_text, loading_text, result_text = "Upload Image", "Analyze! 🚀", "Calculating...", "✅ Result:"
        st.caption("Upload fridge photo, get recipes.")
    elif secilen_dil == "Deutsch":
        upload_text, button_text, loading_text, result_text = "Bild hochladen", "Analysieren! 🚀", "Berechnung...", "✅ Ergebnis:"
        st.caption("Lade ein Foto hoch.")
    else:
        upload_text, button_text, loading_text, result_text = "Resim Yükle", "Analiz Et! 🚀", "Hesaplanıyor...", "✅ Sonuç:"
        st.caption("Dolabın fotoğrafını yükle, tarifini al.")

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

# --- SAYFA 2: KALORİ TAKİBİ (YENİ ÖZELLİK) ---
elif secilen_sayfa == "📊 Kalori & Diyet Takibi":
    st.title("📊 Günlük Takip")
    
    # Verileri Yükle
    veri_tabani = verileri_yukle()
    
    # Tarih Seçimi (Varsayılan Bugün)
    bugun = str(date.today())
    secilen_tarih = st.date_input("Tarih Seç", date.today())
    tarih_str = str(secilen_tarih)
    
    # O tarihte kayıt yoksa boş liste oluştur
    if tarih_str not in veri_tabani:
        veri_tabani[tarih_str] = {"Sabah": [], "Öğle": [], "Akşam": [], "Ara Öğün": []}
    
    gunluk_veri = veri_tabani[tarih_str]

    # --- YENİ YEMEK EKLEME FORMU ---
    st.subheader("➕ Ne Yedin?")
    
    col1, col2 = st.columns(2)
    with col1:
        ogun = st.selectbox("Öğün Seç", ["Sabah", "Öğle", "Akşam", "Ara Öğün"])
        yemek_adi = st.text_input("Yemek Adı (Örn: 2 Yumurta)")
    
    with col2:
        kalori = st.number_input("Kalori (kcal)", min_value=0, step=10)
        protein = st.number_input("Protein (gr)", min_value=0, step=1)
        karbon = st.number_input("Karbonhidrat (gr)", min_value=0, step=1)
        yag = st.number_input("Yağ (gr)", min_value=0, step=1)

    if st.button("Listeye Ekle 💾"):
        if yemek_adi:
            yeni_kayit = {
                "yemek": yemek_adi,
                "kalori": kalori,
                "protein": protein,
                "karbon": karbon,
                "yag": yag
            }
            # Listeye ekle
            gunluk_veri[ogun].append(yeni_kayit)
            # Veritabanına kaydet
            veri_tabani[tarih_str] = gunluk_veri
            veriyi_kaydet(veri_tabani)
            st.success(f"{yemek_adi} {ogun} öğününe eklendi!")
            st.rerun() # Sayfayı yenile ki tablo güncellensin
        else:
            st.warning("Lütfen yemek adı gir.")

    st.divider()

    # --- GÜNLÜK ÖZET (TOPLAMLAR) ---
    st.subheader(f"📅 {tarih_str} Özeti")
    
    # Toplamları Hesapla
    toplam_kalori = 0
    toplam_protein = 0
    toplam_karbon = 0
    toplam_yag = 0

    for o in ["Sabah", "Öğle", "Akşam", "Ara Öğün"]:
        for item in gunluk_veri[o]:
            toplam_kalori += item['kalori']
            toplam_protein += item['protein']
            toplam_karbon += item['karbon']
            toplam_yag += item['yag']

    # Güzel Gösterge (Metrics)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🔥 Toplam Kalori", f"{toplam_kalori} kcal")
    k2.metric("🥩 Protein", f"{toplam_protein} gr")
    k3.metric("🍞 Karbonhidrat", f"{toplam_karbon} gr")
    k4.metric("💧 Yağ", f"{toplam_yag} gr")

    # --- DETAYLI LİSTE ---
    st.write("### 📋 Öğün Detayları")
    
    for o in ["Sabah", "Öğle", "Akşam", "Ara Öğün"]:
        # Sadece yemek varsa o öğünü göster
        if len(gunluk_veri[o]) > 0:
            st.markdown(f"**{o}**")
            for yemek in gunluk_veri[o]:
                st.text(f"- {yemek['yemek']}: {yemek['kalori']} kcal | P:{yemek['protein']} K:{yemek['karbon']} Y:{yemek['yag']}")
            st.divider()
    
    # Günü Temizle Butonu
    if st.button("🗑️ Bu Günü Sil / Sıfırla"):
        del veri_tabani[tarih_str]
        veriyi_kaydet(veri_tabani)
        st.rerun()