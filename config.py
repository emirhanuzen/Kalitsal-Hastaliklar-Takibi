# config.py
# Veritabanı ve uygulama konfigürasyon ayarları
# DÜZELTME: MongoDB bağlantısı Atlas olarak güncellendi.

# MongoDB Bağlantı Ayarları
# <<< DÜZELTME BURADA: Buraya Atlas'tan kopyaladığın bağlantı dizesini yapıştır >>>
# <<< '<password>' kısmını Atlas'ta oluşturduğun şifreyle değiştirmeyi unutma! >>>
MONGO_CONNECTION_STRING = 'mongodb+srv://Emirhan_Uzen:Codegen01"@krap.uczuzhr.mongodb.net/?appName=KRAP' # <<< ÖRNEK - KENDİ DİZENİ YAPIŞTIR
MONGO_DATABASE_NAME = 'KRAP_Atlas_DB' # Atlas'taki veritabanı adımız (veya ne verdiysen)

# MS SQL Server Ayarları
SQL_SERVER_SUNUCU_ADI = 'EMIRHAN'  # Bu artık doğru görünüyor
SQL_SERVER_VERITABANI_ADI = 'KRAP_DB'  # Oluşturduğun DB

# Flask Ayarları
JSON_AS_ASCII = False  # Türkçe karakterler için