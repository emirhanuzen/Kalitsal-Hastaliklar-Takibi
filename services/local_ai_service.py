# services/local_ai_service.py
# Kendi yapay zeka modelimiz - Risk analizi sonuçları için açıklama üretimi

import sys
import os

# Opsiyonel import'lar - Kendi modelinize göre açın
try:
    import joblib
except ImportError:
    joblib = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForCausalLM = None

# Model yolu - Kendi modelinizi buraya koyun
MODEL_PATH = os.getenv('LOCAL_AI_MODEL_PATH', 'models/risk_analysis_model')
MODEL_LOADED = False
MODEL = None
TOKENIZER = None

# Cache için basit bir sözlük
_disease_cache = {}
_risk_analysis_cache = {}

# Hastalık-Bölüm Mapping'i
# Her hastalık için uygun hastane bölümü
HASTALIK_BOLUM_MAPPING = {
    # Autosomal Recessive Hastalıklar
    'Akdeniz Anemisi': 'Hematoloji Bölümü',
    'Kistik Fibrozis': 'Göğüs Hastalıkları Bölümü',
    'SMA': 'Nöroloji Bölümü',
    'Orak Hücreli Anemi': 'Hematoloji Bölümü',
    'Fenilketonüri (PKU)': 'Metabolizma ve Endokrinoloji Bölümü',
    'Tay-Sachs': 'Nöroloji Bölümü',
    'Albinizm': 'Dermatoloji Bölümü',
    'Galaktozemi': 'Metabolizma ve Endokrinoloji Bölümü',
    'Wilson Hastalığı': 'Gastroenteroloji Bölümü',
    'Ailevi Akdeniz Ateşi': 'İç Hastalıkları (Romatoloji) Bölümü',
    
    # X-Linked Recessive Hastalıklar
    'Hemofili A': 'Hematoloji Bölümü',
    'Hemofili B': 'Hematoloji Bölümü',
    'Renk Körlüğü': 'Göz Hastalıkları Bölümü',
    'Duchenne MD': 'Nöroloji Bölümü',
    'G6PD Eksikliği': 'Hematoloji Bölümü',
    
    # Autosomal Dominant Hastalıklar
    'Huntington': 'Nöroloji Bölümü',
    'Marfan Sendromu': 'Kardiyoloji Bölümü',
    'Akondroplazi': 'Ortopedi ve Travmatoloji Bölümü',
    'Polikistik Böbrek': 'Nefroloji Bölümü',
    'Nörofibromatozis': 'Nöroloji Bölümü'
}


def get_recommended_department(hastalik_adi):
    """
    Hastalık adına göre önerilen hastane bölümünü döndürür.
    
    Args:
        hastalik_adi: Hastalık adı
    
    Returns:
        str: Önerilen hastane bölümü (varsayılan: 'Tıbbi Genetik Bölümü')
    """
    result = HASTALIK_BOLUM_MAPPING.get(hastalik_adi, 'Tıbbi Genetik Bölümü')
    if result == 'Tıbbi Genetik Bölümü':
        print(f">>> DEBUG (get_recommended_department): '{hastalik_adi}' mapping'de bulunamadı, varsayılan kullanılıyor. Mevcut key'ler: {list(HASTALIK_BOLUM_MAPPING.keys())[:5]}...", file=sys.stderr)
    return result


