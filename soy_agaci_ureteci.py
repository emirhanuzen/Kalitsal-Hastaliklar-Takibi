# soy_agaci_ureteci.py
# GÖREVİ: Sadece soy ağacı üretme algoritmasını barındırır.
# Flask veya veritabanı hakkında hiçbir şey bilmez.

import random
import uuid
import datetime

# --- 1. İSİM ARŞİVLERİ ---s
ERKEK_ISIMLERI = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hasan", "Hüseyin", "İbrahim", "Yusuf", "Osman", "Ömer"]
KADIN_ISIMLERI = ["Ayşe", "Fatma", "Zeynep", "Elif", "Meryem", "Emine", "Hatice", "Zehra", "Sultan", "Hanife"]
SOYADLARI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir"]


# --- 2. ALGORİTMA FONKSİYONLARI ---

def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None):
    """Algoritma içinde yeni bir birey oluşturur."""
    if cinsiyet == "Kadın":
        isim = random.choice(KADIN_ISIMLERI)
    else:
        isim = random.choice(ERKEK_ISIMLERI)

    # Her bireye benzersiz bir BireyID atıyoruz (MongoDB'de aramak için)
    birey_id = str(uuid.uuid4())

    # Herkese rastgele kurgusal TC ata
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
    for hastalik, oran in hastalik_listesi:
        mevcut_oran = oran
        if hastalik == "Renk Körlüğü" and birey["cinsiyet"] == "Kadın":
            mevcut_oran = 0.005  # Kadınlarda farklı oran

        if random.random() < mevcut_oran:
            birey["hastaliklar"].append(hastalik)


def uret_ata_tarafi(birey, soy_agaci_listesi, mevcut_kusak, max_kusak, hastalik_listesi):
    """Bir bireyden geriye doğru (atalar) ağacı üretir."""
    if mevcut_kusak <= max_kusak:  # Geriye doğru 0'a (veya 1'e) kadar gider
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

    uret_ata_tarafi(baba, soy_agaci_listesi, mevcut_kusak - 1, max_kusak, hastalik_listesi)
    uret_ata_tarafi(anne, soy_agaci_listesi, mevcut_kusak - 1, max_kusak, hastalik_listesi)


def uret_cocuk_tarafi(birey, soy_agaci_listesi, mevcut_kusak, max_kusak, hastalik_listesi):
    """Bir bireyden ileriye doğru (çocuklar, torunlar) ağacı üretir."""
    if mevcut_kusak >= max_kusak:
        return

    cocuk_sayisi = random.randint(0, 3)  # 0, 1, 2 veya 3 çocuk olabilir
    for _ in range(cocuk_sayisi):
        cocuk_dogum_yili = birey["dogum_yili"] + random.randint(20, 35)

        if cocuk_dogum_yili > datetime.date.today().year:
            continue

        cocuk = kisi_olustur(
            random.choice(["Erkek", "Kadın"]),
            birey["soyad"] if birey["cinsiyet"] == "Erkek" else random.choice(SOYADLARI),
            cocuk_dogum_yili,
            mevcut_kusak + 1
        )
        hastaliklari_ata(cocuk, hastalik_listesi)
        soy_agaci_listesi.append(cocuk)

        uret_cocuk_tarafi(cocuk, soy_agaci_listesi, mevcut_kusak + 1, max_kusak, hastalik_listesi)


def uret_dinamik_soy_agaci(kullanici_bilgileri, hastalik_listesi):
    """
    YAŞ ODAKLI ANA ALGORİTMA FONKSİYONU
    Kullanıcıyı alır, yaşına göre kuşak belirler ve çift yönlü ağacı üretir.
    """
    soy_agaci = []

    dogum_tarihi = kullanici_bilgileri["dogum_tarihi"]
    yas = datetime.date.today().year - dogum_tarihi.year

    # Toplam 4 kuşak olacak (1: Ata, 2, 3, 4: Son nesil)
    GERIYE_MAX_KUSAK = 1  # Ağacın kökü (en yaşlı) 1. kuşak olacak
    ILERIYE_MAX_KUSAK = 4  # Ağacın sonu 4. kuşak olacak
    KULLANICI_KUSAGI = 0

    if yas > 50:
        KULLANICI_KUSAGI = 2  # Sondan 3. (1-2-3-4)
    elif 18 <= yas <= 50:
        KULLANICI_KUSAGI = 3  # Sondan 2.
    else:  # 18'den küçükse
        KULLANICI_KUSAGI = 4  # Son kuşak

    kok_kullanici = kisi_olustur(
        random.choice(["Erkek", "Kadın"]),
        random.choice(SOYADLARI),
        kullanici_bilgileri["dogum_tarihi"].year,
        KULLANICI_KUSAGI,
        kullanici_bilgileri["kendi_tc"]
    )
    hastaliklari_ata(kok_kullanici, hastalik_listesi)
    soy_agaci.append(kok_kullanici)

    # Geriye doğru ataları üret
    uret_ata_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, GERIYE_MAX_KUSAK, hastalik_listesi)

    # İleriye doğru çocukları üret
    uret_cocuk_tarafi(kok_kullanici, soy_agaci, KULLANICI_KUSAGI, ILERIYE_MAX_KUSAK, hastalik_listesi)

    return soy_agaci, kok_kullanici["birey_id"]