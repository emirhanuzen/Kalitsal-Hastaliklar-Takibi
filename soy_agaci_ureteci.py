# soy_agaci_ureteci.py
# GÖREVİ: Sadece soy ağacı üretme algoritmasını barındırır.

import random
import uuid
import datetime

# --- 1. İSİM ARŞİVLERİ ---
ERKEK_ISIMLERI = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hasan", "Hüseyin", "İbrahim", "Yusuf", "Osman", "Ömer"]
KADIN_ISIMLERI = ["Ayşe", "Fatma", "Zeynep", "Elif", "Meryem", "Emine", "Hatice", "Zehra", "Sultan", "Hanife"]
SOYADLARI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın",
             "Özdemir"]  # Kızlık soyadları için

# --- Global Değişken ( Çocuk üretimindeki soyadı mantığı için ) ---
KULLANICI_KUSAGI = 0


# --- 2. ALGORİTMİK FONKSİYONLAR ---

def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None, isim=None):
    """Algoritma içinde yeni bir birey oluşturur. Eğer isim verilmezse rastgele seçer."""

    if isim is None:
        if cinsiyet == "Kadın":
            isim = random.choice(KADIN_ISIMLERI)
        else:
            isim = random.choice(ERKEK_ISIMLERI)

    birey_id = str(uuid.uuid4())

    if kurgusal_tc is None:
        kurgusal_tc = ''.join([str(random.randint(1, 9)) for _ in range(11)])

    yeni_kisi = {
        "birey_id": birey_id,
        "kurgusal_tc": kurgusal_tc,
        "isim": isim,
        "soyad": soyad,
        "cinsiyet": cinsiyet,
        "dogum_yili": dogum_yili,
        "kusak": kusak,
        "anne_id": None,
        "baba_id": None,
        "hastaliklar": []
    }
    return yeni_kisi


def hastaliklari_ata(birey, hastalik_listesi):
    """Bir bireye SQL'den gelen oranlara göre hastalık atar."""
    # Hastalık listesi yoksa veya boşsa işlem yapma
    if not hastalik_listesi:
        return

    for hastalik_tuple in hastalik_listesi:
        # Gelen verinin tuple olduğunu varsayalım (HastalikAdi, GorulmeOrani)
        if len(hastalik_tuple) < 2: continue  # Veri formatı bozuksa atla
        hastalik = hastalik_tuple[0]
        oran = hastalik_tuple[1]

        # Oran None veya geçersizse atla
        if oran is None or not isinstance(oran, (int, float)): continue

        mevcut_oran = oran
        if hastalik == "Renk Körlüğü" and birey["cinsiyet"] == "Kadın":
            mevcut_oran = 0.005

        if random.random() < mevcut_oran:
            if "hastaliklar" not in birey:
                birey["hastaliklar"] = []
            # Aynı hastalığı tekrar eklememek için kontrol et
            if hastalik not in birey["hastaliklar"]:
                birey["hastaliklar"].append(hastalik)


def uret_ata_tarafi(birey, soy_agaci_listesi, mevcut_kusak, hedef_kusak, hastalik_listesi):
    """Bir bireyden geriye doğru (atalar) ağacı üretir. Hedef kuşağa ulaşınca durur."""
    if mevcut_kusak <= hedef_kusak:
        return

    ebeveyn_dogum_yili = birey["dogum_yili"] - random.randint(20, 35)

    baba = kisi_olustur("Erkek", birey["soyad"], ebeveyn_dogum_yili, mevcut_kusak - 1)
    anne = kisi_olustur("Kadın", random.choice(SOYADLARI), ebeveyn_dogum_yili, mevcut_kusak - 1)

    hastaliklari_ata(baba, hastalik_listesi)
    hastaliklari_ata(anne, hastalik_listesi)

    soy_agaci_listesi.append(baba)
    soy_agaci_listesi.append(anne)

    birey["baba_id"] = baba["birey_id"]
    birey["anne_id"] = anne["birey_id"]

    uret_ata_tarafi(baba, soy_agaci_listesi, mevcut_kusak - 1, hedef_kusak, hastalik_listesi)
    uret_ata_tarafi(anne, soy_agaci_listesi, mevcut_kusak - 1, hedef_kusak, hastalik_listesi)


