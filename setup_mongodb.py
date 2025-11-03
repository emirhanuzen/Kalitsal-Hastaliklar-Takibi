# setup_mongodb.py
# MongoDB veritabanı ve collection'ları oluşturma scripti

import pymongo
import sys
from config import MONGO_CONNECTION_STRING, MONGO_DATABASE_NAME

def setup_mongodb():
    """MongoDB'de veritabanı ve collection'ları oluşturur."""
    try:
        print(f">>> MongoDB bağlantısı deneniyor: {MONGO_CONNECTION_STRING}")
        
        # MongoDB'ye bağlan
        client = pymongo.MongoClient(MONGO_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        
        # Bağlantıyı test et
        client.admin.command('ping')
        print(">>> MongoDB'ye başarıyla bağlandı!")
        
        # Veritabanını al (yoksa oluşturulur)
        db = client[MONGO_DATABASE_NAME]
        print(f">>> Veritabanı seçildi: {MONGO_DATABASE_NAME}")
        
        # FamilyTrees collection'ını oluştur (ilk kayıt yapıldığında otomatik oluşur ama kontrol edelim)
        family_trees = db["FamilyTrees"]
        
        # Collection'ın var olup olmadığını kontrol et
        collections = db.list_collection_names()
        if "FamilyTrees" in collections:
            print(">>> 'FamilyTrees' collection zaten mevcut.")
        else:
            print(">>> 'FamilyTrees' collection oluşturuluyor...")
            # Boş bir doküman ekleyerek collection'ı oluştur, sonra sil
            family_trees.insert_one({"_setup": True})
            family_trees.delete_one({"_setup": True})
            print(">>> 'FamilyTrees' collection başarıyla oluşturuldu!")
        
        # Veritabanı bilgilerini göster
        print(f"\n>>> MongoDB Kurulumu Tamamlandı!")
        print(f"    Veritabanı: {MONGO_DATABASE_NAME}")
        print(f"    Collection'lar: {db.list_collection_names()}")
        print(f"    Bağlantı: {MONGO_CONNECTION_STRING}\n")
        
        client.close()
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        print(f"!!! HATA: MongoDB sunucusuna bağlanılamıyor. Lütfen MongoDB'nin çalıştığından emin olun.", file=sys.stderr)
        print(f"    Bağlantı string'i: {MONGO_CONNECTION_STRING}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"!!! HATA: MongoDB kurulumu sırasında bir sorun oluştu: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("MongoDB Veritabanı Kurulum Scripti")
    print("=" * 60)
    success = setup_mongodb()
    if success:
        print(">>> Kurulum başarıyla tamamlandı!")
        sys.exit(0)
    else:
        print(">>> Kurulum başarısız oldu!")
        sys.exit(1)

