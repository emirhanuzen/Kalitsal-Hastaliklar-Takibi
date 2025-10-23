# soy_agaci_ureteci.py (GENETİK SİMÜLASYON - HATALAR DÜZELTİLDİ)

import random
import uuid
import datetime
import math
import sys

# --- 1. İSİM ARŞİVLERİ ---
ERKEK_ISIMLERI = ["Ahmet", "Mehmet", "Mustafa", "Ali", "Hasan", "Hüseyin", "İbrahim", "Yusuf", "Osman", "Ömer"]
KADIN_ISIMLERI = ["Ayşe", "Fatma", "Zeynep", "Elif", "Meryem", "Emine", "Hatice", "Zehra", "Sultan", "Hanife"]
SOYADLARI = ["Yılmaz", "Kaya", "Demir", "Çelik", "Şahin", "Yıldız", "Yıldırım", "Öztürk", "Aydın", "Özdemir"]

# --- Global Değişkenler ---
HASTALIK_DETAYLARI = {}
TUM_BIREYLER = {} # Ağacı üretirken tüm bireyleri burada saklayalım: {birey_id: birey_nesnesi}

# --- 2. YENİ YARDIMCI FONKSİYONLAR ---

def calculate_allele_frequencies(hastalik_listesi_sql):
    global HASTALIK_DETAYLARI
    HASTALIK_DETAYLARI = {}
    if not hastalik_listesi_sql:
        print("--- UYARI (ureteci): Boş hastalık listesi alındı.", file=sys.stderr)
        return
    for hastalik_tuple in hastalik_listesi_sql:
        # Gelen tuple yapısını kontrol edelim
        if len(hastalik_tuple) < 3:
             print(f"--- UYARI (ureteci): Beklenenden eksik veri geldi: {hastalik_tuple}, atlanıyor.", file=sys.stderr)
             continue
        ad, oran, sekil = hastalik_tuple[:3] # İlk 3 elemanı alalım

        if oran is None or not isinstance(oran, (float, int)) or oran <= 0 or oran >= 1:
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için geçersiz oran ({oran}), atlanıyor.", file=sys.stderr)
            continue
        if not sekil or not isinstance(sekil, str):
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için geçersiz kalıtım şekli ({sekil}), atlanıyor.", file=sys.stderr)
            continue

        q = 0
        p = 1
        try:
            if sekil == 'Çekinik':
                q = math.sqrt(oran)
                p = 1 - q
            elif sekil == 'X-Bağlı Çekinik':
                 q = oran
                 p = 1 - q
            else:
                 print(f"--- UYARI (ureteci): '{ad}' hastalığı için desteklenmeyen kalıtım şekli: {sekil}", file=sys.stderr)
                 continue
        except ValueError:
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için oran ({oran}) karekök alınamaz, atlanıyor.", file=sys.stderr)
            continue

        HASTALIK_DETAYLARI[ad] = {'oran': oran, 'sekil': sekil, 'q': q, 'p': p}
    print(f">>> DEBUG (ureteci): Hesaplanan alel frekansları: {HASTALIK_DETAYLARI}")

def determine_initial_genotype(hastalik_adi, cinsiyet):
    details = HASTALIK_DETAYLARI.get(hastalik_adi)
    if not details: return None
    p = details['p']
    q = details['q']
    sekil = details['sekil']
    rand_num = random.random()

    if sekil == 'Çekinik':
        if rand_num < p*p: return "NN"
        elif rand_num < p*p + 2*p*q: return "NT"
        else: return "TT"
    elif sekil == 'X-Bağlı Çekinik':
        if cinsiyet == 'Erkek':
            return "XnY" if rand_num < p else "XtY"
        else: # Kadın
             if rand_num < p*p: return "XnXn"
             elif rand_num < p*p + 2*p*q: return "XnXt"
             else: return "XtXt"
    return None

def determine_phenotype(hastalik_adi, genotype, cinsiyet):
    details = HASTALIK_DETAYLARI.get(hastalik_adi)
    if not details or genotype is None: return None
    sekil = details['sekil']

    if sekil == 'Çekinik':
        if genotype == "TT": return "Hasta"
        elif genotype == "NT": return "Taşıyıcı"
        else: return None
    elif sekil == 'X-Bağlı Çekinik':
        if cinsiyet == 'Erkek':
            return "Hasta" if genotype == "XtY" else None
        else: # Kadın
            if genotype == "XtXt": return "Hasta"
            elif genotype == "XnXt": return "Taşıyıcı"
            else: return None
    return None

