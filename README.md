## 🧬 KRAP – Kalıtsal Risk Analiz Platformu

KRAP (Kalıtsal Risk Analiz Platformu), **kalıtsal hastalık risklerini** analiz etmek için tasarlanmış, hibrit veritabanı (SQL + NoSQL) kullanan bir **web tabanlı Mendel genetiği simülasyonudur**.  

Gerçek kişi verisi yerine tamamen **kurgusal (sentetik) soy ağaçları** üretir; ancak bu ağaçlardaki kalıtım, **Mendel kalıtım kuralları** (çekinik, taşıyıcı, X’e bağlı vb.) ile hesaplanır. Yani sistem, hastalıkları rastgele atamak yerine:

- Alel frekanslarını hesaplar,
- Genotip → fenotip dönüşümünü uygular,
- Kullanıcının kendisi ve ailesi için **olasılıksal risk tahmini** üretir.


## 🏗️ Mimarî ve Klasör Yapısı

Platform, modüler ve genişletilebilir bir mimarî ile tasarlanmıştır.

```bash
KRAP/
├── run.py                # 🚀 Giriş noktası – Flask uygulamasını başlatır
└── app/
    ├── __init__.py       # Flask app factory, config yükleme
    ├── db.py             # 🗄️ Hibrit veritabanı bağlantıları (SQL Server + MongoDB)
    ├── validators.py     # ✅ Girdi/doğrulama kuralları
    │
    ├── routes/           # 🌐 HTTP & API endpoint'leri
    │   ├── __init__.py
    │   ├── auth_routes.py        # Kayıt, giriş, profil, 'My Children' API'leri
    │   └── health_routes.py      # Sistem sağlık/test endpoint'leri (örn. /test-baglanti)
    │
    ├── services/         # 🧠 İş kuralları ve domain mantığı
    │   ├── __init__.py
    │   ├── soy_agaci_service.py  # Dinamik soy ağacı üretimi (ata + çocuk tarafı)
    │   ├── risk_service.py       # Kullanıcı bazlı kalıtsal risk analizi
    │   └── registration_service.py
    │         # Senaryo 1: Yeni aile başlat
    │         # Senaryo 2: Mevcut aileye katıl (Join Family)
    │
    ├── genetics/         # 🔬 Mendel genetiği hesaplamaları
    │   ├── __init__.py
    │   ├── constants.py  # İsim listeleri, sabitler, genetik parametreler
    │   ├── genetics.py   # Alel frekansları, genotip üretimi, X-bağlı/çekinik kurallar
    │   ├── person.py     # Kişi (birey) nesnesi oluşturma
    │   └── family_tree.py# Soy ağacı üzerinde gen aktarımı (ata → çocuk)
    │
    └── templates/        # 🖥️ Flask Jinja2 şablonları (UI)
        ├── index.html    # Giriş ekranı
        ├── kayit.html    # Kayıt formu (Senaryo 1 & 2)
        └── profil.html   # Profil + Soy ağacı + "Çocuklarım" paneli
```

> Not: Yukarıdaki yapı, projenin **modüler hedef mimarîsini** temsil eder. Bazı dosya adları/konumları refaktör sürecinde yakın gelecekte birebir bu yapıya taşınmaktadır.


## 🌟 Çekirdek Özellikler (Senaryolar)

### 1️⃣ Senaryo 1 – Yeni Aile Evreni Başlatma

- Kullanıcı, kendine ait **kurgusal TC**, doğum tarihi, cinsiyet vb. bilgilerle kayıt olur.
- Sistem, kullanıcının **yaşına göre kuşak konumunu** belirler (ör. 3. kuşak = ebeveyn).
- Ardından:
  - Geriye doğru **ata kuşakları** (anne, baba, büyükanne, büyükbaba, vb.),
  - İleriye doğru **çocuk ve torun kuşakları**
  - Her birey için **genotip** ve buna bağlı **hastalık durumu** (Sağlıklı / Taşıyıcı / Hasta)
    üretilir.
- Tüm soy ağacı, hibrit veritabanı modelinde saklanır:
  - SQL Server → Kullanıcı hesapları (`Users` tablosu)
  - MongoDB → Aile ağaçları (`FamilyTrees.agac_verisi` dokümanı)


### 2️⃣ Senaryo 2 – Mevcut Aileye Katılma (Join Family)

- Kullanıcı, kayıt olurken:
  - **Ebeveyn Kurgusal TC** (ebeveyninin kurgusal TC’si),
  - **Kendi Kurgusal TC** (ağaçta kendisine atanmış kurgusal TC)
    bilgilerini girer.
