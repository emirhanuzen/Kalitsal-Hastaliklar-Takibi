# Kalitsal-Hastaliklar-Takibi

Proje, kullanıcıların kayıt olduğu web tabanlı kalıtsal hastalık takip sistemidir. Gerçek soy ağacı verilerine erişimimiz olmadığı için bu prototip modelinde yapay zeka yalnızca sentetik/sahte verilerle kullanıcıya örnek bir soy ağacı oluşturur ve veritabanındaki hastalık profilleri üzerinden istatistiksel risk analizi sunar.

## Kurulum

### 1. Python Bağımlılıkları

Proje klasöründe terminal açıp aşağıdaki komutu çalıştırın:

```bash
pip install -r requirements.txt
```

Bu komut şu paketleri yükleyecektir:
- Flask (Web framework)
- pyodbc (SQL Server bağlantısı)
- pymongo (MongoDB bağlantısı)
- bcrypt (Şifre hashleme)

### 2. Veritabanı Gereksinimleri

Projenin çalışması için iki veritabanına ihtiyaç vardır:

#### MS SQL Server
- SQL Server'ın kurulu ve çalışır durumda olması gerekir
- `KRAP_DB` adında bir veritabanı oluşturulmalıdır
- `Users` ve `Hastaliklar` tabloları oluşturulmalıdır
- ODBC Driver yüklü olmalıdır (Windows'ta genellikle varsayılan olarak yüklüdür)

#### MongoDB
- MongoDB bağlantı string'i `app.py` dosyasında tanımlanmıştır
- MongoDB Atlas veya yerel MongoDB kullanılabilir

### 3. Projeyi Çalıştırma

```bash
python app.py
```

Flask uygulaması varsayılan olarak `http://localhost:5000` adresinde çalışacaktır.

### 4. Veritabanı Bağlantı Ayarları

`config.py` dosyasındaki bağlantı ayarlarını kendi sisteminize göre düzenleyin:

- `SQL_SERVER_SUNUCU_ADI`: SQL Server sunucu adı (varsayılan: `localhost`)
- `SQL_SERVER_VERITABANI_ADI`: Veritabanı adı (varsayılan: `KRAP_DB`)
- `MONGO_CONNECTION_STRING`: MongoDB bağlantı string'i

## Proje Yapısı

Proje modüler yapıda düzenlenmiştir:

```
Kalitsal-Hastaliklar-Takibi-main/
├── app.py                      # Ana Flask uygulaması
├── config.py                   # Konfigürasyon ayarları
├── database.py                 # Veritabanı bağlantıları
├── routes.py                   # API endpoint'leri
├── validators.py               # Veri doğrulama fonksiyonları
├── soy_agaci_ureteci.py       # Ana soy ağacı üretim fonksiyonu
├── services/
│   ├── __init__.py
│   └── registration_service.py # Kayıt işlem mantığı
└── genetics/
    ├── __init__.py
    ├── constants.py            # İsim listeleri ve sabitler
    ├── genetics.py             # Genetik hesaplamalar
    ├── person.py               # Kişi oluşturma
    └── family_tree.py          # Soy ağacı üretimi
```

### Modül Açıklamaları

- **app.py**: Flask uygulamasını başlatır ve route'ları kaydeder
- **config.py**: Tüm konfigürasyon ayarları (veritabanı, Flask vb.)
- **database.py**: MongoDB ve SQL Server bağlantıları, veritabanı yardımcı fonksiyonları
- **routes.py**: API endpoint tanımları
- **validators.py**: Kullanıcı verilerinin doğrulanması
- **services/registration_service.py**: Kayıt işlemlerinin iş mantığı (yeni aile, mevcut aileye katılma)
- **genetics/**: Genetik simülasyon ve soy ağacı üretimi modülleri
  - **constants.py**: İsim listeleri
  - **genetics.py**: Alel frekansları, genotip, fenotip hesaplamaları
  - **person.py**: Kişi oluşturma fonksiyonları
  - **family_tree.py**: Soy ağacı oluşturma ve gen aktarımı
- **soy_agaci_ureteci.py**: Ana soy ağacı üretim fonksiyonu (diğer modülleri kullanır)
