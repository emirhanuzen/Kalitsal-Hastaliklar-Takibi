# app.py
# GÖREVİ: Sadece web isteklerini alır, veritabanlarıyla konuşur ve cevap döndürür.

from flask import Flask, jsonify, request
import pyodbc  # MS SQL Server
import pymongo # MongoDB
import bcrypt  # Şifre hashleme
import datetime # Yaş hesaplaması için
import sys
import uuid # Bunu da import edelim (kullanılmasa bile)

# Algoritma dosyamızdan ana fonksiyonu çağırıyoruz
try:
    from soy_agaci_ureteci import uret_dinamik_soy_agaci
except ImportError:
    print("!!! HATA: soy_agaci_ureteci.py dosyası bulunamadı veya içe aktarılamadı.", file=sys.stderr)
    uret_dinamik_soy_agaci = None

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# --- 1. VERİTABANI BAĞLANTILARI ---
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
mongo_db = None
mongo_client = None
try:
    mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    mongo_db = mongo_client["KRAP_NoSQL_DB"]
    print(">>> MongoDB'ye başarıyla bağlandı.")
except Exception as e:
    print(f"!!! MongoDB BAĞLANTI HATASI: {e}", file=sys.stderr)
    if mongo_client:
         mongo_client.close()

SQL_SERVER_SUNUCU_ADI = 'localhost' # SSMS'teki sunucu adın
SQL_SERVER_VERİTABANI_ADI = 'KRAP_DB' # Oluşturduğun DB
SQL_SERVER_CONNECTION_STRING = None
try:
    SQL_SERVER_CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SQL_SERVER_SUNUCU_ADI};'
        f'DATABASE={SQL_SERVER_VERİTABANI_ADI};'
        'Trusted_Connection=yes;'
    )
    with pyodbc.connect(SQL_SERVER_CONNECTION_STRING) as conn:
        print(">>> MS SQL Server'a başarıyla bağlandı.")
except Exception as e:
    print(f"!!! MS SQL Server BAĞLANTI HATASI: {e}", file=sys.stderr)
    SQL_SERVER_CONNECTION_STRING = None

# --- 2. YARDIMCI FONKSİYONLAR ---
def get_hastalik_listesi(sql_conn):
    hastaliklar = []
    try:
        cursor = sql_conn.cursor()
        cursor.execute("SELECT HastalikAdi, GorulmeOrani FROM Hastaliklar")
        hastaliklar = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(f"Hastalık listesi çekilemedi: {e}", file=sys.stderr)
    return hastaliklar

