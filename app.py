# app.py
# GÖREVİ: Web isteklerini alır, veritabanlarıyla konuşur, algoritmayı çağırır ve cevap döndürür.
# SON GÜNCELLEME: Cinsiyet alanı eklendi.

from flask import Flask, jsonify, request
import pyodbc  # MS SQL Server
import pymongo # MongoDB
import bcrypt  # Şifre hashleme
import datetime # Yaş hesaplaması için
from bson import ObjectId # MongoDB ID tipi için
import sys     # Hata yazdırma için

# Algoritma dosyamızdan ana fonksiyonu çağırıyoruz
try:
    # Bu importun çalışması için soy_agaci_ureteci.py dosyasının
    # app.py ile aynı klasörde olduğundan emin olmalısın.
    from soy_agaci_ureteci import uret_dinamik_soy_agaci
except ImportError:
    print("!!! HATA: soy_agaci_ureteci.py dosyası bulunamadı veya içe aktarılamadı.", file=sys.stderr)
    uret_dinamik_soy_agaci = None

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False # Türkçe karakterler için

# --- 1. VERİTABANI BAĞLANTILARI ---
# Ayarları kendi sistemine göre düzenlemeyi unutma!
MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
SQL_SERVER_SUNUCU_ADI = 'localhost' # SSMS'teki sunucu adın
SQL_SERVER_VERITABANI_ADI = 'KRAP_DB' # Oluşturduğun DB

mongo_db = None
mongo_client = None
SQL_SERVER_CONNECTION_STRING = None

try:
    # MongoDB Bağlantısı ve Testi
    mongo_client = pymongo.MongoClient(MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping') # Bağlantıyı test et
    mongo_db = mongo_client["KRAP_NoSQL_DB"]
    print(f">>> MongoDB'ye başarıyla bağlandı. Veritabanı: {mongo_db.name}")
except Exception as e:
    print(f"!!! MongoDB BAĞLANTI HATASI: {e}", file=sys.stderr)
    if mongo_client: mongo_client.close()

try:
    # MS SQL Server Bağlantı String'i ve Testi
    SQL_SERVER_CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SQL_SERVER_SUNUCU_ADI};'
        f'DATABASE={SQL_SERVER_VERITABANI_ADI};'
        'Trusted_Connection=yes;' # Windows Authentication için
    )
    with pyodbc.connect(SQL_SERVER_CONNECTION_STRING) as conn:
        print(f">>> MS SQL Server'a başarıyla bağlandı. Veritabanı: {SQL_SERVER_VERITABANI_ADI}")
except Exception as e:
    print(f"!!! MS SQL Server BAĞLANTI HATASI: {e}", file=sys.stderr)
    SQL_SERVER_CONNECTION_STRING = None

# --- 2. YARDIMCI FONKSİYON: Hastalık Listesi ---
def get_hastalik_listesi(sql_conn):
    hastaliklar = []
    cursor = None
    try:
        if not sql_conn or sql_conn.closed:
             print("!!! HATA (get_hastalik_listesi): Geçersiz SQL bağlantısı.", file=sys.stderr)
             return []
        cursor = sql_conn.cursor()
        cursor.execute("SELECT HastalikAdi, GorulmeOrani FROM Hastaliklar")
        hastaliklar = cursor.fetchall()
    except Exception as e:
        print(f"!!! HATA (get_hastalik_listesi): Hastalık listesi çekilemedi: {e}", file=sys.stderr)
    finally:
         if cursor:
              try: cursor.close()
              except: pass
    return hastaliklar

