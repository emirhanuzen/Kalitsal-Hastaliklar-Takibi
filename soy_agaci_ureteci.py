# soy_agaci_ureteci.py
# GÖREVİ: Sadece soy ağacı üretme algoritmasını barındırır.
# SON GÜNCELLEME: Kayıt olan kullanıcının cinsiyetini formdan alır.

import random
import uuid
import datetime

# --- 1. İSİM ARŞİVLERİ ---
ERKEK_ISIMLERI = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hasan", "Hüseyin", "İbrahim", "Yusuf", "Osman", "Ömer"]
KADIN_ISIMLERI = ["Ayşe", "Fatma", "Zeynep", "Elif", "Meryem", "Emine", "Hatice", "Zehra", "Sultan", "Hanife"]
SOYADLARI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir"]

# --- Global Değişken ---
KULLANICI_KUSAGI = 0

# --- 2. ALGORİTMİK FONKSİYONLAR ---

def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None, isim=None):
    """Algoritma içinde yeni bir birey oluşturur. Eğer isim verilmezse rastgele seçer."""
    if isim is None:
        if cinsiyet == "Kadın": isim = random.choice(KADIN_ISIMLERI)
        else: isim = random.choice(ERKEK_ISIMLERI)
    birey_id = str(uuid.uuid4())
    if kurgusal_tc is None: kurgusal_tc = ''.join([str(random.randint(1, 9)) for _ in range(11)])
    yeni_kisi = {
        "birey_id": birey_id, "kurgusal_tc": kurgusal_tc, "isim": isim, "soyad": soyad,
        "cinsiyet": cinsiyet, "dogum_yili": dogum_yili, "kusak": kusak,
        "anne_id": None, "baba_id": None, "hastaliklar": []
    }
    return yeni_kisi

def hastaliklari_ata(birey, hastalik_listesi_sql):
    """Bir bireye SQL'den gelen oranlara göre hastalık atar."""
    if not hastalik_listesi_sql: return
    for hastalik_tuple in hastalik_listesi_sql:
        if len(hastalik_tuple) < 2: continue
        hastalik = hastalik_tuple[0]
        oran = hastalik_tuple[1]
        if oran is None or not isinstance(oran, (int, float)): continue
        mevcut_oran = oran
        if hastalik == "Renk Körlüğü" and birey["cinsiyet"] == "Kadın": mevcut_oran = 0.005
        if random.random() < mevcut_oran:
            if "hastaliklar" not in birey or not isinstance(birey["hastaliklar"], list):
                 birey["hastaliklar"] = []
            if hastalik not in birey["hastaliklar"]:
                 birey["hastaliklar"].append(hastalik)

def uret_ata_tarafi(birey, soy_agaci_listesi, mevcut_kusak, hedef_kusak, hastalik_listesi_sql):
    """Bir bireyden geriye doğru (atalar) ağacı üretir."""
    if mevcut_kusak <= hedef_kusak: return
    ebeveyn_dogum_yili = birey["dogum_yili"] - random.randint(20, 35)
    baba = kisi_olustur("Erkek", birey["soyad"], ebeveyn_dogum_yili, mevcut_kusak - 1)
    anne = kisi_olustur("Kadın", random.choice(SOYADLARI), ebeveyn_dogum_yili, mevcut_kusak - 1)
    hastaliklari_ata(baba, hastalik_listesi_sql)
    hastaliklari_ata(anne, hastalik_listesi_sql)
    soy_agaci_listesi.append(baba)
    soy_agaci_listesi.append(anne)
    birey["baba_id"] = baba["birey_id"]
    birey["anne_id"] = anne["birey_id"]
    uret_ata_tarafi(baba, soy_agaci_listesi, mevcut_kusak - 1, hedef_kusak, hastalik_listesi_sql)
    uret_ata_tarafi(anne, soy_agaci_listesi, mevcut_kusak - 1, hedef_kusak, hastalik_listesi_sql)