def load_model():
    """
    Kendi yapay zeka modelinizi yükler.
    Bu fonksiyonu kendi model yapınıza göre düzenleyin.
    """
    global MODEL, TOKENIZER, MODEL_LOADED
    
    if MODEL_LOADED:
        return True
    
    try:
        print(">>> Model yükleniyor...", file=sys.stderr)
        
        # KENDİ MODELİNİZİ BURAYA YÜKLEYİN
        # Model dosyası yoksa template kullanılacak
        
        # ÖRNEK 1: Transformers modeli (GPT, BERT, vb.) - Model dosyanız varsa açın
        # if os.path.exists(MODEL_PATH):
        #     TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH)
        #     MODEL = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
        #     MODEL.eval()
        #     MODEL_LOADED = True
        #     print(">>> Transformers modeli başarıyla yüklendi!", file=sys.stderr)
        #     return True
        
        # ÖRNEK 2: Joblib ile kaydedilmiş model - Model dosyanız varsa açın
        # if os.path.exists(MODEL_PATH + '.pkl'):
        #     MODEL = joblib.load(MODEL_PATH + '.pkl')
        #     MODEL_LOADED = True
        #     print(">>> Joblib modeli başarıyla yüklendi!", file=sys.stderr)
        #     return True
        
        # ÖRNEK 3: PyTorch modeli - Model dosyanız varsa açın
        # if os.path.exists(MODEL_PATH + '.pth'):
        #     MODEL = torch.load(MODEL_PATH + '.pth', map_location='cpu')
        #     MODEL.eval()
        #     MODEL_LOADED = True
        #     print(">>> PyTorch modeli başarıyla yüklendi!", file=sys.stderr)
        #     return True
        
        # ÖRNEK 4: TensorFlow/Keras modeli - Model dosyanız varsa açın
        # if os.path.exists(MODEL_PATH + '.h5'):
        #     import tensorflow as tf
        #     MODEL = tf.keras.models.load_model(MODEL_PATH + '.h5')
        #     MODEL_LOADED = True
        #     print(">>> TensorFlow modeli başarıyla yüklendi!", file=sys.stderr)
        #     return True
        
        # Model dosyası bulunamadı - Template kullanılacak
        print(">>> Model dosyası bulunamadı. Template-based açıklama kullanılacak.", file=sys.stderr)
        MODEL_LOADED = False  # Model yüklenmedi, template kullan
        return False
        
    except Exception as e:
        print(f"!!! Model yükleme hatası: {e}", file=sys.stderr)
        print(">>> Varsayılan template kullanılacak.", file=sys.stderr)
        MODEL_LOADED = False
        return False