# --- 3. ANA KAYIT API ENDPOINT'İ ---
@app.route('/api/register', methods=['POST'])
def register_user():

    if SQL_SERVER_CONNECTION_STRING is None or mongo_db is None or uret_dinamik_soy_agaci is None:
         return jsonify({"durum": "hata", "mesaj": "Sunucu başlangıç hatası: Veritabanı veya algoritma modülü yüklenemedi."}), 500

    # 1. JSON Verisini Al ve Doğrula
    try:
        data = request.get_json()
        if not data:
             return jsonify({"durum": "hata", "mesaj": "İstek gövdesi (body) boş olamaz. JSON verisi gönderin."}), 400

        email = data['email']
        password = data['password']
        kendi_tc = str(data['kendi_tc']) if 'kendi_tc' in data and data['kendi_tc'] is not None else None
        dogum_tarihi_str = data['dogum_tarihi'] # Format: "YYYY-MM-DD"
        isim = data['isim']
        soyad = data['soyad']
        cinsiyet = data['cinsiyet'] # <<< CİNSİYET ALANI EKLENDİ >>>
        ebeveyn_tc_raw = data.get('ebeveyn_tc')
        ebeveyn_tc = str(ebeveyn_tc_raw) if ebeveyn_tc_raw is not None and ebeveyn_tc_raw != "" else None

    except KeyError as e:
        return jsonify({"durum": "hata", "mesaj": f"Eksik JSON verisi: {e} alanı gerekli."}), 400
    except Exception as e:
         return jsonify({"durum": "hata", "mesaj": f"JSON verisi işlenirken hata: {e}"}), 400

    # Temel Veri Kontrolleri (Cinsiyet kontrolü eklendi)
    if not all([email, password, kendi_tc, dogum_tarihi_str, isim, soyad, cinsiyet]): # <<< Cinsiyet eklendi
         return jsonify({"durum": "hata", "mesaj": "Email, şifre, TC, doğum tarihi, isim, soyad ve cinsiyet alanları zorunludur."}), 400
    if cinsiyet not in ["Erkek", "Kadın"]: # <<< Cinsiyet değeri kontrolü
         return jsonify({"durum": "hata", "mesaj": "Cinsiyet 'Erkek' veya 'Kadın' olmalıdır."}), 400
    if not kendi_tc or len(kendi_tc) != 11 or not kendi_tc.isdigit():
         return jsonify({"durum": "hata", "mesaj": "Kendi Kurgusal TC'niz 11 haneli bir sayı olmalıdır."}), 400
    if ebeveyn_tc and (len(ebeveyn_tc) != 11 or not ebeveyn_tc.isdigit()):
         return jsonify({"durum": "hata", "mesaj": "Ebeveyn Kurgusal TC 11 haneli bir sayı olmalıdır."}), 400

    # 2. Şifreyi Güvenli Hale Getir (Hash)
    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    except Exception as e:
        print(f"!!! Şifre hashleme hatası: {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": "Şifre işlenirken bir sorun oluştu."}), 500

    # 3. Doğum Tarihini Kontrol Et ve Çevir
    try:
        dogum_tarihi = datetime.datetime.strptime(dogum_tarihi_str, '%Y-%m-%d').date()
        if dogum_tarihi.year < 1900 or dogum_tarihi > datetime.date.today():
             raise ValueError("Geçersiz doğum yılı.")
    except ValueError as e:
        return jsonify({"durum": "hata", "mesaj": f"Doğum tarihi formatı hatalı veya geçersiz: {e}. Lütfen YYYY-MM-DD formatında geçerli bir tarih girin."}), 400

    # 4. SQL Bağlantısını Aç
    sql_conn = None
    mongo_tree_id_for_rollback = None

    try:
        sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING, autocommit=False)
        cursor = sql_conn.cursor()
        print(">>> DEBUG: SQL Bağlantısı açıldı (autocommit=False).")
    except Exception as e:
        print(f"!!! SQL Server bağlantı hatası (kayıt sırasında): {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": f"Veritabanı bağlantı hatası."}), 500

    # --- SENARYO 1: YENİ AİLE EVRENİ BAŞLAT (Ebeveyn TC Boş) ---
    if not ebeveyn_tc:
        print(">>> Senaryo 1 başlatılıyor: Yeni Aile Evreni Başlat")
        try:
            # Kullanıcı zaten var mı kontrolü
            cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", (email, kendi_tc))
            if cursor.fetchone():
                return jsonify({"durum": "hata", "mesaj": "Bu e-posta veya Kurgusal TC zaten kayıtlı."}), 409

            # Hastalıkları çek
            hastalik_listesi = get_hastalik_listesi(sql_conn)
            if not hastalik_listesi:
                 return jsonify({"durum": "hata", "mesaj": "Hastalık listesi veritabanından çekilemedi."}), 500

            # Algoritmayı çağır (CİNSİYET BİLGİSİNİ DE GÖNDER)
            print(">>> DEBUG: Algoritma çağrılıyor...")
            kullanici_kayit_verisi = {
                "isim": isim,
                "soyad": soyad,
                "dogum_tarihi": dogum_tarihi,
                "kendi_tc": kendi_tc,
                "cinsiyet": cinsiyet # <<< CİNSİYET BURADA GÖNDERİLİYOR >>>
            }
            try:
                soy_agaci_dokumani, kok_birey_id = uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi)
                print(f">>> DEBUG: Algoritma çalıştı, {len(soy_agaci_dokumani)} birey üretildi.")
            except Exception as e:
                 print(f"!!! Algoritma çalışma hatası: {e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": f"Soy ağacı üretilirken hata oluştu: {e}"}), 500

            # MongoDB'ye kaydet
            try:
                 family_trees_collection = mongo_db["FamilyTrees"]
                 print(">>> DEBUG: MongoDB'ye insert deneniyor...")
                 insert_result = family_trees_collection.insert_one({"agac_verisi": soy_agaci_dokumani})
                 mongo_tree_id = str(insert_result.inserted_id)
                 mongo_tree_id_for_rollback = insert_result.inserted_id # ObjectId olarak sakla
                 print(f">>> DEBUG: MongoDB insert BAŞARILI, ID: {mongo_tree_id}")
            except Exception as e:
                 print(f"!!! MongoDB kayıt hatası: {e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": f"Soy ağacı kaydedilirken hata oluştu: {e}"}), 500

            # SQL Server'a kaydet (Isim, Soyad ile birlikte)
            try:
                print(">>> DEBUG: SQL Server'a INSERT deneniyor...")
                cursor.execute(
                    """
                    INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (email, hashed_password, kendi_tc, dogum_tarihi, isim, soyad, mongo_tree_id, kok_birey_id)
                )
                print(">>> DEBUG: SQL INSERT gönderildi, commit deneniyor...")
                sql_conn.commit() # Tüm işlemler başarılıysa onayla
                print(">>> DEBUG: SQL commit BAŞARILI!")
            except pyodbc.IntegrityError as e:
                 print(f"!!! SQL Integrity Hatası (Senaryo 1): {e}", file=sys.stderr)
                 try: sql_conn.rollback()
                 except: pass
                 if mongo_tree_id_for_rollback:
                     try: mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                     except Exception as mongo_e: print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": "E-posta veya Kurgusal TC başka bir kullanıcı tarafından alınmış olabilir."}), 409
            except Exception as e:
                 print(f"!!! SQL Kayıt Hatası (Senaryo 1): {e}", file=sys.stderr)
                 try: sql_conn.rollback()
                 except: pass
                 if mongo_tree_id_for_rollback:
                     try: mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                     except Exception as mongo_e: print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
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
                if sql_conn and not sql_conn.closed: sql_conn.rollback()
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
                try: sql_conn.close()
                except: pass
                print(">>> DEBUG: SQL Bağlantısı kapatıldı.")

    # --- SENARYO 2: VAR OLAN EVRENE KATIL (Ebeveyn TC Dolu) ---
    else:
        print(">>> Senaryo 2 başlatılıyor: Var Olan Evrene Katıl")
        try:
            # 1. Yeni kullanıcının Email veya Kendi TC'si zaten kayıtlı mı?
            cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", (email, kendi_tc))
            if cursor.fetchone():
                return jsonify({"durum": "hata", "mesaj": "Bu e-posta veya Kendi Kurgusal TC'niz zaten kayıtlı."}), 409

            # 2. Ebeveyn TC'si sistemde kayıtlı mı?
            print(f">>> DEBUG (Senaryo 2): Ebeveyn TC'si ile kullanıcı aranıyor: '{ebeveyn_tc}'")
            cursor.execute("SELECT UserID, FamilyTreeID_Mongo, BireyID_Mongo FROM Users WHERE KurgusalTC = ?", (ebeveyn_tc,))
            ebeveyn_kaydi = cursor.fetchone()
            print(f">>> DEBUG (Senaryo 2): Ebeveyn arama sorgusu sonucu: {ebeveyn_kaydi}")
            if not ebeveyn_kaydi:
                return jsonify({"durum": "hata", "mesaj": "Girilen Ebeveyn Kurgusal TC'si sistemde bulunamadı."}), 404

            ebeveyn_user_id_sql = ebeveyn_kaydi[0]
            ebeveyn_family_tree_id_str = ebeveyn_kaydi[1]
            ebeveyn_birey_id_mongo = ebeveyn_kaydi[2]

            if not ebeveyn_family_tree_id_str:
                 return jsonify({"durum": "hata", "mesaj": "Ebeveyn kullanıcısının soy ağacı bilgisi eksik (FamilyTreeID_Mongo NULL)."}), 500

            # 3. Ebeveynin soy ağacını MongoDB'den bul
            family_trees_collection = mongo_db["FamilyTrees"]
            soy_agaci_dokumani = None
            try:
                 print(f">>> DEBUG (Senaryo 2): MongoDB'de ağaç aranıyor, ID: {ebeveyn_family_tree_id_str}")
                 ebeveyn_family_tree_id_object = ObjectId(ebeveyn_family_tree_id_str)
                 soy_agaci_dokumani = family_trees_collection.find_one({"_id": ebeveyn_family_tree_id_object})
            except Exception as e:
                 print(f"!!! MongoDB Ağaç Arama Hatası (Senaryo 2): {e}", file=sys.stderr)
                 return jsonify({"durum": "hata", "mesaj": f"Ebeveynin soy ağacı bulunamadı veya ID formatı hatalı: {e}"}), 404

            if not soy_agaci_dokumani or "agac_verisi" not in soy_agaci_dokumani:
                print(f"!!! HATA (Senaryo 2): MongoDB'de {ebeveyn_family_tree_id_str} ID'li ağaç bulundu ama 'agac_verisi' alanı eksik.")
                return jsonify({"durum": "hata", "mesaj": "Ebeveynin soy ağacı verisi bozuk veya eksik."}), 500

            agac_verisi = soy_agaci_dokumani["agac_verisi"]
            print(f">>> DEBUG (Senaryo 2): Ağaç bulundu, içinde {len(agac_verisi)} birey var.")

            # 4. Ağacın içinde KENDİ TC'sine sahip bireyi ara
            cocuk_birey = None
            for birey in agac_verisi:
                if birey.get("kurgusal_tc") == kendi_tc:
                    cocuk_birey = birey
                    print(f">>> DEBUG (Senaryo 2): Kendi TC'si ({kendi_tc}) ile eşleşen birey bulundu: {cocuk_birey.get('isim')}")
                    break

            if not cocuk_birey:
                return jsonify({"durum": "hata", "mesaj": "Girdiğiniz Kendi Kurgusal TC'niz, belirtilen ebeveynin soy ağacında bulunamadı."}), 404

            # 5. İlişkiyi Doğrula
            cocuk_anne_id = cocuk_birey.get("anne_id")
            cocuk_baba_id = cocuk_birey.get("baba_id")
            print(f">>> DEBUG (Senaryo 2): Çocuk Anne ID: {cocuk_anne_id}, Çocuk Baba ID: {cocuk_baba_id}, Ebeveyn Birey ID: {ebeveyn_birey_id_mongo}")
            if cocuk_anne_id != ebeveyn_birey_id_mongo and cocuk_baba_id != ebeveyn_birey_id_mongo:
                return jsonify({"durum": "hata", "mesaj": "Girilen ebeveyn kodu ile kendi kodunuz arasında aile bağı bulunamadı."}), 400

            # 6. Bu kimlik daha önce alınmış mı? (BireyID_Mongo ile kontrol)
            cursor.execute("SELECT UserID FROM Users WHERE BireyID_Mongo = ?", (cocuk_birey["birey_id"],))
            if cursor.fetchone():
                 return jsonify({"durum": "hata", "mesaj": "Bu kurgusal kimlik zaten başka bir kullanıcı tarafından alınmış."}), 409

            # 7. Yeni kullanıcıyı SQL'e kaydet
            print(">>> DEBUG (Senaryo 2): Tüm doğrulamalar başarılı, SQL'e INSERT deneniyor...")
            cursor.execute(
                """
                INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (email, hashed_password, kendi_tc, dogum_tarihi, isim, soyad, ebeveyn_family_tree_id_str, cocuk_birey["birey_id"])
            )
            sql_conn.commit()
            print(">>> DEBUG (Senaryo 2): SQL commit BAŞARILI!")

            print(f">>> Mevcut aileye katılım başarılı: {email} ({isim} {soyad}), Ağaç ID: {ebeveyn_family_tree_id_str}")
            return jsonify({
                "durum": "basarili",
                "mesaj": "Mevcut aile evrenine başarıyla katıldınız.",
                "FamilyTreeID": ebeveyn_family_tree_id_str
            }), 201

        except pyodbc.IntegrityError as e: # Email veya TC unique constraint hatası
            print(f"!!! SQL Integrity Hatası (Senaryo 2): {e}", file=sys.stderr)
            try: sql_conn.rollback()
            except: pass
            return jsonify({"durum": "hata", "mesaj": "E-posta veya Kendi Kurgusal TC'niz başka bir kullanıcı tarafından alınmış olabilir."}), 409
        except Exception as e: # Diğer tüm beklenmedik hatalar
            print(f"!!! Senaryo 2'de beklenmedik hata: {e}", file=sys.stderr)
            try:
                if sql_conn and not sql_conn.closed: sql_conn.rollback()
            except: pass
            return jsonify({"durum": "hata", "mesaj": f"Katılım sırasında beklenmedik bir sunucu hatası oluştu: {e}"}), 500
        finally:
            if sql_conn:
                try: sql_conn.close()
                except: pass
                print(">>> DEBUG: SQL Bağlantısı kapatıldı.")


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

# Sunucuyu Başlatma Bloğu
if __name__ == '__main__':
    app.run(debug=True)