def uret_cocuk_tarafi(birey, soy_agaci_listesi, mevcut_kusak, hedef_kusak, hastalik_listesi_sql):
    """Bir bireyden ileriye doğru (çocuklar, torunlar) ağacı üretir."""
    if mevcut_kusak >= hedef_kusak: return
    cocuk_sayisi = random.randint(0, 3)
    for _ in range(cocuk_sayisi):
        cocuk_dogum_yili = birey["dogum_yili"] + random.randint(20, 35)
        if cocuk_dogum_yili > datetime.date.today().year: continue
        cocugun_cinsiyeti = random.choice(["Erkek", "Kadın"])
        cocugun_soyadi = birey["soyad"] if birey["cinsiyet"] == "Erkek" else random.choice(SOYADLARI)
        cocuk = kisi_olustur(cocugun_cinsiyeti, cocugun_soyadi, cocuk_dogum_yili, mevcut_kusak + 1)

        # Çocuğa ebeveyn ID'sini ata
        if birey["cinsiyet"] == "Kadın":
            cocuk["anne_id"] = birey["birey_id"]
        else: # Erkek ise
            cocuk["baba_id"] = birey["birey_id"]

        hastaliklari_ata(cocuk, hastalik_listesi_sql)
        soy_agaci_listesi.append(cocuk)
        uret_cocuk_tarafi(cocuk, soy_agaci_listesi, mevcut_kusak + 1, hedef_kusak, hastalik_listesi_sql)


def uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi_sql):
    """
    YAŞ ODAKLI ANA ALGORİTMA FONKSİYONU
    Kullanıcıyı alır, yaşına ve CİNSİYETİNE göre ağacı üretir.
    """
    global KULLANICI_KUSAGI
    soy_agaci = []

    dogum_tarihi_nesnesi = kullanici_kayit_verisi.get("dogum_tarihi")
    kullanici_ismi = kullanici_kayit_verisi.get("isim")
    kullanici_soyadi = kullanici_kayit_verisi.get("soyad")
    kullanici_tc = kullanici_kayit_verisi.get("kendi_tc")
    kullanici_cinsiyet = kullanici_kayit_verisi.get("cinsiyet") # <<< Gelen cinsiyeti al

    if not isinstance(dogum_tarihi_nesnesi, datetime.date):
        raise TypeError(f"uret_dinamik_soy_agaci: geçersiz doğum tarihi tipi {type(dogum_tarihi_nesnesi)}")
    if kullanici_cinsiyet not in ["Erkek", "Kadın"]:
        raise ValueError(f"uret_dinamik_soy_agaci: geçersiz cinsiyet değeri '{kullanici_cinsiyet}'")

    yas = datetime.date.today().year - dogum_tarihi_nesnesi.year
    GERIYE_HEDEF_KUSAK = 1
    ILERIYE_HEDEF_KUSAK = 4
    KULLANICI_KUSAGI = 0
    if yas > 50: KULLANICI_KUSAGI = 2
    elif 18 <= yas <= 50: KULLANICI_KUSAGI = 3
    else: KULLANICI_KUSAGI = 4

    # <<< DEĞİŞİKLİK BURADA: Kök kullanıcıyı oluştururken gelen CİNSİYETİ kullan >>>
    kok_kullanici = kisi_olustur(
        kullanici_cinsiyet, # <<< DEĞİŞTİ: Rastgele değil, gelen değer
        kullanici_soyadi,
        dogum_tarihi_nesnesi.year,
        KULLANICI_KUSAGI,
        kullanici_tc,
        kullanici_ismi
    )
    hastaliklari_ata(kok_kullanici, hastalik_listesi_sql)
    soy_agaci.append(kok_kullanici)

    # Geriye doğru ataları üret
    uret_ata_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, GERIYE_HEDEF_KUSAK, hastalik_listesi_sql)

    # İleriye doğru çocukları üret
    uret_cocuk_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, ILERIYE_HEDEF_KUSAK, hastalik_listesi_sql)

    # Hastalıkları boş olanları güncelle
    for kisi in soy_agaci:
        if isinstance(kisi.get("hastaliklar"), list) and not kisi["hastaliklar"]:
            kisi["hastaliklar"] = "Hasta Değil"

    return soy_agaci, kok_kullanici["birey_id"]