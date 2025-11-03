# routes.py
# API endpoint'leri
# DÜZELTME: Gereksiz/hatalı import kaldırıldı ve başlangıç kontrolü düzeltildi.

from flask import jsonify, request
import pyodbc  # SQL bağlantısı bu dosyada oluşturuluyor
import sys

# Bu importların çalışması için database.py, validators.py ve services/ klasörünün
# bu dosyayla aynı dizin yapısında olması gerekir.
from database import SQL_SERVER_CONNECTION_STRING, mongo_db, get_hastalik_listesi
from validators import validate_register_data
from services.registration_service import register_new_family, register_existing_family


# !!! KALDIRILDI: Bu import hem gereksizdi (kullanılmıyordu) hem de 'dainamik' yazım hatası vardı.
# from soy_agaci_ureteci import uret_dainamik_soy_agaci


def register_user():
    """Ana kayıt API endpoint'i"""

    # <<< DÜZELTME: Kontrol, algoritma fonksiyonuna değil, veritabanı bağlantılarına bakmalı >>>
    if SQL_SERVER_CONNECTION_STRING is None or mongo_db is None:
        return jsonify({
            "durum": "hata",
            "mesaj": "Sunucu başlangıç hatası: Veritabanı bağlantısı kurulamadı."
        }), 500

    # JSON verisini al
    data = request.get_json()
    if not data:
        return jsonify({
            "durum": "hata",
            "mesaj": "İstek gövdesi (body) boş olamaz. JSON verisi gönderin."
        }), 400

    # Veriyi doğrula
    validated_data, error_msg, status_code = validate_register_data(data)
    if error_msg:
        return jsonify({"durum": "hata", "mesaj": error_msg}), status_code

    # SQL bağlantısını aç
    sql_conn = None
    try:
        sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING, autocommit=False)
        cursor = sql_conn.cursor()
        print(">>> DEBUG: SQL Bağlantısı açıldı (autocommit=False).")
    except Exception as e:
        print(f"!!! SQL Server bağlantı hatası (kayıt sırasında): {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": f"Veritabanı bağlantı hatası."}), 500

    try:
        # Senaryo seçimi: Ebeveyn TC boş mu dolu mu?
        if not validated_data['ebeveyn_tc']:
            # <<< DÜZELTME: Senaryo 1'in artık hastalık listesine ihtiyacı var >>>
            hastalik_listesi = get_hastalik_listesi(sql_conn)
            if not hastalik_listesi:
                print("!!! HATA: Hastalık listesi SQL'den çekilemedi.")
                return jsonify({"durum": "hata", "mesaj": "Hastalık listesi veritabanından çekilemedi."}), 500

            result, status_code = register_new_family(validated_data, sql_conn, cursor, mongo_db, hastalik_listesi)
        else:
            result, status_code = register_existing_family(validated_data, sql_conn, cursor, mongo_db)

        return jsonify(result), status_code

    except Exception as e:
        # Beklenmedik bir hata olursa (örn: register_new_family içinde)
        print(f"!!! Ana kayıt bloğunda beklenmedik hata: {e}", file=sys.stderr)
        try:
            sql_conn.rollback()  # SQL işlemini geri al
        except:
            pass
        return jsonify({"durum": "hata", "mesaj": f"İşlem sırasında beklenmedik bir sunucu hatası oluştu: {e}"}), 500

    finally:
        if sql_conn:
            try:
                sql_conn.close()
            except:
                pass
            print(">>> DEBUG: SQL Bağlantısı kapatıldı.")


def test_connection():
    """Test endpoint'i - veritabanı bağlantılarını test eder"""
    results = {}

    if SQL_SERVER_CONNECTION_STRING is not None:
        try:
            with pyodbc.connect(SQL_SERVER_CONNECTION_STRING) as conn:
                results['sql_server'] = "Bağlantı BAŞARILI!"
        except Exception as e:
            results['sql_server'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['sql_server'] = "HATA: Bağlantı dizesi ayarlanamadı."

    if mongo_db is not None:
        try:
            mongo_db.client.admin.command('ping')
            results['mongodb'] = "Bağlantı BAŞARILI!"
        except Exception as e:
            results['mongodb'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['mongodb'] = "HATA: Bağlantı kurulamadı."

    return jsonify(results)