def generate_risk_explanation(hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik, aciklama):
    """
    Kendi yapay zeka modelinizle risk analizi açıklaması üretir.
    
    Args:
        hastalik_adi: Hastalık adı
        kalitim_sekli: Kalıtım şekli (Çekinik, X-Bağlı Çekinik, vb.)
        durum: Kullanıcının durumu (Hasta, Taşıyıcı, Yüksek Risk, vb.)
        risk_seviyesi: Risk seviyesi (Düşük, Orta, Yüksek, Çok Yüksek)
        tasiyici_olabilirlik: Taşıyıcı olma olasılığı (0-100)
        aciklama: Mevcut açıklama metni
    
    Returns:
        str: Model tarafından üretilen açıklama metni
    """
    global MODEL, TOKENIZER
    
    # Cache kontrolü
    cache_key = f"{hastalik_adi}_{kalitim_sekli}_{durum}_{risk_seviyesi}"
    if cache_key in _disease_cache:
        print(f">>> DEBUG: Cache'den döndürülüyor: {hastalik_adi}", file=sys.stderr)
        return _disease_cache[cache_key]
    
    try:
        # Model yüklü mü kontrol et
        if not MODEL_LOADED:
            load_model()
        
        # Eğer model yüklüyse, kendi modelinizle tahmin yapın
        if MODEL is not None and TOKENIZER is not None and torch is not None:
            print(f">>> Model ile açıklama üretiliyor: {hastalik_adi}", file=sys.stderr)
            
            # KENDİ MODELİNİZLE AÇIKLAMA ÜRETME KODU
            # Model tipinize göre aşağıdaki kodları düzenleyin
            
            # ÖRNEK 1: Transformers modeli ile text generation
            prompt = f"""Hastalık: {hastalik_adi}
Kalıtım Şekli: {kalitim_sekli}
Durum: {durum}
Risk Seviyesi: {risk_seviyesi}
Taşıyıcı Olma Olasılığı: %{tasiyici_olabilirlik}

Bu hastalık hakkında kısa ve anlaşılır bir açıklama yaz:"""
            
            # Tokenize
            inputs = TOKENIZER.encode(prompt, return_tensors='pt', max_length=512, truncation=True)
            
            # Generate
            with torch.no_grad():
                outputs = MODEL.generate(
                    inputs,
                    max_length=150,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=TOKENIZER.eos_token_id
                )
            
            # Decode
            generated_text = TOKENIZER.decode(outputs[0], skip_special_tokens=True)
            
            # Sadece yeni üretilen kısmı al
            explanation = generated_text[len(prompt):].strip()
            
            # Cache'e kaydet
            _disease_cache[cache_key] = explanation
            print(f">>> Model açıklama üretti: {explanation[:50]}...", file=sys.stderr)
            return explanation
            
            # ÖRNEK 2: Joblib modeli ile tahmin (model tipinize göre düzenleyin)
            # prediction = MODEL.predict([hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik])
            # explanation = str(prediction[0])
            # _disease_cache[cache_key] = explanation
            # return explanation
            
            # ÖRNEK 3: PyTorch modeli ile tahmin (model tipinize göre düzenleyin)
            # inputs = torch.tensor([...])  # Modelinize göre input hazırlayın
            # with torch.no_grad():
            #     outputs = MODEL(inputs)
            # explanation = process_output(outputs)  # Modelinize göre output işleyin
            # _disease_cache[cache_key] = explanation
            # return explanation
        
        # Model yoksa, akıllı template kullan
        else:
            return generate_template_explanation(hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik, aciklama)
            
    except Exception as e:
        print(f"!!! Model tahmin hatası: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        # Hata durumunda template kullan
        return generate_template_explanation(hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik, aciklama)


def generate_template_explanation(hastalik_adi, kalitim_sekli, durum, risk_seviyesi, tasiyici_olabilirlik, aciklama):
    """
    Model yoksa veya hata varsa, akıllı template ile açıklama üretir.
    Bu fonksiyon geçici bir çözümdür - kendi modeliniz hazır olunca kaldırılabilir.
    """
    
    # Risk seviyesine göre detaylı mesaj
    risk_seviyesi_str = str(risk_seviyesi) if risk_seviyesi else 'Orta'
    if 'Yüksek' in risk_seviyesi_str or 'Yuksek' in risk_seviyesi_str:
        ton = "önemli bir risk"
        tavsiye_detay = "Mutlaka bir genetik danışmana başvurmanız önerilir. Bu hastalık için genetik test yaptırmanız ve aile planlaması konusunda uzman görüşü almanız kritik öneme sahiptir."
        onlem = "Düzenli sağlık kontrolleri yaptırmalı ve gerekli durumlarda erken müdahale için hazırlıklı olmalısınız."
    elif 'Orta' in risk_seviyesi_str:
        ton = "orta düzeyde bir risk"
        tavsiye_detay = "Genetik danışmanlık almanız faydalı olabilir. Bu hastalık hakkında daha detaylı bilgi edinmek ve aile planlaması konusunda bilinçli kararlar vermek için bir genetik uzmanına danışmanız önerilir."
        onlem = "Düzenli takip ve gerekli durumlarda genetik test yaptırmanız önemlidir."
    else:
        ton = "düşük bir risk"
        tavsiye_detay = "Düzenli takip yeterli olabilir. Ancak aile geçmişinizde bu hastalık varsa, yine de bir genetik danışmana danışmanız faydalı olabilir."
        onlem = "Genel sağlık kontrollerinizi aksatmayın ve aile planlaması yaparken bu bilgiyi göz önünde bulundurun."
    
    # Kalıtım şekline göre detaylı açıklama
    kalitim_aciklama = ""
    kalitim_detay = ""
    if kalitim_sekli == "Çekinik" or kalitim_sekli == "Cekinik":
        kalitim_aciklama = "otozomal çekinik"
        kalitim_detay = "Bu kalıtım şeklinde, hastalık geni hem anne hem babadan geçtiğinde hastalık ortaya çıkar. Taşıyıcı bireyler genellikle sağlıklı görünür ancak geni çocuklarına aktarabilirler."
    elif kalitim_sekli == "X-Bağlı Çekinik" or kalitim_sekli == "X-Bagli Cekinik" or "X" in kalitim_sekli.upper():
        kalitim_aciklama = "X kromozomuna bağlı çekinik"
        kalitim_detay = "Bu kalıtım şeklinde, hastalık X kromozomunda taşınır. Erkeklerde tek bir X kromozomu olduğu için daha sık görülür, kadınlarda ise genellikle taşıyıcılık şeklinde seyreder."
    else:
        kalitim_aciklama = kalitim_sekli.lower()
        kalitim_detay = "Bu kalıtım şekliyle ilgili detaylı bilgi için bir genetik uzmanına danışmanız önerilir."
    
    # Taşıyıcı olasılığına göre detaylı mesaj
    if tasiyici_olabilirlik >= 75:
        tasiyici_detay = f"%{tasiyici_olabilirlik} gibi yüksek bir olasılıkla taşıyıcısınız. Bu durum, çocuklarınıza bu geni aktarma ihtimalinizin yüksek olduğu anlamına gelir."
    elif tasiyici_olabilirlik >= 50:
        tasiyici_detay = f"%{tasiyici_olabilirlik} olasılıkla taşıyıcı olabilirsiniz. Bu durumda, çocuklarınıza geni aktarma ihtimaliniz orta düzeydedir."
    elif tasiyici_olabilirlik >= 25:
        tasiyici_detay = f"%{tasiyici_olabilirlik} olasılıkla taşıyıcı olabilirsiniz. Bu düşük bir risk olmakla birlikte, yine de dikkatli olmanız önerilir."
    else:
        tasiyici_detay = f"Taşıyıcı olma riskiniz %{tasiyici_olabilirlik} gibi düşük bir seviyededir. Ancak aile geçmişinizde bu hastalık varsa, yine de genetik test yaptırmanız faydalı olabilir."
    
    # Detaylı final açıklama
    explanation = f"{hastalik_adi}, {kalitim_aciklama} kalıtım şekliyle geçen bir genetik hastalıktır. "
    explanation += f"{kalitim_detay} "
    explanation += f"Sizin için {ton} tespit edilmiştir. "
    explanation += f"{tasiyici_detay} "
    explanation += f"{tavsiye_detay} "
    explanation += f"{onlem}"
    
    # Cache'e kaydet
    cache_key = f"{hastalik_adi}_{kalitim_sekli}_{durum}_{risk_seviyesi}"
    _disease_cache[cache_key] = explanation
    
    return explanation


def get_disease_information(hastalik_adi, kalitim_sekli, durum="Taşıyıcı", risk_seviyesi=None, tasiyici_olabilirlik=None, aciklama=None):
    """
    Gemini API yerine kendi modelimizi kullanarak hastalık bilgisi üretir.
    Aynı interface'i koruyoruz ki app.py'de değişiklik minimal olsun.
    
    Args:
        hastalik_adi: Hastalık adı
        kalitim_sekli: Kalıtım şekli (Çekinik, X-Bağlı Çekinik, vb.)
        durum: Kullanıcının durumu (Hasta, Taşıyıcı, Yüksek Risk, vb.)
        risk_seviyesi: Risk seviyesi (opsiyonel)
        tasiyici_olabilirlik: Taşıyıcı olma olasılığı (opsiyonel)
        aciklama: Mevcut açıklama (opsiyonel)
    
    Returns:
        dict: Hastalık bilgileri içeren sözlük (Gemini formatıyla uyumlu)
    """
    try:
        # Risk bilgileri varsa kullan, yoksa varsayılan değerler
        risk_seviyesi = risk_seviyesi or 'Orta'
        tasiyici_olabilirlik = tasiyici_olabilirlik or 50
        aciklama = aciklama or f"{hastalik_adi} hakkında risk analizi yapıldı."
        
        # Kendi modelimizle açıklama üret
        bilgi_icerigi = generate_risk_explanation(
            hastalik_adi,
            kalitim_sekli,
            durum,
            risk_seviyesi,
            tasiyici_olabilirlik,
            aciklama
        )
        
        # Önerilen bölümü belirle
        onerilen_bolum = get_recommended_department(hastalik_adi)
        
        result = {
            "hastalik_adi": hastalik_adi,
            "kalitim_sekli": kalitim_sekli,
            "durum": durum,
            "bilgi_icerigi": bilgi_icerigi,
            "onerilen_bolum": onerilen_bolum,
            "basarili": True
        }
        
        return result
        
    except Exception as e:
        print(f"!!! Local AI model hatası: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        # Hata durumunda varsayılan mesaj
        onerilen_bolum = get_recommended_department(hastalik_adi)
        return {
            "hastalik_adi": hastalik_adi,
            "kalitim_sekli": kalitim_sekli,
            "durum": durum,
            "bilgi_icerigi": f"{hastalik_adi} hakkında risk analizi yapıldı. Detaylı bilgi için bir genetik danışmana başvurmanız önerilir.",
            "onerilen_bolum": onerilen_bolum,
            "basarili": False
        }


def get_multiple_diseases_info(hastalik_listesi):
    """
    Birden fazla hastalık için bilgi üretir.
    Gemini API formatıyla uyumlu.
    
    Args:
        hastalik_listesi: [{"hastalik": "Hastalık Adı", "durum": "Hasta/Taşıyıcı", "kalitim_sekli": "Çekinik/X-Bağlı Çekinik", ...}, ...]
    
    Returns:
        list: Hastalık bilgileri listesi
    """
    hastalik_bilgileri = []
    
    for hastalik in hastalik_listesi:
        hastalik_adi = hastalik.get("hastalik", "")
        durum = hastalik.get("durum", "Taşıyıcı")
        kalitim_sekli = hastalik.get("kalitim_sekli", "Çekinik")
        risk_seviyesi = hastalik.get("risk_seviyesi")
        tasiyici_olabilirlik = hastalik.get("tasiyici_olabilirlik")
        aciklama = hastalik.get("aciklama")
        
        if hastalik_adi:
            bilgi = get_disease_information(
                hastalik_adi,
                kalitim_sekli,
                durum,
                risk_seviyesi,
                tasiyici_olabilirlik,
                aciklama
            )
            hastalik_bilgileri.append(bilgi)
    
    return hastalik_bilgileri


def calculate_risk_analysis_with_model(soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari):
    """
    Model ile risk analizi yapar.
    
    Args:
        soy_agaci_listesi: Tüm soy ağacı bireyleri listesi
        kullanici_birey_id: Kullanıcının birey ID'si
        kullanici_cinsiyet: Kullanıcının cinsiyeti
        hastalik_detaylari: Hastalık detayları sözlüğü
    
    Returns:
        risk_analizi: Her hastalık için risk bilgileri içeren liste
    """
    global MODEL, TOKENIZER, MODEL_LOADED
    
    # Cache kontrolü
    cache_key = f"risk_{kullanici_birey_id}_{kullanici_cinsiyet}"
    if cache_key in _risk_analysis_cache:
        print(f">>> DEBUG: Risk analizi cache'den döndürülüyor", file=sys.stderr)
        return _risk_analysis_cache[cache_key]
    
    # Bireyleri ID'ye göre indeksle
    birey_map = {}
    for birey in soy_agaci_listesi:
        birey_id = str(birey.get("birey_id", ""))
        birey_map[birey_id] = birey
    
    # Kullanıcıyı bul
    kullanici_birey_id_str = str(kullanici_birey_id)
    kullanici_birey = birey_map.get(kullanici_birey_id_str)
    if not kullanici_birey:
        print(f"!!! UYARI: Kullanıcı bireyi bulunamadı. ID: {kullanici_birey_id_str}", file=sys.stderr)
        return []
    
    # Ebeveynleri bul
    anne_id = str(kullanici_birey.get("anne_id", "")) if kullanici_birey.get("anne_id") else None
    baba_id = str(kullanici_birey.get("baba_id", "")) if kullanici_birey.get("baba_id") else None
    anne = birey_map.get(anne_id) if anne_id else None
    baba = birey_map.get(baba_id) if baba_id else None
    
    # Model yüklü mü kontrol et
    if not MODEL_LOADED:
        load_model()
    
    risk_analizi = []
    
    # Her hastalık için model ile risk analizi yap
    for hastalik_adi, details in hastalik_detaylari.items():
        sekil = details['sekil']
        oran = details.get('oran', 0)
        
        # Ebeveyn durumlarını topla
        anne_durumu = None
        baba_durumu = None
        anne_ismi = None
        baba_ismi = None
        
        if anne:
            anne_ismi = f"{anne.get('isim', 'Bilinmeyen')} {anne.get('soyad', '')}".strip()
            anne_hastaliklar = anne.get("hastaliklar", "Sağlıklı")
            if anne_hastaliklar != "Sağlıklı" and isinstance(anne_hastaliklar, list):
                for h in anne_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        anne_durumu = h.get("durum")
                        break
        
        if baba:
            baba_ismi = f"{baba.get('isim', 'Bilinmeyen')} {baba.get('soyad', '')}".strip()
            baba_hastaliklar = baba.get("hastaliklar", "Sağlıklı")
            if baba_hastaliklar != "Sağlıklı" and isinstance(baba_hastaliklar, list):
                for h in baba_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        baba_durumu = h.get("durum")
                        break
        
        # Model ile risk analizi yap
        try:
            if MODEL is not None and MODEL_LOADED:
                print(f">>> Model ile risk analizi yapılıyor: {hastalik_adi}", file=sys.stderr)
                
                # Model input hazırlama
                model_input = {
                    "hastalik_adi": hastalik_adi,
                    "kalitim_sekli": sekil,
                    "kullanici_cinsiyet": kullanici_cinsiyet,
                    "anne_durumu": anne_durumu if anne_durumu else "Sağlıklı",
                    "baba_durumu": baba_durumu if baba_durumu else "Sağlıklı",
                    "oran": oran
                }
                
                # MODEL ÇAĞRISI - Kendi modelinizle değiştirebilirsiniz
                # ÖRNEK: model_output = MODEL.predict(model_input) veya MODEL(model_input)
                # Şimdilik algoritma sonuçlarını model çıktısı gibi kullanıyoruz (mekanizma testi için)
                
                # Algoritma ile hesapla (model simülasyonu için)
                from genetics.risk_analysis import calculate_user_risk_algorithmic
                algorithmic_result = calculate_user_risk_algorithmic(
                    soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari
                )
                
                # Model çıktısı gibi kullan (mekanizma testi)
                for risk in algorithmic_result:
                    if risk.get('hastalik') == hastalik_adi:
                        # Model ile yapıldığını işaretle
                        risk['model_ile_hesaplandi'] = True
                        risk_analizi.append(risk)
                        print(f">>> Model risk analizi tamamlandı: {hastalik_adi} - {risk.get('risk_seviyesi')}", file=sys.stderr)
                        break
            else:
                # Model yoksa algoritma kullan
                print(f">>> Model yüklü değil, algoritma ile risk analizi yapılıyor: {hastalik_adi}", file=sys.stderr)
                from genetics.risk_analysis import calculate_user_risk_algorithmic
                algorithmic_result = calculate_user_risk_algorithmic(
                    soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari
                )
                
                for risk in algorithmic_result:
                    if risk.get('hastalik') == hastalik_adi:
                        risk['model_ile_hesaplandi'] = False
                        risk_analizi.append(risk)
                        break
                    
        except Exception as e:
            print(f"!!! Model risk analizi hatası: {e}, algoritma fallback kullanılıyor", file=sys.stderr)
            # Hata durumunda algoritma kullan
            from genetics.risk_analysis import calculate_user_risk_algorithmic
            algorithmic_result = calculate_user_risk_algorithmic(
                soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari
            )
            for risk in algorithmic_result:
                if risk.get('hastalik') == hastalik_adi:
                    risk['model_ile_hesaplandi'] = False
                    risk_analizi.append(risk)
                    break
    
    # Model sonuç döndürmediyse, algoritma fallback kullan
    if not risk_analizi:
        print(">>> Model risk analizi sonuç döndürmedi, algoritma fallback kullanılıyor...", file=sys.stderr)
        from genetics.risk_analysis import calculate_user_risk_algorithmic
        risk_analizi = calculate_user_risk_algorithmic(
            soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari
        )
    
    # Cache'e kaydet
    _risk_analysis_cache[cache_key] = risk_analizi
    
    return risk_analizi

