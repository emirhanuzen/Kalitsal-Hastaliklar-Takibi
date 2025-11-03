# genetics/family_tree.py
# Soy ağacı üretim fonksiyonları

import random
import datetime
import sys
from genetics.constants import SOYADLARI
from genetics.person import kisi_olustur
from genetics.genetics import (
    determine_initial_genotype,
    determine_phenotype,
    inherit_allele,
    get_hastalik_detaylari
)


# Global bireyler sözlüğü
TUM_BIREYLER = {}


def reset_bireyler():
    """Bireyler sözlüğünü sıfırlar."""
    global TUM_BIREYLER
    TUM_BIREYLER = {}


def get_bireyler():
    """Bireyler sözlüğünü döndürür."""
    return TUM_BIREYLER


def agaci_uret_ve_genleri_aktar(birey_id, hedef_kusak, is_ata_uretimi):
    """
    Özyinelemeli ana fonksiyon. Hem ağacı kurar hem genleri aktarır.
    """
    global TUM_BIREYLER

    mevcut_birey = TUM_BIREYLER.get(birey_id)
    if not mevcut_birey:
        return

    mevcut_kusak = mevcut_birey["kusak"]

    if is_ata_uretimi and mevcut_kusak <= hedef_kusak:
        return
    if not is_ata_uretimi and mevcut_kusak >= hedef_kusak:
        return

    # --- ATA ÜRETİMİ (Geriye Doğru) ---
    if is_ata_uretimi:
        ebeveyn_dogum_yili = mevcut_birey["dogum_yili"] - random.randint(20, 35)
        baba = kisi_olustur("Erkek", mevcut_birey["soyad"], ebeveyn_dogum_yili, mevcut_kusak - 1)
        anne = kisi_olustur("Kadın", random.choice(SOYADLARI), ebeveyn_dogum_yili, mevcut_kusak - 1)

        TUM_BIREYLER[baba["birey_id"]] = baba
        TUM_BIREYLER[anne["birey_id"]] = anne

        mevcut_birey["baba_id"] = baba["birey_id"]
        mevcut_birey["anne_id"] = anne["birey_id"]

        # Ebeveynlere başlangıç genotiplerini ata (eğer yoksa)
        if not baba.get("genotip"):
            baba["genotip"] = {}
        if not anne.get("genotip"):
            anne["genotip"] = {}
        
        hastalik_detaylari = get_hastalik_detaylari()
        for hastalik_adi in hastalik_detaylari:
            # Eğer ebeveynin bu hastalık için genotipi yoksa, başlangıç genotipi ata
            if hastalik_adi not in baba["genotip"] or baba["genotip"][hastalik_adi] is None:
                baba["genotip"][hastalik_adi] = determine_initial_genotype(hastalik_adi, baba["cinsiyet"])
            if hastalik_adi not in anne["genotip"] or anne["genotip"][hastalik_adi] is None:
                anne["genotip"][hastalik_adi] = determine_initial_genotype(hastalik_adi, anne["cinsiyet"])

        # Özyineleme: Ataları üretmeye devam et
        agaci_uret_ve_genleri_aktar(baba["birey_id"], hedef_kusak, True)
        agaci_uret_ve_genleri_aktar(anne["birey_id"], hedef_kusak, True)

        # GEN AKTARIMI (Ata Üretimi Sonrası) - Çocuğa (mevcut_birey) genleri aktar
        anne_genotipleri = anne.get("genotip", {})
        baba_genotipleri = baba.get("genotip", {})
        cocuk_genotipleri = {}
        
        if not mevcut_birey.get("genotip"):
            mevcut_birey["genotip"] = {}
        
        hastalik_detaylari = get_hastalik_detaylari()
        for hastalik_adi, details in hastalik_detaylari.items():
            sekil = details['sekil']
            anne_genotip = anne_genotipleri.get(hastalik_adi)
            baba_genotip = baba_genotipleri.get(hastalik_adi)

            if anne_genotip and baba_genotip:
                # Çocuğun cinsiyetine göre kalıtım yap
                cocuk_cinsiyeti = mevcut_birey["cinsiyet"]
                
                # Cinsiyet bazlı kalıtım kuralları
                if sekil == 'X-Bağlı Çekinik':
                    if cocuk_cinsiyeti == 'Erkek':
                        # Erkek çocuk: Anne X kromozomu + Baba Y kromozomu
                        allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                        # Baba Y kromozomu verir
                        cocuk_genotipleri[hastalik_adi] = allele_anneden + 'Y'
                    else:  # Kadın çocuk
                        # Kadın çocuk: Anne X kromozomu + Baba X kromozomu
                        allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                        allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                        # Baba X veriyorsa (normal durumda Y verir ama X de verebilir teorik olarak)
                        if allele_babadan == 'Y':
                            # Bu durum olamaz, tekrar dene veya varsayılan kullan
                            allele_babadan = 'Xn'  # Varsayılan
                        cocuk_genotipleri[hastalik_adi] = allele_anneden + allele_babadan
                        
                elif sekil == 'Çekinik':
                    # Otozomal çekinik: Her iki ebeveynden birer alel
                    allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                    allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                    
                    if allele_anneden and allele_babadan:
                        cocuk_genotipleri[hastalik_adi] = "".join(sorted([allele_anneden, allele_babadan]))
            else:
                # Ebeveyn genotipleri eksikse, çocuğa da başlangıç genotipi ata
                cocuk_genotipleri[hastalik_adi] = determine_initial_genotype(
                    hastalik_adi, mevcut_birey["cinsiyet"]
                )
        
        # Çocuğun genotiplerini güncelle
        for hastalik_adi, genotype in cocuk_genotipleri.items():
            mevcut_birey["genotip"][hastalik_adi] = genotype

    # --- ÇOCUK ÜRETİMİ (İleriye Doğru) ---
    else:
        cocuk_sayisi = random.randint(0, 3)
        for _ in range(cocuk_sayisi):
            cocuk_dogum_yili = mevcut_birey["dogum_yili"] + random.randint(20, 35)
            if cocuk_dogum_yili > datetime.date.today().year:
                continue

            cocugun_cinsiyeti = random.choice(["Erkek", "Kadın"])
            cocugun_soyadi = mevcut_birey["soyad"]

            cocuk = kisi_olustur(cocugun_cinsiyeti, cocugun_soyadi, cocuk_dogum_yili, mevcut_kusak + 1)
            cocuk["genotip"] = {}

            # GEN AKTARIMI (Çocuk Üretimi Sırasında)
            anne = None
            baba = None
            if mevcut_birey["cinsiyet"] == "Kadın":
                anne = mevcut_birey
                # Eş için başlangıç genotipleri oluştur
                baba_genotipleri = {}
                hastalik_detaylari = get_hastalik_detaylari()
                for hastalik_adi in hastalik_detaylari:
                    baba_genotipleri[hastalik_adi] = determine_initial_genotype(hastalik_adi, "Erkek")
                baba = {"genotip": baba_genotipleri, "cinsiyet": "Erkek"}
            else:  # mevcut_birey Erkek ise
                baba = mevcut_birey
                # Eş için başlangıç genotipleri oluştur
                anne_genotipleri = {}
                hastalik_detaylari = get_hastalik_detaylari()
                for hastalik_adi in hastalik_detaylari:
                    anne_genotipleri[hastalik_adi] = determine_initial_genotype(hastalik_adi, "Kadın")
                anne = {"genotip": anne_genotipleri, "cinsiyet": "Kadın"}

            cocuk_genotipleri = {}
            if anne and baba:
                hastalik_detaylari = get_hastalik_detaylari()
                for hastalik_adi, details in hastalik_detaylari.items():
                    sekil = details['sekil']
                    anne_genotip = anne.get("genotip", {}).get(hastalik_adi)
                    baba_genotip = baba.get("genotip", {}).get(hastalik_adi)

                    if anne_genotip and baba_genotip:
                        # Çocuğun cinsiyetine göre kalıtım yap
                        if sekil == 'X-Bağlı Çekinik':
                            if cocugun_cinsiyeti == 'Erkek':
                                # Erkek çocuk: Anne X kromozomu + Baba Y kromozomu
                                allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                                cocuk_genotipleri[hastalik_adi] = allele_anneden + 'Y'
                            else:  # Kadın çocuk
                                # Kadın çocuk: Anne X kromozomu + Baba X kromozomu
                                allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                                allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                                if allele_babadan == 'Y':
                                    allele_babadan = 'Xn'  # Varsayılan
                                cocuk_genotipleri[hastalik_adi] = allele_anneden + allele_babadan
                        elif sekil == 'Çekinik':
                            # Otozomal çekinik: Her iki ebeveynden birer alel
                            allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                            allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                            if allele_anneden and allele_babadan:
                                cocuk_genotipleri[hastalik_adi] = "".join(sorted([allele_anneden, allele_babadan]))
                    else:
                        # Ebeveyn genotipleri eksikse, çocuğa başlangıç genotipi ata
                        cocuk_genotipleri[hastalik_adi] = determine_initial_genotype(
                            hastalik_adi, cocugun_cinsiyeti
                        )

            cocuk["genotip"] = cocuk_genotipleri

            # Çocuğa ebeveyn ID'sini ata
            if mevcut_birey["cinsiyet"] == "Kadın":
                cocuk["anne_id"] = mevcut_birey["birey_id"]
            else:
                cocuk["baba_id"] = mevcut_birey["birey_id"]

            TUM_BIREYLER[cocuk["birey_id"]] = cocuk

            # Özyineleme
            agaci_uret_ve_genleri_aktar(cocuk["birey_id"], hedef_kusak, False)


