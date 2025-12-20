# Kendi AI Modelinizi Entegre Etme Kılavuzu

Gemini API kaldırıldı ve yerine kendi yapay zeka modelinizi kullanabilirsiniz.

## 📁 Dosya Yapısı

- `services/local_ai_service.py` - Kendi modelinizi entegre edeceğiniz dosya
- `app.py` - Model çağrıları burada yapılıyor (değiştirilmesi gerekmez)

## 🔧 Model Entegrasyonu

### 1. Model Yükleme

`services/local_ai_service.py` dosyasındaki `load_model()` fonksiyonunu düzenleyin:

#### Örnek 1: Hugging Face Transformers Modeli
```python
def load_model():
    global MODEL, TOKENIZER, MODEL_LOADED
    
    if MODEL_LOADED:
        return True
    
    try:
        print(">>> Model yükleniyor...", file=sys.stderr)
        
        # Kendi modelinizi yükleyin
        TOKENIZER = AutoTokenizer.from_pretrained('path/to/your/model')
        MODEL = AutoModelForCausalLM.from_pretrained('path/to/your/model')
        MODEL.eval()
        
        MODEL_LOADED = True
        return True
    except Exception as e:
        print(f"!!! Model yükleme hatası: {e}", file=sys.stderr)
        return False
```

#### Örnek 2: PyTorch Modeli
```python
def load_model():
    global MODEL, MODEL_LOADED
    
    if MODEL_LOADED:
        return True
    
    try:
        MODEL = torch.load('path/to/your/model.pth', map_location='cpu')
        MODEL.eval()
        MODEL_LOADED = True
        return True
    except Exception as e:
        print(f"!!! Model yükleme hatası: {e}", file=sys.stderr)
        return False
```

#### Örnek 3: TensorFlow/Keras Modeli
```python
def load_model():
    global MODEL, MODEL_LOADED
    
    if MODEL_LOADED:
        return True
    
    try:
        import tensorflow as tf
        MODEL = tf.keras.models.load_model('path/to/your/model.h5')
        MODEL_LOADED = True
        return True
    except Exception as e:
        print(f"!!! Model yükleme hatası: {e}", file=sys.stderr)
        return False
```

### 2. Tahmin Fonksiyonu

`generate_risk_explanation()` fonksiyonunu kendi modelinize göre düzenleyin:

```python
def generate_risk_explanation(hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik, aciklama):
    # Kendi modelinizle tahmin yapın
    prompt = f"""Hastalık: {hastalik_adi}
Kalıtım Şekli: {kalitim_sekli}
Durum: {durum}
Risk Seviyesi: {risk_seviyesi}
Taşıyıcı Olma Olasılığı: %{tasiyici_olabilirlik}"""
    
    # Modelinize göre tahmin yapın
    prediction = YOUR_MODEL.predict(prompt)
    
    return prediction
```

## 📦 Gerekli Kütüphaneler

Model tipinize göre `requirements.txt` dosyasına ekleyin:

```bash
# Transformers için
transformers>=4.30.0
torch>=2.0.0

# TensorFlow için
tensorflow>=2.13.0

# Diğer
numpy>=1.24.0
pandas>=2.0.0
```

## 🚀 Kullanım

Model entegre edildikten sonra, sistem otomatik olarak:
1. Risk analizi yapılır (`genetics/risk_analysis.py`)
2. Risk sonuçları kendi modelinize gönderilir
3. Model açıklama metni üretir
4. Frontend'e gönderilir

## ⚙️ Ortam Değişkenleri

Model yolunu ortam değişkeni ile belirtebilirsiniz:

```bash
export LOCAL_AI_MODEL_PATH=/path/to/your/model
```

## 🔍 Test

Modelinizi test etmek için:

```python
from services.local_ai_service import get_disease_information

result = get_disease_information(
    hastalik_adi="Akdeniz Anemisi",
    kalitim_sekli="Çekinik",
    durum="Taşıyıcı",
    risk_seviyesi="Yüksek",
    tasiyici_olabilirlik=75,
    aciklama="Test açıklaması"
)

print(result['bilgi_icerigi'])
```

## 📝 Notlar

- Model yüklenemezse, sistem otomatik olarak template-based açıklama kullanır
- Cache mekanizması aktif (aynı parametreler için tekrar hesaplama yapılmaz)
- Model yükleme sadece bir kez yapılır (singleton pattern)