- İş akışı:
  1. SQL tarafında ebeveyn kullanıcısı bulunur (`FamilyTreeID_Mongo`, `BireyID_Mongo`).
  2. MongoDB’de aynı `FamilyTreeID_Mongo` ile aile ağacı çekilir.
  3. `kurgusal_tc == kendi_tc` olan birey, **ağaç içinde** bulunur.
  4. Ebeveyn ile çocuk arasında **soy bağı doğrulanır**  
     (`anne_id == parent_uuid` veya `baba_id == parent_uuid`).
  5. Bu birey için daha önce kullanıcı hesabı açılmış mı kontrol edilir.
  6. Her şey yolundaysa, yeni kullanıcı SQL’de bu bireye bağlanır:
     - `FamilyTreeID_Mongo` → ebeveynle aynı ağaç,
     - `BireyID_Mongo` → ağaçtaki mevcut bireyin UUID’si.

Bu sayede **aynı aile evreni içinde** birden fazla kullanıcı, farklı bireylere karşılık gelerek sistemi birlikte kullanabilir.


### 3️⃣ "Çocuklarım" Paneli 👶🧬

Profil sayfasında yer alan **"Çocuklarım ve Tahmini Riskleri (DEBUG)"** alanı sayesinde:

- Kullanıcı, kendi `BireyID_Mongo` ve `FamilyTreeID_Mongo` bilgileri ile:
  - MongoDB’deki soy ağacından **doğrudan çocuklarını** bulur,
  - Her çocuk için:
    - Ad & Soyad
    - Cinsiyet, doğum yılı
    - Hastalık durumu (renkli etiketler: Kırmızı = Hasta, Turuncu = Taşıyıcı, Yeşil = Sağlıklı)
    - Basitleştirilmiş **genetik risk notu** (ör. “Taşıyıcı → kendi çocuklarına %50 aktarım riski”)
  - Ayrıca çocukların **kurgusal TC**’leri debug amaçlı gösterilir ve tek tıkla kopyalanabilir.

Bu panel, özellikle **Senaryo 2 testleri** için ebeveyn → çocuk geçişlerini kolayca doğrulamak amacıyla tasarlanmıştır.


## 🧰 Teknoloji Yığını

- **Dil & Framework**
  - Python 3.x
  - Flask (Web framework)
- **Veritabanları**
  - Microsoft SQL Server (Kullanıcı hesapları, hastalık master verisi)
  - MongoDB Atlas (Soy ağaçları, birey dokümanları)
- **Bağlantı & ORM Benzeri Katmanlar**
  - PyODBC (`pyodbc`) – SQL Server bağlantısı
  - PyMongo (`pymongo`) – MongoDB bağlantısı
- **Güvenlik & Yardımcılar**
  - `bcrypt` – Şifre hashleme
  - `validators.py` – Girdi ve iş kuralları doğrulama


## 🚀 Kurulum ve Çalıştırma

### 1. Depoyu Klonla

```bash
git clone https://github.com/<kullanici>/KRAP.git
cd KRAP
```

### 2. Sanal Ortam Oluştur ve Aktifleştir (Önerilir)

```bash
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. Python Bağımlılıklarını Yükle

```bash
pip install -r requirements.txt
```

Başlıca paketler:
- Flask
- pyodbc
- pymongo
- bcrypt

### 4. Konfigürasyon – `config.py` ⚙️

`config.py` dosyasında aşağıdaki alanları kendi ortamınıza göre güncelleyin:

- **SQL Server**
  - `SQL_SERVER_SUNUCU_ADI` → Örn: `localhost\\SQLEXPRESS`
  - `SQL_SERVER_VERITABANI_ADI` → Örn: `KRAP_DB`
- **MongoDB**
  - `MONGO_CONNECTION_STRING` → MongoDB Atlas connection string’iniz

Ayrıca:
- `JSON_AS_ASCII`, `SECRET_KEY` vb. Flask ayarlarını da burada yönetebilirsiniz.

### 5. Veritabanı Gereksinimleri

#### 🗄️ SQL Server

- `KRAP_DB` adında bir veritabanı oluşturun.
- En azından aşağıdaki tablolar gereklidir:
  - `Users` (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo, …)
  - `Hastaliklar` (hastalık adı, kalıtım şekli, frekanslar vb.)
- Uygun bir ODBC Driver yüklü olmalıdır (Windows’ta genelde hazır gelir).

#### 🍃 MongoDB Atlas

- `FamilyTrees` koleksiyonunda her aile için bir doküman tutulur:
  - `_id` → ObjectId
  - `agac_verisi` → birey listesi (her birey: `birey_id`, `kurgusal_tc`, `anne_id`, `baba_id`, `hastaliklar`, …)


### 6. Uygulamayı Çalıştırma

Projeyi başlatmak için:

```bash
python run.py
```

Flask uygulaması varsayılan olarak şu adreste çalışır:

```text
http://localhost:5000
```


## 🤝 Katkıda Bulunma

Öneri, hata bildirimi veya katkı göndermek isterseniz:

- Issue açabilir,
- Pull Request gönderebilir,
- Veya kod içinde `TODO` / `DEBUG` notlarını takip ederek eksik alanları iyileştirebilirsiniz.

KRAP halen **araştırma ve prototip** niteliğinde bir projedir; özellikle genetik modelleme ve risk analizi katmanında yapılacak katkılar, gerçekçi simülasyon kalitesini önemli ölçüde artıracaktır. 🙌

