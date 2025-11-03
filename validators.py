# validators.py
# Veri doğrulama fonksiyonları

import datetime
import bcrypt
import sys


def validate_register_data(data):
    """
    Kayıt verilerini doğrular ve döndürür.
    Hata durumunda (None, hata_mesajı, status_kodu) tuple döner.
    Başarılı durumda (doğrulanmış_veri, None, None) tuple döner.
    """
    try:
        # Zorunlu alanları kontrol et
        email = data.get('email')
        password = data.get('password')
        kendi_tc = str(data['kendi_tc']) if 'kendi_tc' in data and data['kendi_tc'] is not None else None
        dogum_tarihi_str = data.get('dogum_tarihi')
        isim = data.get('isim')
        soyad = data.get('soyad')
        cinsiyet = data.get('cinsiyet')
        ebeveyn_tc_raw = data.get('ebeveyn_tc')
        ebeveyn_tc = str(ebeveyn_tc_raw) if ebeveyn_tc_raw is not None and ebeveyn_tc_raw != "" else None

        # Temel kontrol
        if not all([email, password, kendi_tc, dogum_tarihi_str, isim, soyad, cinsiyet]):
            return None, "Email, şifre, TC, doğum tarihi, isim, soyad ve cinsiyet alanları zorunludur.", 400

        # Cinsiyet kontrolü
        if cinsiyet not in ["Erkek", "Kadın"]:
            return None, "Cinsiyet 'Erkek' veya 'Kadın' olmalıdır.", 400

        # TC kontrolü
        if not kendi_tc or len(kendi_tc) != 11 or not kendi_tc.isdigit():
            return None, "Kendi Kurgusal TC'niz 11 haneli bir sayı olmalıdır.", 400

        if ebeveyn_tc and (len(ebeveyn_tc) != 11 or not ebeveyn_tc.isdigit()):
            return None, "Ebeveyn Kurgusal TC 11 haneli bir sayı olmalıdır.", 400

        # Doğum tarihi kontrolü
        try:
            dogum_tarihi = datetime.datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
            if dogum_tarihi.year < 1900 or dogum_tarihi > datetime.date.today():
                return None, "Geçersiz doğum yılı. Lütfen YYYY-MM-DD formatında geçerli bir tarih girin.", 400
        except ValueError as e:
            return None, f"Doğum tarihi formatı hatalı: {e}. Lütfen YYYY-MM-DD formatında geçerli bir tarih girin.", 400

        # Şifreyi hashle
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        except Exception as e:
            print(f"!!! Şifre hashleme hatası: {e}", file=sys.stderr)
            return None, "Şifre işlenirken bir sorun oluştu.", 500

        # Doğrulanmış veriyi döndür
        validated_data = {
            'email': email,
            'hashed_password': hashed_password,
            'kendi_tc': kendi_tc,
            'dogum_tarihi': dogum_tarihi,
            'isim': isim,
            'soyad': soyad,
            'cinsiyet': cinsiyet,
            'ebeveyn_tc': ebeveyn_tc
        }

        return validated_data, None, None

    except KeyError as e:
        return None, f"Eksik JSON verisi: {e} alanı gerekli.", 400
    except Exception as e:
        return None, f"JSON verisi işlenirken hata: {e}", 400