def inherit_allele(parent_genotype, sekil, parent_cinsiyet):
    """Ebeveynden çocuğa geçecek tek bir aleli (geni) seçer."""
    if not parent_genotype: return None

    # Otozomal (Çekinik veya Baskın)
    if sekil == 'Çekinik': # Varsayılan 'Baskın' için de aynı mantık şimdilik
        if len(parent_genotype) == 2:
            return random.choice(list(parent_genotype)) # String'i listeye çevirip seç
        else:
            print(f"--- UYARI (ureteci): Beklenmeyen otozomal genotip formatı: {parent_genotype}", file=sys.stderr)
            return None

    # X-Bağlı Çekinik
    elif sekil == 'X-Bağlı Çekinik':
        if parent_cinsiyet == 'Erkek': # Baba XY (XnY veya XtY)
            # Baba Y veya X kromozomunu verir (Xn veya Xt)
            x_allele = parent_genotype[:2] # Xn veya Xt
            return random.choice([x_allele, 'Y'])
        else: # Anne XX (XnXn, XnXt, XtXt)
             # Anne sadece X kromozomlarından birini verir
             if len(parent_genotype) == 4 and parent_genotype.startswith("X"):
                 allele1 = parent_genotype[0:2] # Xn veya Xt
                 allele2 = parent_genotype[2:4] # Xn veya Xt
                 return random.choice([allele1, allele2])
             else:
                 print(f"--- UYARI (ureteci): Beklenmeyen X-bağlı kadın genotip formatı: {parent_genotype}", file=sys.stderr)
                 return None
    return None # Desteklenmeyen durum


# --- 3. ANA ÜRETİM FONKSİYONU ---

