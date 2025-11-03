# genetics/person.py
# Kişi oluşturma fonksiyonları

import uuid
import random
from genetics.constants import ERKEK_ISIMLERI, KADIN_ISIMLERI


def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None, isim=None):
    """Yeni bir kişi oluşturur."""
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
        "hastaliklar": [],  # Sonradan fenotipe göre doldurulacak
        "genotip": {}  # Genotipleri burada saklayacağız
    }
    
    return yeni_kisi

