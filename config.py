# config.py
# Veritabanı ve uygulama konfigürasyon ayarları

# MongoDB Bağlantı Ayarları
# Local MongoDB bağlantısı
MONGO_CONNECTION_STRING = 'mongodb+srv://Emirhan_Uzen:Codegen01"@krap.uczuzhr.mongodb.net/?appName=KRAP'  # Local MongoDB bağlantı dizesi
MONGO_DATABASE_NAME = 'KRAP_Atlas_DB'  # Local MongoDB veritabanı adı

# MS SQL Server Ayarları
SQL_SERVER_SUNUCU_ADI = 'HMD16\\SQLEXPRESS'  # SQL Server sunucu adı
SQL_SERVER_VERITABANI_ADI = 'KRAP_DB'  # Veritabanı adı

# Flask Ayarları
JSON_AS_ASCII = False  # Türkçe karakterler için