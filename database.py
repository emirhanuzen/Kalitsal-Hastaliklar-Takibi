# database.py
# Veritabanı bağlantıları ve yardımcı fonksiyonlar

import pyodbc
import pymongo
import sys
from config import (
    MONGO_CONNECTION_STRING,
    MONGO_DATABASE_NAME,
    SQL_SERVER_SUNUCU_ADI,
    SQL_SERVER_VERITABANI_ADI
)

# Global bağlantı değişkenleri
mongo_db = None
mongo_client = None
SQL_SERVER_CONNECTION_STRING = None


def initialize_mongodb():
    """MongoDB bağlantısını başlatır."""
    global mongo_db, mongo_client
    try:
        mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ping')  # Bağlantıyı test et
        mongo_db = mongo_client[MONGO_DATABASE_NAME]
        print(f">>> MongoDB'ye başarıyla bağlandı. Veritabanı: {mongo_db.name}")
        return True
    except Exception as e:
        print(f"!!! MongoDB BAĞLANTI HATASI: {e}", file=sys.stderr)
        if mongo_client:
            mongo_client.close()
        return False


def initialize_sql_server():
    """MS SQL Server bağlantısını başlatır."""
    global SQL_SERVER_CONNECTION_STRING
    try:
        # Önce "ODBC Driver 17 for SQL Server" dene, yoksa "SQL Server" kullan
        try:
            test_conn = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={SQL_SERVER_SUNUCU_ADI};'
                f'DATABASE={SQL_SERVER_VERITABANI_ADI};'
                f'Trusted_Connection=yes;',
                timeout=1
            )
            test_conn.close()
            driver_name = 'ODBC Driver 17 for SQL Server'
        except:
            driver_name = 'SQL Server'

        SQL_SERVER_CONNECTION_STRING = (
            f'DRIVER={{{driver_name}}};'
            f'SERVER={SQL_SERVER_SUNUCU_ADI};'
            f'DATABASE={SQL_SERVER_VERITABANI_ADI};'
            'Trusted_Connection=yes;'  # Windows Authentication için
        )
        with pyodbc.connect(SQL_SERVER_CONNECTION_STRING) as conn:
            print(f">>> MS SQL Server'a başarıyla bağlandı. Veritabanı: {SQL_SERVER_VERITABANI_ADI}")
        return True
    except Exception as e:
        print(f"!!! MS SQL Server BAĞLANTI HATASI: {e}", file=sys.stderr)
        SQL_SERVER_CONNECTION_STRING = None
        return False


def get_hastalik_listesi(sql_conn):
    """SQL Server'dan hastalık adı, oranı VE KALITIM ŞEKLİNİ çeker."""
    hastaliklar = []
    cursor = None
    try:
        if not sql_conn or sql_conn.closed:
            print("!!! HATA (get_hastalik_listesi): Geçersiz SQL bağlantısı.", file=sys.stderr)
            return []
        cursor = sql_conn.cursor()
        sorgu = "SELECT HastalikAdi, GorulmeOrani, KalitimSekli FROM Hastaliklar"
        print(f">>> DEBUG (get_hastalik_listesi): Sorgu çalıştırılıyor: {sorgu}")
        cursor.execute(sorgu)
        hastaliklar = cursor.fetchall()
        print(f">>> DEBUG (get_hastalik_listesi): Sorgu sonucu (fetchall): {hastaliklar}")
    except Exception as e:
        print(f"!!! HATA (get_hastalik_listesi): Hastalık listesi çekilemedi: {e}", file=sys.stderr)
        hastaliklar = []
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
    print(f">>> DEBUG (get_hastalik_listesi): Fonksiyon şu listeyi döndürüyor: {hastaliklar}")
    return hastaliklar


# Bağlantıları başlat
initialize_mongodb()
initialize_sql_server()

