# soy_agaci_ureteci.py
# GENETİK SİMÜLASYON - Ana fonksiyon
# Bu dosya modüler yapıda yeniden düzenlenmiştir

import datetime
import sys

from genetics.genetics import calculate_allele_frequencies, get_hastalik_detaylari
from genetics.family_tree import (
    reset_bireyler,
    get_bireyler,
    agaci_uret_ve_genleri_aktar,
    olustur_final_listesi
)
from genetics.person import kisi_olustur
from genetics.carrier_guarantee import ensure_at_least_one_carrier


def uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi_sql):
    """GENETİK SİMÜLASYONLU ANA ALGORİTMA FONKSİYONU"""
    
    # 1. Bireyler sözlüğünü sıfırla
    reset_bireyler()
    TUM_BIREYLER = get_bireyler()

    # 2. Hastalık detaylarını ve alel frekanslarını hesapla
    calculate_allele_frequencies(hastalik_listesi_sql)
    if not get_hastalik_detaylari():
        print("--- UYARI (ureteci): Geçerli hastalık detayı yok, genetik simülasyon yapılamayacak.", file=sys.stderr)
        return [], None

    # 3. Kullanıcı bilgilerini al ve yaş/kuşak belirle
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
    
    if yas > 50:
        KULLANICI_KUSAGI = 2
    elif 18 <= yas <= 50:
        KULLANICI_KUSAGI = 3
    else:
        KULLANICI_KUSAGI = 4

    # 4. Kök kullanıcıyı oluştur
    kok_kullanici = kisi_olustur(
        kullanici_cinsiyet,
        kullanici_soyadi,
        dogum_tarihi_nesnesi.year,
        KULLANICI_KUSAGI,
        kullanici_tc,
        kullanici_ismi
    )
    TUM_BIREYLER[kok_kullanici["birey_id"]] = kok_kullanici
    kok_birey_id = kok_kullanici["birey_id"]

    # 5. Ağacı üret ve genleri aktar
    agaci_uret_ve_genleri_aktar(kok_birey_id, GERIYE_HEDEF_KUSAK, True)  # Önce ataları üret

    # 6. Kullanıcının genotipini ebeveynlerinden kalıtım yoluyla hesapla
    # (Kullanıcıya doğrudan hastalık atanmaz, sadece genotip hesaplanır)
    if kok_kullanici.get("anne_id") and kok_kullanici.get("baba_id"):
        anne_birey = TUM_BIREYLER.get(kok_kullanici["anne_id"])
        baba_birey = TUM_BIREYLER.get(kok_kullanici["baba_id"])
        
        if anne_birey and baba_birey:
            if not kok_kullanici.get("genotip"):
                kok_kullanici["genotip"] = {}
            
            hastalik_detaylari = get_hastalik_detaylari()
            anne_genotipleri = anne_birey.get("genotip", {})
            baba_genotipleri = baba_birey.get("genotip", {})
            
            for hastalik_adi, details in hastalik_detaylari.items():
                if hastalik_adi not in kok_kullanici["genotip"]:
                    sekil = details['sekil']
                    anne_genotip = anne_genotipleri.get(hastalik_adi)
                    baba_genotip = baba_genotipleri.get(hastalik_adi)
                    
                    if anne_genotip and baba_genotip:
                        from genetics.genetics import inherit_allele
                        
                        if sekil == 'X-Bağlı Çekinik':
                            if kullanici_cinsiyet == 'Erkek':
                                allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                                kok_kullanici["genotip"][hastalik_adi] = allele_anneden + 'Y'
                            else:  # Kadın
                                allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                                allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                                if allele_babadan == 'Y':
                                    allele_babadan = 'Xn'  # Varsayılan
                                kok_kullanici["genotip"][hastalik_adi] = allele_anneden + allele_babadan
                        elif sekil == 'Çekinik':
                            allele_anneden = inherit_allele(anne_genotip, sekil, "Kadın")
                            allele_babadan = inherit_allele(baba_genotip, sekil, "Erkek")
                            if allele_anneden and allele_babadan:
                                kok_kullanici["genotip"][hastalik_adi] = "".join(sorted([allele_anneden, allele_babadan]))

    # 7. En az bir taşıyıcı birey garantisi
    # Soy ağacında mutlaka en az bir taşıyıcı olmalı ki risk analizi yapılabilsin
    ensure_at_least_one_carrier(kok_birey_id)
    
    # 8. Fenotipleri belirle ve son listeyi oluştur
    # Kullanıcıya (kök birey) hastalık atanmaz - her zaman "Sağlıklı" görünsün
    son_soy_agaci_listesi = olustur_final_listesi(kullanici_birey_id=kok_birey_id)

    return son_soy_agaci_listesi, kok_birey_id
