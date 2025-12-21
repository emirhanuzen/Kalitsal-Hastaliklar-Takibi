# soy_agaci_ureteci.py
# GENETİK SİMÜLASYON - Ana fonksiyon
# Bu dosya modüler yapıda yeniden düzenlenmiştir

import datetime
import sys
import random

from genetics.genetics import calculate_allele_frequencies, get_hastalik_detaylari
from genetics.family_tree import (
    reset_bireyler,
    get_bireyler,
    agaci_uret_ve_genleri_aktar,
    olustur_final_listesi
)
from genetics.person import kisi_olustur
from genetics.carrier_guarantee import ensure_at_least_one_carrier


def uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi_sql, sql_conn=None):
    """
    GENETİK SİMÜLASYONLU ANA ALGORİTMA FONKSİYONU
    
    Args:
        kullanici_kayit_verisi: User registration data
        hastalik_listesi_sql: Disease list from SQL
        sql_conn: Optional SQL connection for TC uniqueness checking
    """
    # 1. Bireyler sözlüğünü sıfırla
    reset_bireyler()
    from genetics.person import reset_tc_tracker
    reset_tc_tracker()  # Reset TC tracker for new tree generation
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
    print(f">>> DEBUG (ureteci): Kullanıcı yaşı hesaplandı: {yas}", file=sys.stderr)
    GERIYE_HEDEF_KUSAK = 1
    ILERIYE_HEDEF_KUSAK = 4
    KULLANICI_KUSAGI = 0

    # TEST AMAÇLI: Kuşak belirleme mantığı
    # 18–60 yaş arası kullanıcıları ZORUNLU olarak 3. kuşak (ebeveyn) yap
    if 18 <= yas <= 60:
        KULLANICI_KUSAGI = 3
    elif yas > 60:
        # 60 yaş üstü: 2. kuşak (büyükanne/büyükbaba)
        KULLANICI_KUSAGI = 2
    else:
        # 18 yaş altı: 4. kuşak (çocuk/son kuşak)
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
    # Önce ataları üret (geriye doğru)
    agaci_uret_ve_genleri_aktar(kok_birey_id, GERIYE_HEDEF_KUSAK, True, sql_conn)
    # Sonra çocukları ve ileri kuşakları üret (ileri doğru)
    agaci_uret_ve_genleri_aktar(kok_birey_id, ILERIYE_HEDEF_KUSAK, False, sql_conn)

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

    # 9. Kök kullanıcının doğrudan çocuklarının isim + TC bilgilerini çıkar
    cocuk_bilgileri = []
    for birey in son_soy_agaci_listesi:
        anne_id = birey.get("anne_id")
        baba_id = birey.get("baba_id")
        if anne_id == kok_birey_id or baba_id == kok_birey_id:
            tc = birey.get("kurgusal_tc")
            if tc:
                ad = birey.get("isim", "") or ""
                soyad = birey.get("soyad", "") or ""
                tam_ad = f"{ad} {soyad}".strip() or ad or "İsimsiz Çocuk"
                cocuk_bilgileri.append({
                    "isim": tam_ad,
                    "tc": str(tc)
                })

    print(f">>> DEBUG (ureteci): Kök kullanıcının {len(cocuk_bilgileri)} çocuğu üretildi.", file=sys.stderr)

    return son_soy_agaci_listesi, kok_birey_id, cocuk_bilgileri
