# genetics/person.py
# Kişi oluşturma fonksiyonları

import uuid
import random
import sys
from genetics.constants import ERKEK_ISIMLERI, KADIN_ISIMLERI

# Global set to track generated TCs in current session (for uniqueness within tree generation)
_generated_tcs = set()


def generate_unique_tc(sql_conn=None, max_attempts=100):
    """
    Generate a unique 11-digit TC number.
    Checks against database if sql_conn is provided, otherwise uses in-memory set.
    Returns: 11-digit string TC
    """
    global _generated_tcs
    
    for attempt in range(max_attempts):
        # Generate 11-digit TC (first digit can't be 0, so range 1-9)
        tc = ''.join([str(random.randint(1, 9)) for _ in range(11)])
        
        # Check in-memory set first
        if tc in _generated_tcs:
            continue
        
        # Check database if connection provided
        if sql_conn:
            try:
                cursor = sql_conn.cursor()
                cursor.execute("SELECT UserID FROM Users WHERE KurgusalTC = ?", (tc,))
                if cursor.fetchone():
                    cursor.close()
                    continue  # TC exists in DB, try again
                cursor.close()
            except Exception as e:
                print(f">>> WARNING: Could not check TC uniqueness in database: {e}", file=sys.stderr)
                # Continue anyway - use in-memory check
        
        # TC is unique
        _generated_tcs.add(tc)
        return tc
    
    # Fallback: if all attempts failed, generate with timestamp component
    import time
    timestamp_part = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    random_part = ''.join([str(random.randint(1, 9)) for _ in range(5)])
    tc = random_part + timestamp_part
    _generated_tcs.add(tc)
    return tc


def reset_tc_tracker():
    """Reset the in-memory TC tracker. Call this before generating a new tree."""
    global _generated_tcs
    _generated_tcs = set()


def kisi_olustur(cinsiyet, soyad, dogum_yili, kusak, kurgusal_tc=None, isim=None, sql_conn=None):
    """
    Yeni bir kişi oluşturur.
    
    Args:
        cinsiyet: "Erkek" or "Kadın"
        soyad: Last name
        dogum_yili: Birth year
        kusak: Generation number
        kurgusal_tc: Optional TC. If None, generates unique TC.
        isim: Optional first name. If None, generates random name.
        sql_conn: Optional SQL connection for TC uniqueness check.
    """
    if isim is None:
        if cinsiyet == "Kadın":
            isim = random.choice(KADIN_ISIMLERI)
        else:
            isim = random.choice(ERKEK_ISIMLERI)
    
    birey_id = str(uuid.uuid4())
    
    if kurgusal_tc is None:
        kurgusal_tc = generate_unique_tc(sql_conn)
    
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