def agaci_uret_ve_genleri_aktar(birey_id, hedef_kusak, is_ata_uretimi):
    """
    Özyinelemeli ana fonksiyon. Hem ağacı kurar hem genleri aktarır.
    """
    global TUM_BIREYLER

    mevcut_birey = TUM_BIREYLER.get(birey_id)
    if not mevcut_birey: return

    mevcut_kusak = mevcut_birey["kusak"]

    if is_ata_uretimi and mevcut_kusak <= hedef_kusak: return
    if not is_ata_uretimi and mevcut_kusak >= hedef_kusak: return

    # --- ATA ÜRETİMİ (Geriye Doğru) ---
    if is_ata_uretimi:
        ebeveyn_dogum_yili = mevcut_birey["dogum_yili"] - random.randint(20, 35)
        # kisi_olustur içinde genotip: {} başlatılıyor
        baba = kisi_olustur("Erkek", mevcut_birey["soyad"], ebeveyn_dogum_yili, mevcut_kusak - 1)
        anne = kisi_olustur("Kadın", random.choice(SOYADLARI), ebeveyn_dogum_yili, mevcut_kusak - 1)

        TUM_BIREYLER[baba["birey_id"]] = baba
        TUM_BIREYLER[anne["birey_id"]] = anne

        mevcut_birey["baba_id"] = baba["birey_id"]
        mevcut_birey["anne_id"] = anne["birey_id"]

        # En tepedeki kuşaktaysak (Kuşak 1), başlangıç genotiplerini ata
        if (mevcut_kusak - 1) == hedef_kusak: # hedef_kusak genellikle 1 olacak
             if not baba.get("genotip"): baba["genotip"] = {}
             if not anne.get("genotip"): anne["genotip"] = {}
             for hastalik_adi in HASTALIK_DETAYLARI:
                 baba["genotip"][hastalik_adi] = determine_initial_genotype(hastalik_adi, baba["cinsiyet"])
                 anne["genotip"][hastalik_adi] = determine_initial_genotype(hastalik_adi, anne["cinsiyet"])

        # Özyineleme: Ataları üretmeye devam et
        agaci_uret_ve_genleri_aktar(baba["birey_id"], hedef_kusak, True)
        agaci_uret_ve_genleri_aktar(anne["birey_id"], hedef_kusak, True)

        # <<< GEN AKTARIMI (Ata Üretimi Sonrası) >>>
        # Ataları ürettikten sonra, ebeveynlerin genotipleri belli olunca çocuğunkini hesapla
        anne_genotipleri = anne.get("genotip", {})
        baba_genotipleri = baba.get("genotip", {})
        cocuk_genotipleri = {}
        for hastalik_adi, details in HASTALIK_DETAYLARI.items():
            sekil = details['sekil']
            anne_genotip = anne_genotipleri.get(hastalik_adi)
            baba_genotip = baba_genotipleri.get(hastalik_adi)

            if anne_genotip and baba_genotip: # İki ebeveynin de genotipi biliniyorsa
                 allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                 allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")

                 if allele_anneden and allele_babadan:
                      # Çocuğun genotipini oluştur (X-bağlı ve Otozomal farklı)
                      if sekil == 'X-Bağlı Çekinik':
                           if allele_babadan == 'Y': # Babadan Y geldiyse cinsiyet Erkek
                                cocuk_genotipleri[hastalik_adi] = allele_anneden + 'Y'
                           else: # Babadan X geldiyse cinsiyet Kadın
                                cocuk_genotipleri[hastalik_adi] = allele_anneden + allele_babadan # İki X'i birleştir
                      elif sekil == 'Çekinik':
                           # Alelleri alfabetik sırala (NT ve TN aynıdır)
                           cocuk_genotipleri[hastalik_adi] = "".join(sorted([allele_anneden, allele_babadan]))
                      # TODO: Baskın için de aynı mantık olabilir
            # Eğer ebeveyn genotipi eksikse çocuğunki hesaplanamaz (None kalır)
        mevcut_birey["genotip"] = cocuk_genotipleri


    # --- ÇOCUK ÜRETİMİ (İleriye Doğru) ---
    else:
        cocuk_sayisi = random.randint(0, 3)
        for _ in range(cocuk_sayisi):
            cocuk_dogum_yili = mevcut_birey["dogum_yili"] + random.randint(20, 35)
            if cocuk_dogum_yili > datetime.date.today().year: continue

            cocugun_cinsiyeti = random.choice(["Erkek", "Kadın"])
            cocugun_soyadi = mevcut_birey["soyad"]

            # Çocuğu oluştur (henüz genotipi yok)
            cocuk = kisi_olustur(cocugun_cinsiyeti, cocugun_soyadi, cocuk_dogum_yili, mevcut_kusak + 1)
            cocuk["genotip"] = {} # Genotip sözlüğünü başlat

            # <<< GEN AKTARIMI (Çocuk Üretimi Sırasında) >>>
            anne = None
            baba = None
            if mevcut_birey["cinsiyet"] == "Kadın":
                anne = mevcut_birey
                # Babayı bulmamız lazım. Ağacımızda eş ilişkisi olmadığı için varsayımsal üretelim.
                # Varsayımsal babanın genotipini başlangıç olasılıklarına göre atayalım.
                baba_genotipleri = {}
                for hastalik_adi in HASTALIK_DETAYLARI:
                    baba_genotipleri[hastalik_adi] = determine_initial_genotype(hastalik_adi, "Erkek")
                baba = {"genotip": baba_genotipleri, "cinsiyet": "Erkek"} # Sadece genotip için
            else: # mevcut_birey Erkek ise
                baba = mevcut_birey
                # Varsayımsal anneyi üretelim.
                anne_genotipleri = {}
                for hastalik_adi in HASTALIK_DETAYLARI:
                    anne_genotipleri[hastalik_adi] = determine_initial_genotype(hastalik_adi, "Kadın")
                anne = {"genotip": anne_genotipleri, "cinsiyet": "Kadın"} # Sadece genotip için

            # Şimdi iki ebeveynin de genotipi var (biri gerçek, biri varsayımsal)
            cocuk_genotipleri = {}
            if anne and baba: # İki ebeveyn de tanımlıysa
                for hastalik_adi, details in HASTALIK_DETAYLARI.items():
                    sekil = details['sekil']
                    anne_genotip = anne.get("genotip", {}).get(hastalik_adi)
                    baba_genotip = baba.get("genotip", {}).get(hastalik_adi)

                    if anne_genotip and baba_genotip:
                         allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                         allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")

                         if allele_anneden and allele_babadan:
                              if sekil == 'X-Bağlı Çekinik':
                                   if allele_babadan == 'Y': # Çocuk Erkek
                                        cocuk_genotipleri[hastalik_adi] = allele_anneden + 'Y'
                                   else: # Çocuk Kadın
                                        cocuk_genotipleri[hastalik_adi] = allele_anneden + allele_babadan
                              elif sekil == 'Çekinik':
                                   cocuk_genotipleri[hastalik_adi] = "".join(sorted([allele_anneden, allele_babadan]))

            cocuk["genotip"] = cocuk_genotipleri

            # Çocuğa ebeveyn ID'sini ata
            if mevcut_birey["cinsiyet"] == "Kadın": cocuk["anne_id"] = mevcut_birey["birey_id"]
            else: cocuk["baba_id"] = mevcut_birey["birey_id"]

            TUM_BIREYLER[cocuk["birey_id"]] = cocuk

            # Özyineleme
            agaci_uret_ve_genleri_aktar(cocuk["birey_id"], hedef_kusak, False)


