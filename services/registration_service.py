# services/registration_service.py
# Kayıt işlem mantığı

import sys
from bson import ObjectId
import pyodbc

from database import get_hastalik_listesi, SQL_SERVER_CONNECTION_STRING, mongo_db
from soy_agaci_ureteci import uret_dinamik_soy_agaci


def register_new_family(data, sql_conn, cursor):
    """
    Senaryo 1: Yeni aile evreni başlat (Ebeveyn TC Boş)
    """
    print(">>> Senaryo 1 başlatılıyor: Yeni Aile Evreni Başlat")
    mongo_tree_id_for_rollback = None

    try:
        # Kullanıcı zaten var mı kontrolü
        cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", 
                      (data['email'], data['kendi_tc']))
        if cursor.fetchone():
            return {"durum": "hata", "mesaj": "Bu e-posta veya Kurgusal TC zaten kayıtlı."}, 409

        # Hastalıkları çek
        hastalik_listesi = get_hastalik_listesi(sql_conn)
        if not hastalik_listesi:
            return {"durum": "hata", "mesaj": "Hastalık listesi veritabanından çekilemedi."}, 500

        # Algoritmayı çağır
        print(">>> DEBUG: Algoritma çağrılıyor...")
        kullanici_kayit_verisi = {
            "isim": data['isim'],
            "soyad": data['soyad'],
            "dogum_tarihi": data['dogum_tarihi'],
            "kendi_tc": data['kendi_tc'],
            "cinsiyet": data['cinsiyet']
        }
        try:
            soy_agaci_dokumani, kok_birey_id = uret_dinamik_soy_agaci(kullanici_kayit_verisi, hastalik_listesi)
            print(f">>> DEBUG: Algoritma çalıştı, {len(soy_agaci_dokumani)} birey üretildi.")
        except Exception as e:
            print(f"!!! Algoritma çalışma hatası: {e}", file=sys.stderr)
            return {"durum": "hata", "mesaj": f"Soy ağacı üretilirken hata oluştu: {e}"}, 500

        # MongoDB'ye kaydet
        try:
            family_trees_collection = mongo_db["FamilyTrees"]
            print(">>> DEBUG: MongoDB'ye insert deneniyor...")
            insert_result = family_trees_collection.insert_one({"agac_verisi": soy_agaci_dokumani})
            mongo_tree_id = str(insert_result.inserted_id)
            mongo_tree_id_for_rollback = insert_result.inserted_id
            print(f">>> DEBUG: MongoDB insert BAŞARILI, ID: {mongo_tree_id}")
        except Exception as e:
            print(f"!!! MongoDB kayıt hatası: {e}", file=sys.stderr)
            return {"durum": "hata", "mesaj": f"Soy ağacı kaydedilirken hata oluştu: {e}"}, 500

        # SQL Server'a kaydet
        try:
            print(">>> DEBUG: SQL Server'a INSERT deneniyor...")
            # Hash'i base64 encode ederek sakla (VARCHAR uyumluluğu için)
            import base64
            hashed_password_encoded = base64.b64encode(data['hashed_password']).decode('utf-8')
            
            cursor.execute(
                """
                INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo)
                OUTPUT INSERTED.UserID
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (data['email'], hashed_password_encoded, data['kendi_tc'], 
                 data['dogum_tarihi'], data['isim'], data['soyad'], 
                 mongo_tree_id, kok_birey_id)
            )
            user_id = cursor.fetchone()[0]
            print(">>> DEBUG: SQL INSERT gönderildi, commit deneniyor...")
            sql_conn.commit()
            print(f">>> DEBUG: SQL commit BAŞARILI! UserID: {user_id}")
        except pyodbc.IntegrityError as e:
            print(f"!!! SQL Integrity Hatası (Senaryo 1): {e}", file=sys.stderr)
            try:
                sql_conn.rollback()
            except:
                pass
            if mongo_tree_id_for_rollback:
                try:
                    mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                except Exception as mongo_e:
                    print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
            return {"durum": "hata", "mesaj": "E-posta veya Kurgusal TC başka bir kullanıcı tarafından alınmış olabilir."}, 409
        except Exception as e:
            print(f"!!! SQL Kayıt Hatası (Senaryo 1): {e}", file=sys.stderr)
            try:
                sql_conn.rollback()
            except:
                pass
            if mongo_tree_id_for_rollback:
                try:
                    mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                except Exception as mongo_e:
                    print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
            return {"durum": "hata", "mesaj": f"Kullanıcı kaydedilirken hata oluştu: {e}"}, 500

        print(f">>> Yeni kullanıcı {data['email']} ({data['isim']} {data['soyad']}) ve soy ağacı {mongo_tree_id} başarıyla oluşturuldu.")
        return {
            "durum": "basarili",
            "mesaj": "Yeni aile evreni başarıyla oluşturuldu.",
            "FamilyTreeID": mongo_tree_id,
            "UserID": user_id
        }, 201

    except Exception as e:
        print(f"!!! Senaryo 1'de beklenmedik hata: {e}", file=sys.stderr)
        try:
            if sql_conn and not sql_conn.closed:
                sql_conn.rollback()
        except:
            pass
        if mongo_tree_id_for_rollback:
            try:
                mongo_db["FamilyTrees"].delete_one({"_id": mongo_tree_id_for_rollback})
                print(">>> DEBUG: Hata nedeniyle MongoDB kaydı geri alındı.")
            except Exception as mongo_e:
                print(f"!!! MongoDB rollback hatası: {mongo_e}", file=sys.stderr)
        return {"durum": "hata", "mesaj": f"Kayıt sırasında beklenmedik bir sunucu hatası oluştu."}, 500


def register_existing_family(data, sql_conn, cursor):
    """
    Senaryo 2: Var olan evrene katıl (Ebeveyn TC Dolu)
    """
    print(">>> Senaryo 2 başlatılıyor: Var Olan Evrene Katıl")

    try:
        # 1. Yeni kullanıcının Email veya Kendi TC'si zaten kayıtlı mı?
        cursor.execute("SELECT UserID FROM Users WHERE Email = ? OR KurgusalTC = ?", 
                      (data['email'], data['kendi_tc']))
        if cursor.fetchone():
            return {"durum": "hata", "mesaj": "Bu e-posta veya Kendi Kurgusal TC'niz zaten kayıtlı."}, 409

        # 2. Ebeveyn TC'si sistemde kayıtlı mı?
        print(f">>> DEBUG (Senaryo 2): Ebeveyn TC'si ile kullanıcı aranıyor: '{data['ebeveyn_tc']}'")
        cursor.execute("SELECT UserID, FamilyTreeID_Mongo, BireyID_Mongo FROM Users WHERE KurgusalTC = ?", 
                      (data['ebeveyn_tc'],))
        ebeveyn_kaydi = cursor.fetchone()
        print(f">>> DEBUG (Senaryo 2): Ebeveyn arama sorgusu sonucu: {ebeveyn_kaydi}")
        if not ebeveyn_kaydi:
            return {"durum": "hata", "mesaj": "Girilen Ebeveyn Kurgusal TC'si sistemde bulunamadı."}, 404

        ebeveyn_family_tree_id_str = ebeveyn_kaydi[1]
        ebeveyn_birey_id_mongo = ebeveyn_kaydi[2]

        if not ebeveyn_family_tree_id_str:
            return {"durum": "hata", "mesaj": "Ebeveyn kullanıcısının soy ağacı bilgisi eksik (FamilyTreeID_Mongo NULL)."}, 500

        # 3. Ebeveynin soy ağacını MongoDB'den bul
        family_trees_collection = mongo_db["FamilyTrees"]
        soy_agaci_dokumani = None
        try:
            print(f">>> DEBUG (Senaryo 2): MongoDB'de ağaç aranıyor, ID: {ebeveyn_family_tree_id_str}")
            ebeveyn_family_tree_id_object = ObjectId(ebeveyn_family_tree_id_str)
            soy_agaci_dokumani = family_trees_collection.find_one({"_id": ebeveyn_family_tree_id_object})
        except Exception as e:
            print(f"!!! MongoDB Ağaç Arama Hatası (Senaryo 2): {e}", file=sys.stderr)
            return {"durum": "hata", "mesaj": f"Ebeveynin soy ağacı bulunamadı veya ID formatı hatalı: {e}"}, 404

        if not soy_agaci_dokumani or "agac_verisi" not in soy_agaci_dokumani:
            print(f"!!! HATA (Senaryo 2): MongoDB'de {ebeveyn_family_tree_id_str} ID'li ağaç bulundu ama 'agac_verisi' alanı eksik.")
            return {"durum": "hata", "mesaj": "Ebeveynin soy ağacı verisi bozuk veya eksik."}, 500

        agac_verisi = soy_agaci_dokumani["agac_verisi"]
        print(f">>> DEBUG (Senaryo 2): Ağaç bulundu, içinde {len(agac_verisi)} birey var.")

        # 4. Ağacın içinde KENDİ TC'sine sahip bireyi ara
        cocuk_birey = None
        for birey in agac_verisi:
            if birey.get("kurgusal_tc") == data['kendi_tc']:
                cocuk_birey = birey
                print(f">>> DEBUG (Senaryo 2): Kendi TC'si ({data['kendi_tc']}) ile eşleşen birey bulundu: {cocuk_birey.get('isim')}")
                break

        if not cocuk_birey:
            return {"durum": "hata", "mesaj": "Girdiğiniz Kendi Kurgusal TC'niz, belirtilen ebeveynin soy ağacında bulunamadı."}, 404

        # 5. İlişkiyi Doğrula
        cocuk_anne_id = cocuk_birey.get("anne_id")
        cocuk_baba_id = cocuk_birey.get("baba_id")
        print(f">>> DEBUG (Senaryo 2): Çocuk Anne ID: {cocuk_anne_id}, Çocuk Baba ID: {cocuk_baba_id}, Ebeveyn Birey ID: {ebeveyn_birey_id_mongo}")
        if cocuk_anne_id != ebeveyn_birey_id_mongo and cocuk_baba_id != ebeveyn_birey_id_mongo:
            return {"durum": "hata", "mesaj": "Girilen ebeveyn kodu ile kendi kodunuz arasında aile bağı bulunamadı."}, 400

        # 6. Bu kimlik daha önce alınmış mı?
        cursor.execute("SELECT UserID FROM Users WHERE BireyID_Mongo = ?", (cocuk_birey["birey_id"],))
        if cursor.fetchone():
            return {"durum": "hata", "mesaj": "Bu kurgusal kimlik zaten başka bir kullanıcı tarafından alınmış."}, 409

        # 7. Yeni kullanıcıyı SQL'e kaydet
        print(">>> DEBUG (Senaryo 2): Tüm doğrulamalar başarılı, SQL'e INSERT deneniyor...")
        # Hash'i base64 encode ederek sakla (VARCHAR uyumluluğu için)
        import base64
        hashed_password_encoded = base64.b64encode(data['hashed_password']).decode('utf-8')
        
        cursor.execute(
            """
            INSERT INTO Users (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo)
            OUTPUT INSERTED.UserID
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (data['email'], hashed_password_encoded, data['kendi_tc'], 
             data['dogum_tarihi'], data['isim'], data['soyad'], 
             ebeveyn_family_tree_id_str, cocuk_birey["birey_id"])
        )
        user_id = cursor.fetchone()[0]
        sql_conn.commit()
        print(f">>> DEBUG (Senaryo 2): SQL commit BAŞARILI! UserID: {user_id}")

        print(f">>> Mevcut aileye katılım başarılı: {data['email']} ({data['isim']} {data['soyad']}), Ağaç ID: {ebeveyn_family_tree_id_str}")
        return {
            "durum": "basarili",
            "mesaj": "Mevcut aile evrenine başarıyla katıldınız.",
            "FamilyTreeID": ebeveyn_family_tree_id_str,
            "UserID": user_id
        }, 201

    except pyodbc.IntegrityError as e:
        print(f"!!! SQL Integrity Hatası (Senaryo 2): {e}", file=sys.stderr)
        try:
            sql_conn.rollback()
        except:
            pass
        return {"durum": "hata", "mesaj": "E-posta veya Kendi Kurgusal TC'niz başka bir kullanıcı tarafından alınmış olabilir."}, 409
    except Exception as e:
        print(f"!!! Senaryo 2'de beklenmedik hata: {e}", file=sys.stderr)
        try:
            if sql_conn and not sql_conn.closed:
                sql_conn.rollback()
        except:
            pass
        return {"durum": "hata", "mesaj": f"Katılım sırasında beklenmedik bir sunucu hatası oluştu: {e}"}, 500