def olustur_final_listesi(kullanici_birey_id=None):
    """
    Bireylerden fenotipleri hesaplayarak final listesini oluşturur.
    
    Args:
        kullanici_birey_id: Kullanıcının birey ID'si (None ise tüm bireylere hastalık atanır)
    """
    son_soy_agaci_listesi = []
    hastalik_detaylari = get_hastalik_detaylari()
    
    for birey_id, birey in TUM_BIREYLER.items():
        # Kullanıcıya (kök kullanıcıya) hastalık atanmaz - her zaman sağlıklı görünsün
        if kullanici_birey_id and birey_id == kullanici_birey_id:
            birey_kopya = birey.copy()
            if "genotip" in birey_kopya:
                del birey_kopya["genotip"]
            birey_kopya["hastaliklar"] = "Sağlıklı"
            son_soy_agaci_listesi.append(birey_kopya)
            continue
        
        # Diğer bireyler için normal fenotip hesaplaması
        fenotip_listesi = []
        birey_genotipleri = birey.get("genotip", {})
        
        for hastalik_adi, genotype in birey_genotipleri.items():
            fenotip_durum = determine_phenotype(hastalik_adi, genotype, birey["cinsiyet"])
            if fenotip_durum:
                fenotip_listesi.append({"hastalik": hastalik_adi, "durum": fenotip_durum})

        birey_kopya = birey.copy()
        if "genotip" in birey_kopya:
            del birey_kopya["genotip"]

        birey_kopya["hastaliklar"] = fenotip_listesi if fenotip_listesi else "Sağlıklı"
        son_soy_agaci_listesi.append(birey_kopya)

    return son_soy_agaci_listesi

