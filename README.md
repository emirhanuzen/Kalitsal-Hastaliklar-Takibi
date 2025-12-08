# 🧬 KRAP – Kalıtsal Risk Analiz Platformu

**KRAP (Kalıtsal Risk Analiz Platformu)**, kalıtsal hastalık risklerini analiz etmek için tasarlanmış, hibrit veritabanı mimarisi (SQL Server + MongoDB) kullanan modern bir **web tabanlı Mendel genetiği simülasyon platformudur**.

Platform, gerçek kişi verisi yerine tamamen **kurgusal (sentetik) soy ağaçları** üretir; ancak bu ağaçlardaki kalıtım, **Mendel kalıtım kuralları** (çekinik, taşıyıcı, X'e bağlı vb.) ile bilimsel olarak hesaplanır. Sistem, hastalıkları rastgele atamak yerine:

- ✅ **Alel frekanslarını** hesaplar
- ✅ **Genotip → fenotip** dönüşümünü uygular
- ✅ Kullanıcının kendisi ve ailesi için **olasılıksal risk tahmini** üretir
- ✅ **Google Gemini AI** ile hastalık bilgilerini zenginleştirir

---

## 🏗️ Mimari ve Teknoloji Yığını

### Backend (Python/Flask)
- **Framework**: Flask 2.0+ (RESTful API)
- **Veritabanları**:
  - **Microsoft SQL Server**: Kullanıcı hesapları, hastalık master verisi
  - **MongoDB**: Soy ağaçları, birey dokümanları (NoSQL)
- **Bağlantı Kütüphaneleri**:
  - `pyodbc` – SQL Server bağlantısı
  - `pymongo` – MongoDB bağlantısı
- **Güvenlik**: `bcrypt` – Şifre hashleme
- **AI Entegrasyonu**: `google-generativeai` – Gemini API

### Frontend (Next.js/React)
- **Framework**: Next.js 16.0.7 (App Router)
- **UI Kütüphaneleri**:
  - React 19.2.0
  - Bootstrap 5.3.8
  - Tailwind CSS 4
- **Dil**: TypeScript 5
- **Linter/Formatter**: Biome 2.2.0

### Özellikler
- 🎨 Modern, responsive UI tasarımı
- 🔄 Next.js API Routes ile Flask backend'e proxy
- 📱 Mobil uyumlu arayüz
- ⚡ Hızlı ve optimize edilmiş performans

---

## 📁 Proje Yapısı

```
KRAP/
├── app.py                    # 🚀 Flask API Backend - Ana uygulama dosyası
├── config.py                 # ⚙️ Veritabanı ve uygulama konfigürasyonu
├── database.py               # 🗄️ Hibrit veritabanı bağlantıları (SQL + MongoDB)
├── validators.py             # ✅ Girdi doğrulama ve iş kuralları
├── routes.py                 # 🌐 Ek API route'ları (kayıt, test vb.)
├── soy_agaci_ureteci.py      # 🌳 Soy ağacı üretim algoritması
│
├── services/                 # 🧠 İş mantığı ve servisler
│   ├── registration_service.py  # Kayıt işlemleri (Yeni aile / Mevcut aileye katıl)
│   ├── gemini_service.py         # Google Gemini AI entegrasyonu
│   └── tree_cleanup.py          # Yardımcı temizlik fonksiyonları
│
├── genetics/                 # 🔬 Mendel genetiği hesaplamaları
│   ├── constants.py          # İsim listeleri, sabitler, genetik parametreler
│   ├── genetics.py           # Alel frekansları, genotip üretimi, X-bağlı/çekinik kurallar
│   ├── person.py             # Kişi (birey) nesnesi oluşturma
│   ├── family_tree.py        # Soy ağacı üzerinde gen aktarımı (ata → çocuk)
│   ├── risk_analysis.py      # Kullanıcı bazlı kalıtsal risk analizi
│   └── carrier_guarantee.py  # Taşıyıcı garantisi algoritması
│
├── frontend/                 # ⚛️ Next.js Frontend Uygulaması
│   ├── app/                  # Next.js App Router
│   │   ├── page.tsx          # Ana giriş sayfası (Login)
│   │   ├── kayit-ol/         # Kayıt sayfası
│   │   │   └── page.tsx
│   │   ├── profil/           # Profil sayfası (Soy ağacı + Risk analizi)
│   │   │   └── page.tsx
│   │   ├── api/              # Next.js API route'ları (Flask'a proxy)
│   │   │   ├── login/route.ts
│   │   │   ├── register/route.ts
│   │   │   ├── profil/route.ts
│   │   │   ├── family-tree/route.ts
│   │   │   └── hastalik-bilgileri/route.ts
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css        # Global CSS stilleri
│   ├── package.json          # Node.js bağımlılıkları
│   ├── next.config.ts        # Next.js yapılandırması (API proxy)
│   ├── tsconfig.json         # TypeScript yapılandırması
│   └── biome.json            # Biome linter/formatter ayarları
│
└── requirements.txt          # Python bağımlılıkları
```

---

## 🌟 Temel Özellikler ve Senaryolar

### 1️⃣ Senaryo 1 – Yeni Aile Evreni Başlatma

Kullanıcı, kendine ait **kurgusal TC**, doğum tarihi, cinsiyet vb. bilgilerle kayıt olur. Sistem:

1. Kullanıcının **yaşına göre kuşak konumunu** belirler (ör. 3. kuşak = ebeveyn)
2. **Geriye doğru** ata kuşakları üretir:
   - Anne, baba
   - Büyükanne, büyükbaba
   - Büyük büyükanne/büyükbaba (5-6 kuşak geriye)
3. **İleriye doğru** çocuk ve torun kuşakları simüle eder
4. Her birey için **genotip** ve buna bağlı **hastalık durumu** (Sağlıklı / Taşıyıcı / Hasta) üretir
5. Tüm soy ağacı hibrit veritabanı modelinde saklanır:
   - **SQL Server** → Kullanıcı hesapları (`Users` tablosu)
   - **MongoDB** → Aile ağaçları (`FamilyTrees.agac_verisi` dokümanı)

### 2️⃣ Senaryo 2 – Mevcut Aileye Katılma (Join Family)

Kullanıcı, kayıt olurken:
- **Ebeveyn Kurgusal TC** (ebeveyninin kurgusal TC'si)
- **Kendi Kurgusal TC** (ağaçta kendisine atanmış kurgusal TC)

bilgilerini girer. İş akışı:

1. SQL tarafında ebeveyn kullanıcısı bulunur (`FamilyTreeID_Mongo`, `BireyID_Mongo`)
2. MongoDB'de aynı `FamilyTreeID_Mongo` ile aile ağacı çekilir
3. `kurgusal_tc == kendi_tc` olan birey, **ağaç içinde** bulunur
4. Ebeveyn ile çocuk arasında **soy bağı doğrulanır** (`anne_id == parent_uuid` veya `baba_id == parent_uuid`)
5. Bu birey için daha önce kullanıcı hesabı açılmış mı kontrol edilir
6. Her şey yolundaysa, yeni kullanıcı SQL'de bu bireye bağlanır

Bu sayede **aynı aile evreni içinde** birden fazla kullanıcı, farklı bireylere karşılık gelerek sistemi birlikte kullanabilir.

### 3️⃣ Risk Analizi ve AI Destekli Bilgilendirme

- **Mendel Genetiği Hesaplamaları**: Alel frekansları, genotip-fenotip dönüşümü
- **Kalıtsal Risk Analizi**: Kullanıcının önceki kuşaklardan hastalık geçiş olasılıkları
- **Google Gemini AI Entegrasyonu**: Her hastalık için dinamik, kişiselleştirilmiş bilgilendirme
- **Görsel Soy Ağacı**: Geçmiş kuşaklar ve gelecek simülasyonu (çocuklar) görselleştirme

---

## 🚀 Kurulum ve Çalıştırma

### Ön Gereksinimler

- **Python 3.x** (3.8+ önerilir)
- **Node.js 18+** ve npm
- **Microsoft SQL Server** (Express Edition yeterli)
- **MongoDB** (Local veya MongoDB Atlas)
- **ODBC Driver** (SQL Server için, Windows'ta genelde hazır gelir)

### 1. Depoyu Klonla

```bash
git clone https://github.com/<kullanici>/KRAP.git
cd KRAP
```

### 2. Backend Kurulumu

#### Python Sanal Ortamı Oluştur

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### Python Bağımlılıklarını Yükle

```bash
pip install -r requirements.txt
```

Başlıca paketler:
- Flask>=2.0.0
- flask-cors>=4.0.0
- pyodbc>=4.0.0
- pymongo>=4.0.0
- bcrypt>=4.0.0
- google-generativeai>=0.3.0

#### Veritabanı Konfigürasyonu

`config.py` dosyasında aşağıdaki alanları güncelleyin:

```python
# MongoDB Bağlantı Ayarları
MONGO_CONNECTION_STRING = 'mongodb://localhost:27017/'  # veya MongoDB Atlas connection string
MONGO_DATABASE_NAME = 'KRAP_NoSQL_DB'

# MS SQL Server Ayarları
SQL_SERVER_SUNUCU_ADI = 'localhost\\SQLEXPRESS'  # Kendi sunucu adınız
SQL_SERVER_VERITABANI_ADI = 'KRAP'  # Veritabanı adı
```

#### SQL Server Veritabanı Hazırlığı

1. `KRAP` adında bir veritabanı oluşturun
2. En azından aşağıdaki tablolar gereklidir:
   - `Users` (Email, PasswordHash, KurgusalTC, DogumTarihi, Isim, Soyad, FamilyTreeID_Mongo, BireyID_Mongo, ...)
   - `Hastaliklar` (HastalikAdi, GorulmeOrani, KalitimSekli, ...)

#### MongoDB Hazırlığı

- Local MongoDB kullanıyorsanız, MongoDB servisinin çalıştığından emin olun
- MongoDB Atlas kullanıyorsanız, connection string'i `config.py`'de güncelleyin
- `FamilyTrees` koleksiyonu otomatik oluşturulacaktır

### 3. Frontend Kurulumu

```bash
cd frontend
npm install
```

### 4. Uygulamayı Çalıştırma

#### Backend (Flask) - Terminal 1

```bash
# Proje kök dizininde
python app.py
```

Flask uygulaması varsayılan olarak şu adreste çalışır:
```
http://localhost:5000
```

#### Frontend (Next.js) - Terminal 2

```bash
# frontend/ dizininde
npm run dev
```

Next.js frontend uygulaması şu adreste çalışır:
```
http://localhost:3000
```

**Not:** Frontend, Next.js API Routes üzerinden Flask backend'e proxy yapar. Her iki sunucunun da çalışıyor olması gerekir.

---

## 📖 Kullanım

### Giriş Yapma

1. `http://localhost:3000` adresine gidin
2. Kurgusal TC kimlik numaranız ve şifrenizle giriş yapın

### Yeni Kayıt

1. "Yeni Hesap Oluştur" butonuna tıklayın
2. Kişisel bilgilerinizi girin (İsim, Soyad, Cinsiyet, Doğum Tarihi, TC)
3. Hesap bilgilerinizi girin (E-posta, Şifre)
4. **Ebeveyn TC** alanını boş bırakırsanız → **Senaryo 1** (Yeni aile evreni)
5. **Ebeveyn TC** alanını doldurursanız → **Senaryo 2** (Mevcut aileye katılma)

### Profil ve Risk Analizi

- **Profil Sekmesi**: Kişisel bilgileriniz ve AI destekli risk analizi
- **Soy Ağacı Sekmesi**: 
  - **Atalarım**: Geçmiş kuşaklar görselleştirmesi
  - **Çocuklarım**: Gelecek simülasyonu (olasılıksal)

---

## 🔬 Genetik Hesaplama Detayları

### Mendel Kalıtım Kuralları

Platform şu kalıtım şekillerini destekler:

1. **Çekinik (Autosomal Recessive)**
   - Genotip: NN (Normal), NT (Taşıyıcı), TT (Hasta)
   - Fenotip: TT → Hasta, NT → Taşıyıcı, NN → Sağlıklı

2. **X-Bağlı Çekinik (X-Linked Recessive)**
   - Erkek: XnY (Sağlıklı), XtY (Hasta)
   - Kadın: XnXn (Sağlıklı), XnXt (Taşıyıcı), XtXt (Hasta)

### Alel Frekansı Hesaplama

- **Çekinik**: `q = √(görülme oranı)`, `p = 1 - q`
- **X-Bağlı**: `q = görülme oranı`, `p = 1 - q`

### Risk Analizi

- Kullanıcının ebeveynlerinden ve önceki kuşaklardan hastalık geçiş olasılıkları hesaplanır
- Her hastalık için **risk seviyesi** (Düşük, Orta, Yüksek, Çok Yüksek) belirlenir
- **Taşıyıcı olabilirlik** yüzdesi hesaplanır

---

## 🤝 Katkıda Bulunma

Öneri, hata bildirimi veya katkı göndermek isterseniz:

- Issue açabilirsiniz
- Pull Request gönderebilirsiniz
- Kod içinde `TODO` / `DEBUG` notlarını takip ederek eksik alanları iyileştirebilirsiniz

KRAP halen **araştırma ve prototip** niteliğinde bir projedir; özellikle genetik modelleme ve risk analizi katmanında yapılacak katkılar, gerçekçi simülasyon kalitesini önemli ölçüde artıracaktır. 🙌

---

## 📝 Lisans

Bu proje araştırma ve eğitim amaçlıdır. Gerçek tıbbi kararlar için kullanılmamalıdır.

---

## 🔗 İletişim ve Destek

Sorularınız veya önerileriniz için GitHub Issues kullanabilirsiniz.