def uret_cocuk_tarafi(birey, soy_agaci_listesi, mevcut_kusak, hedef_kusak, hastalik_listesi):
    """Bir bireyden ileriye doğru (çocuklar, torunlar) ağacı üretir. Hedef kuşağa ulaşınca durur."""
    if mevcut_kusak >= hedef_kusak:
        return

    cocuk_sayisi = random.randint(0, 3)
    for _ in range(cocuk_sayisi):
        cocuk_dogum_yili = birey["dogum_yili"] + random.randint(20, 35)

        if cocuk_dogum_yili > datetime.date.today().year:
            continue

        cocugun_cinsiyeti = random.choice(["Erkek", "Kadın"])
        cocugun_soyadi = birey["soyad"] if birey["cinsiyet"] == "Erkek" else random.choice(SOYADLARI)

        cocuk = kisi_olustur(
            cocugun_cinsiyeti,
            cocugun_soyadi,
            cocuk_dogum_yili,
            mevcut_kusak + 1
        )
        hastaliklari_ata(cocuk, hastalik_listesi)
        soy_agaci_listesi.append(cocuk)

        uret_cocuk_tarafi(cocuk, soy_agaci_listesi, mevcut_kusak + 1, hedef_kusak, hastalik_listesi)


def uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi):
    """
    YAŞ ODAKLI ANA ALGORİTMA FONKSİYONU
    Kullanıcıyı alır, yaşına göre kuşak belirler ve çift yönlü ağacı üretir.
    Kullanıcının kendisi için kayıt verisindeki AD ve SOYADI kullanır.
    """
    global KULLANICI_KUSAGI
    soy_agaci = []

    # Gelen veriyi alalım
    dogum_tarihi_nesnesi = kullanici_kayit_verisi.get("dogum_tarihi")
    kullanici_ismi = kullanici_kayit_verisi.get("isim")
    kullanici_soyadi = kullanici_kayit_verisi.get("soyad")
    kullanici_tc = kullanici_kayit_verisi.get("kendi_tc")

    # Doğum tarihi nesnesi gelmediyse veya None ise hata verelim
    if not isinstance(dogum_tarihi_nesnesi, datetime.date):
        raise TypeError(
            f"uret_dinamik_soy_agaci fonksiyonuna geçersiz doğum tarihi tipi geldi: {type(dogum_tarihi_nesnesi)}")

    # --- YENİ EKLENEN DEBUG SATIRI ---
    print(f"DEBUG: Gelen dogum_tarihi_nesnesi tipi: {type(dogum_tarihi_nesnesi)}, Değeri: {dogum_tarihi_nesnesi}")
    # ----------------------------------

    # Yaşı hesapla
    yas = datetime.date.today().year - dogum_tarihi_nesnesi.year

    GERIYE_HEDEF_KUSAK = 1
    ILERIYE_HEDEF_KUSAK = 4
    KULLANICI_KUSAGI = 0

    if yas > 50:
        KULLANICI_KUSAGI = 2
    elif 18 <= yas <= 50:
        KULLANICI_KUSAGI = 3
    else:
        KULLANICI_KUSAGI = 4

    # Kök kullanıcıyı (kaydolan kişi) oluştur
    kok_kullanici = kisi_olustur(
        random.choice(["Erkek", "Kadın"]),
        kullanici_soyadi,  # Kullanıcının girdiği soyad
        dogum_tarihi_nesnesi.year,  # Doğum YILI (int)
        KULLANICI_KUSAGI,  # Hesaplanan kuşak
        kullanici_tc,  # Kullanıcının girdiği TC
        kullanici_ismi  # Kullanıcının girdiği isim
    )
    hastaliklari_ata(kok_kullanici, hastalik_listesi)
    soy_agaci.append(kok_kullanici)

    # Geriye doğru ataları üret
    uret_ata_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, GERIYE_HEDEF_KUSAK, hastalik_listesi)

    # İleriye doğru çocukları üret
    uret_cocuk_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, ILERIYE_HEDEF_KUSAK, hastalik_listesi)

    return soy_agaci, kok_kullanici["birey_id"]