# --- 3. ANA KAYIT API ENDPOINT'İ ---
@app.route('/api/register', methods=['POST'])
def register_user():

    if SQL_SERVER_CONNECTION_STRING is None or mongo_db is None or uret_dinamik_soy_agaci is None:
         return jsonify({"durum": "hata", "mesaj": "Sunucu başlangıç hatası: Veritabanı veya algoritma modülü yüklenemedi."}), 500

    try:
        data = request.get_json()
        if not data: # Eğer body boşsa
             return jsonify({"durum": "hata", "mesaj": "İstek gövdesi (body) boş olamaz. JSON verisi gönderin."}), 400

        email = data['email']
        password = data['password']
        kendi_tc = data['kendi_tc']
        dogum_tarihi_str = data['dogum_tarihi'] # "YYYY-MM-DD"
        isim = data['isim']
        soyad = data['soyad']
        ebeveyn_tc = data.get('ebeveyn_tc') # None olabilir
    except KeyError as e:
        return jsonify({"durum": "hata", "mesaj": f"Eksik JSON verisi: {e} alanı gerekli."}), 400
    except Exception as e:
         return jsonify({"durum": "hata", "mesaj": f"JSON verisi işlenirken hata: {e}"}), 400

    if not all([email, password, kendi_tc, dogum_tarihi_str, isim, soyad]):
         return jsonify({"durum": "hata", "mesaj": "Email, şifre, TC, doğum tarihi, isim ve soyad alanları zorunludur."}), 400
    if len(kendi_tc) != 11 or not kendi_tc.isdigit():
         return jsonify({"durum": "hata", "mesaj": "Kurgusal TC 11 haneli bir sayı olmalıdır."}), 400

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    except Exception as e:
        print(f"!!! Şifre hashleme hatası: {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": "Şifre işlenirken bir sorun oluştu."}), 500

    try:
        dogum_tarihi = datetime.datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
        if dogum_tarihi.year < 1900 or dogum_tarihi > datetime.date.today():
             raise ValueError("Geçersiz doğum yılı.")
    except ValueError as e:
        return jsonify({"durum": "hata", "mesaj": f"Doğum tarihi formatı hatalı veya geçersiz: {e}. Lütfen YYYY-MM-DD formatında geçerli bir tarih girin."}), 400

    sql_conn = None
    mongo_tree_id_for_rollback = None # Hata durumunda MongoDB kaydını silebilmek için
    insert_result_for_rollback = None

    try:
        sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING, autocommit=False) # Otomatik commit'i kapatalım
        cursor = sql_conn.cursor()
        print(">>> DEBUG: SQL Bağlantısı açıldı (autocommit=False).")
    except Exception as e:
        print(f"!!! SQL Server bağlantı hatası (kayıt sırasında): {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": f"Veritabanı bağlantı hatası."}), 500

    # --- SENARYO 1: YENİ AİLE EVRENİ BAŞLAT ---
    if not ebeveyn_tc:
        print(">>> Senaryo 1 başlatılıyor: Yeni Aile Evreni Başlat")
        try:
            cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", (email, kendi_tc))
            if cursor.fetchone():
                return jsonify({"durum": "hata", "mesaj": "Bu e-posta veya Kurgusal TC zaten kayıtlı."}), 409

            hastalik_listesi = get_hastalik_listesi(sql_conn) # Aynı bağlantıyı kullanalım
            if not hastalik_listesi:
                 return jsonify({"durum": "hata", "mesaj": "Hastalık listesi veritabanından çekilemedi."}), 500

            print(">>> DEBUG: Hastalık listesi çekildi, algoritma çağrılıyor...")
            kullanici_kayit_verisi = {"isim": isim, "soyad": soyad, "dogum_tarihi": dogum_tarihi, "kendi_tc": kendi_tc}
            try:
                soy_agaci_dokumani, kok_birey_id = uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi)
                print(f">>> DEBUG: Algoritma çalıştı, {len(soy_agaci_dokumani)} birey üretildi.")
            except Exception as e:
                 print(f"!!! Algoritma çalışma hatası: {e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": f"Soy ağacı üretilirken hata oluştu: {e}"}), 500

            try:
                 family_trees_collection = mongo_db["FamilyTrees"]
                 print(">>> DEBUG: MongoDB'ye insert deneniyor...")
                 insert_result = family_trees_collection.insert_one({"agac_verisi": soy_agaci_dokumani})
                 mongo_tree_id = str(insert_result.inserted_id)
                 # Rollback için bilgileri sakla
                 mongo_tree_id_for_rollback = insert_result.inserted_id
                 insert_result_for_rollback = insert_result
                 print(f">>> DEBUG: MongoDB insert BAŞARILI, ID: {mongo_tree_id}")
            except Exception as e:
                 print(f"!!! MongoDB kayıt hatası: {e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": f"Soy ağacı kaydedilirken hata oluştu: {e}"}), 500

            try:
                print(">>> DEBUG: SQL Server'a INSERT deneniyor...")
                # <<< HATA BURADAYDI, DÜZELTİLDİ: VALUES ve parametre sırası güncellendi >>>
                cursor.execute(
                    """
                    INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (email, hashed_password, kendi_tc, dogum_tarihi, isim, soyad, mongo_tree_id, kok_birey_id)
                )
                print(">>> DEBUG: SQL INSERT komutu gönderildi, commit deneniyor...")
                sql_conn.commit() # Değişiklikleri onayla
                print(">>> DEBUG: SQL commit BAŞARILI!")
            except pyodbc.IntegrityError as e:
                 print(f"!!! SQL Integrity Hatası (kayıt): {e}", file=sys.stderr)
                 # MongoDB'deki kaydı sil
                 if mongo_tree_id_for_rollback: family_trees_collection.delete_one({"_id": mongo_tree_id_for_rollback})
                 return jsonify({"durum": "hata", "mesaj": "E-posta veya Kurgusal TC başka bir kullanıcı tarafından alınmış olabilir."}), 409
            except Exception as e:
                 print(f"!!! SQL Kayıt Hatası: {e}", file=sys.stderr)
                 # MongoDB'deki kaydı sil
                 if mongo_tree_id_for_rollback: family_trees_collection.delete_one({"_id": mongo_tree_id_for_rollback})
                 return jsonify({"durum": "hata", "mesaj": f"Kullanıcı kaydedilirken hata oluştu: {e}"}), 500

            print(f">>> Yeni kullanıcı {email} ({isim} {soyad}) ve soy ağacı {mongo_tree_id} başarıyla oluşturuldu.")
            return jsonify({
                "durum": "basarili",
                "mesaj": "Yeni aile evreni başarıyla oluşturuldu.",
                "FamilyTreeID": mongo_tree_id
            }), 201

        except Exception as e:
            print(f"!!! Senaryo 1'de beklenmedik hata: {e}", file=sys.stderr)
            try:
                if sql_conn: sql_conn.rollback() # Hata olursa geri almayı dene
            except: pass
            # MongoDB kaydını da silmeye çalışalım
            try:
                if mongo_tree_id_for_rollback:
                     mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                     print(">>> DEBUG: Hata nedeniyle MongoDB kaydı geri alındı.")
            except Exception as mongo_e:
                 print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
            return jsonify({"durum": "hata", "mesaj": f"Kayıt sırasında beklenmedik bir sunucu hatası oluştu."}), 500
        finally:
            if sql_conn:
                sql_conn.close()
                print(">>> DEBUG: SQL Bağlantısı kapatıldı.")

    # --- SENARYO 2: VAR OLAN EVRENE KATIL ---
    else:
        # (Bu bölüm aynı)
        print(">>> Senaryo 2 başlatılıyor: Var Olan Evrene Katıl")
        if sql_conn:
            sql_conn.close()
        return jsonify({"durum": "basarili", "mesaj": "Senaryo 2 henüz kodlanmadı."}), 501


# --- Test Endpoint'i ---
@app.route('/test-baglanti')
def test_baglanti():
     # ... (kod aynı) ...
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


if __name__ == '__main__':
    app.run(debug=True)