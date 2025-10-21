# app.py
# GÖREVİ: Sadece web isteklerini alır, veritabanlarıyla konuşur ve cevap döndürür.

from flask import Flask, jsonify, request
import pyodbc  # MS SQL Server
import pymongo  # MongoDB
import bcrypt  # Şifre hashleme
import datetime  # Yaş hesaplaması için
import sys

# YENİ EKLENDİ: Algoritma dosyamızdan ana fonksiyonu çağırıyoruz
from soy_agaci_ureteci import uret_dinamik_soy_agaci

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- 1. VERİTABANI BAĞLANTILARI ---
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
mongo_db = None
try:
    mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
    mongo_db = mongo_client["KRAP_NoSQL_DB"]
    mongo_client.server_info()
    print(">>> MongoDB'ye başarıyla bağlandı.")
except Exception as e:
    print(f"!!! MongoDB BAĞLANTI HATASI: {e}", file=sys.stderr)

SQL_SERVER_SUNUCU_ADI = 'localhost'  # SSMS'teki sunucu adın
SQL_SERVER_VERITABANI_ADI = 'KRAP_DB'  # Oluşturduğun DB
SQL_SERVER_CONNECTION_STRING = None
try:
    SQL_SERVER_CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SQL_SERVER_SUNUCU_ADI};'
        f'DATABASE={SQL_SERVER_VERITABANI_ADI};'
        'Trusted_Connection=yes;'
    )
    conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
    conn.close()
    print(">>> MS SQL Server'a başarıyla bağlandı.")
except Exception as e:
    print(f"!!! MS SQL Server BAĞLANTI HATASI: {e}", file=sys.stderr)


# --- 2. YARDIMCI FONKSİYONLAR ---
def get_hastalik_listesi(sql_conn):
    """SQL Server'dan hastalık listesini ve oranlarını çeker."""
    try:
        cursor = sql_conn.cursor()
        cursor.execute("SELECT HastalikAdi, GorulmeOrani FROM Hastaliklar")
        return cursor.fetchall()
    except Exception as e:
        print(f"Hastalık listesi çekilemedi: {e}", file=sys.stderr)
        return []


# --- 3. ANA KAYIT API ENDPOINT'İ ---
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        kendi_tc = data['kendi_tc']
        dogum_tarihi_str = data['dogum_tarihi']  # "YYYY-MM-DD"
        ebeveyn_tc = data.get('ebeveyn_tc')  # Bu boş olabilir (None)
    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": f"Eksik veya hatalı JSON verisi: {e}"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        dogum_tarihi = datetime.datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify(
            {"durum": "hata", "mesaj": "Doğum tarihi formatı hatalı. Lütfen YYYY-MM-DD formatında girin."}), 400

    try:
        sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
        cursor = sql_conn.cursor()
    except Exception as e:
        return jsonify({"durum": "hata", "mesaj": f"SQL Server bağlantı hatası: {e}"}), 500

    # --- SENARYO 1: YENİ AİLE EVRENİ BAŞLAT ---
    if not ebeveyn_tc:
        print("Senaryo 1 başlatılıyor: Yeni Aile Evreni Başlat")
        try:
            cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", (email, kendi_tc))
            if cursor.fetchone():
                sql_conn.close()
                return jsonify({"durum": "hata", "mesaj": "Bu e-posta veya Kurgusal TC zaten kayıtlı."}), 409

            hastalik_listesi = get_hastalik_listesi(sql_conn)
            if not hastalik_listesi:
                sql_conn.close()
                return jsonify({"durum": "hata", "mesaj": "Hastalık listesi veritabanından çekilemedi."}), 500

            # 6. ANA ALGORİTMAYI ÇAĞIR (Artık başka dosyadan geliyor)
            kullanici_bilgileri = {"dogum_tarihi": dogum_tarihi, "kendi_tc": kendi_tc}
            soy_agaci_dokumani, kok_birey_id = uret_dinamik_soy_agaci(kullanici_bilgileri, hastalik_listesi)

            family_trees_collection = mongo_db["FamilyTrees"]
            insert_result = family_trees_collection.insert_one({"agac_verisi": soy_agaci_dokumani})
            mongo_tree_id = str(insert_result.inserted_id)

            cursor.execute(
                """
                INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, FamilyTreeID_Mongo, BireyID_Mongo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (email, hashed_password, kendi_tc, dogum_tarihi, mongo_tree_id, kok_birey_id)
            )
            sql_conn.commit()

            print(f"Yeni kullanıcı {email} ve soy ağacı {mongo_tree_id} başarıyla oluşturuldu.")
            sql_conn.close()
            return jsonify({
                "durum": "basarili",
                "mesaj": "Yeni aile evreni başarıyla oluşturuldu.",
                "FamilyTreeID": mongo_tree_id
            }), 201

        except Exception as e:
            sql_conn.rollback()  # Hata olursa SQL işlemini geri al
            sql_conn.close()
            # MongoDB'de oluşan kaydı da silmek gerekebilir (daha ileri seviye)
            return jsonify({"durum": "hata", "mesaj": f"Senaryo 1 işlenirken hata oluştu: {e}"}), 500

    # --- SENARYO 2: VAR OLAN EVRENE KATIL ---
    else:
        print("Senaryo 2 başlatılıyor: Var Olan Evrene Katıl")
        # BU BÖLÜMÜ BİR SONRAKİ GÖREVDE KODLAYACAĞIZ
        sql_conn.close()
        return jsonify({"durum": "basarili", "mesaj": "Senaryo 2 henüz kodlanmadı."}), 501


# --- Test Endpoint'i (Hala duruyor) ---
@app.route('/test-baglanti')
def test_baglanti():
    results = {}
    if SQL_SERVER_CONNECTION_STRING is not None:
        try:
            conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
            results['sql_server'] = "Bağlantı BAŞARILI!"
            conn.close()
        except Exception as e:
            results['sql_server'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['sql_server'] = "HATA: Bağlantı dizesi ayarlanamadı."

    if mongo_db is not None:
        try:
            mongo_db.command('ping')
            results['mongodb'] = "Bağlantı BAŞARILI!"
        except Exception as e:
            results['mongodb'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['mongodb'] = "HATA: Bağlantı kurulamadı."
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)