def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None, isim=None):
    """(Tekrar tanımlandı - yukarıdaki ile aynı olmalı)"""
    if isim is None:
        if cinsiyet == "Kadın": isim = random.choice(KADIN_ISIMLERI)
        else: isim = random.choice(ERKEK_ISIMLERI)
    birey_id = str(uuid.uuid4())
    if kurgusal_tc is None: kurgusal_tc = ''.join([str(random.randint(1, 9)) for _ in range(11)])
    yeni_kisi = {
        "birey_id": birey_id, "kurgusal_tc": kurgusal_tc, "isim": isim, "soyad": soyad,
        "cinsiyet": cinsiyet, "dogum_yili": dogum_yili, "kusak": kusak,
        "anne_id": None, "baba_id": None,
        "hastaliklar": [], # Sonradan fenotipe göre doldurulacak
        "genotip": {} # Genotipleri burada saklayacağız
    }
    return yeni_kisi

def uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi_sql):
    """GENETİK SİMÜLASYONLU ANA ALGORİTMA FONKSİYONU"""
    global KULLANICI_KUSAGI, TUM_BIREYLER
    TUM_BIREYLER = {}

    # 1. Hastalık detaylarını ve alel frekanslarını hesapla
    calculate_allele_frequencies(hastalik_listesi_sql)
    if not HASTALIK_DETAYLARI:
        print("--- UYARI (ureteci): Geçerli hastalık detayı yok, genetik simülasyon yapılamayacak.")
        # Hata durumunda boş ağaç döndürelim
        return [], None

    # 2. Kullanıcı bilgilerini al ve yaş/kuşak belirle
    dogum_tarihi_nesnesi = kullanici_kayit_verisi.get("dogum_tarihi")
    kullanici_ismi = kullanici_kayit_verisi.get("isim")
    kullanici_soyadi = kullanici_kayit_verisi.get("soyad")
    kullanici_tc = kullanici_kayit_verisi.get("kendi_tc")
    kullanici_cinsiyet = kullanici_kayit_verisi.get("cinsiyet")

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

    # 3. Kök kullanıcıyı oluştur
    kok_kullanici = kisi_olustur(
        kullanici_cinsiyet, kullanici_soyadi, dogum_tarihi_nesnesi.year,
        KULLANICI_KUSAGI, kullanici_tc, kullanici_ismi
    )
    TUM_BIREYLER[kok_kullanici["birey_id"]] = kok_kullanici
    kok_birey_id = kok_kullanici["birey_id"]

    # 4. Ağacı üret ve genleri aktar
    agaci_uret_ve_genleri_aktar(kok_birey_id, GERIYE_HEDEF_KUSAK, True) # Önce ataları üret (bu genleri de hesaplar)
    # agaci_uret_ve_genleri_aktar(kok_birey_id, ILERIYE_HEDEF_KUSAK, False) # Sonra çocukları (bu da genleri hesaplar)

    # 5. Fenotipleri belirle ve son listeyi oluştur
    son_soy_agaci_listesi = []
    for birey_id, birey in TUM_BIREYLER.items():
        fenotip_listesi = []
        birey_genotipleri = birey.get("genotip", {})
        for hastalik_adi, genotype in birey_genotipleri.items():
            fenotip_durum = determine_phenotype(hastalik_adi, genotype, birey["cinsiyet"])
            if fenotip_durum:
                fenotip_listesi.append({"hastalik": hastalik_adi, "durum": fenotip_durum})

        # Sonuç listesine eklemeden önce genotip bilgisini kaldıralım
        birey_kopya = birey.copy()
        if "genotip" in birey_kopya:
            del birey_kopya["genotip"]

        birey_kopya["hastaliklar"] = fenotip_listesi if fenotip_listesi else "Sağlıklı"

        son_soy_agaci_listesi.append(birey_kopya)

    return son_soy_agaci_listesi, kok_birey_id