# services/gemini_service.py
# Gemini API servisi - Hastalık bilgileri için dinamik içerik üretimi

import google.generativeai as genai
import sys
import time
from functools import lru_cache

# Gemini API Key
GEMINI_API_KEY = 'AIzaSyB-fR-3VN1GLl2QagKYk6fXaRMrQLaY_9w'

# Gemini API'yi yapılandır
genai.configure(api_key=GEMINI_API_KEY)

# Model: gemini-2.0-flash-exp (veya gemini-2.0-flash)
MODEL_NAME = 'gemini-2.0-flash-exp'

# Cache için basit bir sözlük (gelişmiş cache için Redis kullanılabilir)
_disease_cache = {}

# Rate limiting için son API çağrısı zamanı
_last_api_call_time = 0
_min_call_interval = 1.0  # Minimum 1 saniye bekleme


def get_disease_information(hastalik_adi, kalitim_sekli, durum="Taşıyıcı"):
    """
    Gemini API kullanarak hastalık hakkında genel bilgileri alır.
    Cache ve rate limiting ile korunur.
    
    Args:
        hastalik_adi: Hastalık adı
        kalitim_sekli: Kalıtım şekli (Çekinik, X-Bağlı Çekinik, vb.)
        durum: Kullanıcının durumu (Hasta, Taşıyıcı)
    
    Returns:
        dict: Hastalık bilgileri içeren sözlük
    """
    global _last_api_call_time
    
    # Cache kontrolü - aynı parametrelerle daha önce çağrıldıysa cache'den dön
    cache_key = f"{hastalik_adi}_{kalitim_sekli}_{durum}"
    if cache_key in _disease_cache:
        print(f">>> DEBUG: Cache'den döndürülüyor: {hastalik_adi}", file=sys.stderr)
        return _disease_cache[cache_key]
    
    try:
        # Rate limiting - minimum bekleme süresi
        current_time = time.time()
        time_since_last_call = current_time - _last_api_call_time
        if time_since_last_call < _min_call_interval:
            wait_time = _min_call_interval - time_since_last_call
            time.sleep(wait_time)
        
        # Gemini modelini oluştur
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Prompt oluştur - Kısa ve öz bilgi için
        prompt = f"""Sen bir genetik hastalık uzmanısın. Aşağıdaki kalıtsal hastalık hakkında kısa ve öz bilgi ver (maksimum 150 kelime).

Hastalık Adı: {hastalik_adi}
Kalıtım Şekli: {kalitim_sekli}
Kullanıcı Durumu: {durum}

Lütfen şu konularda kısa bilgi ver:
1. Hastalığın kısa tanımı (1-2 cümle)
2. Temel belirtiler (madde halinde, maksimum 3-4 madde)
3. {durum} durumu ne anlama gelir ve ne gibi önlemler alınmalı (kısa)
4. Kalıtım şekli hakkında özet bilgi ({kalitim_sekli})

Bilgileri Türkçe, anlaşılır ve profesyonel bir dille sun. HTML formatında:
- Başlıklar için <h6> veya <strong> kullan
- Paragraflar için <p> kullan
- Listeler için <ul> ve <li> kullan

Çok kısa ve öz tut. Maksimum 150 kelime kullan. Yanıtını JSON formatında verme, doğrudan HTML içerik olarak ver."""

        # API çağrısı yap (rate limiting ile)
        _last_api_call_time = time.time()
        response = model.generate_content(prompt)
        
        # Yanıtı al
        if response and response.text:
            bilgi_icerigi = response.text
        else:
            bilgi_icerigi = f"{hastalik_adi} hastalığı hakkında bilgi alınamadı. Lütfen daha sonra tekrar deneyin."
        
        result = {
            "hastalik_adi": hastalik_adi,
            "kalitim_sekli": kalitim_sekli,
            "durum": durum,
            "bilgi_icerigi": bilgi_icerigi,
            "basarili": True
        }
        
        # Cache'e kaydet
        _disease_cache[cache_key] = result
        return result
        
    except Exception as e:
        error_str = str(e)
        print(f"!!! Gemini API hatası: {error_str}", file=sys.stderr)
        
        # Rate limit hatası kontrolü
        if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
            # Rate limit aşıldı - kullanıcıya bilgilendirme mesajı döndür
            return {
                "hastalik_adi": hastalik_adi,
                "kalitim_sekli": kalitim_sekli,
                "durum": durum,
                "bilgi_icerigi": f"""
                    <p><strong>{hastalik_adi}</strong> hakkında bilgi alınırken API kotası limitine ulaşıldı.</p>
                    <p><strong>Kalıtım Şekli:</strong> {kalitim_sekli}</p>
                    <p><strong>Durumunuz:</strong> {durum}</p>
                    <p class="text-muted">Lütfen daha sonra tekrar deneyin veya bir genetik danışmana başvurun.</p>
                """,
                "basarili": False,
                "rate_limit_error": True
            }
        
        # Diğer hatalar için genel mesaj
        return {
            "hastalik_adi": hastalik_adi,
            "kalitim_sekli": kalitim_sekli,
            "durum": durum,
            "bilgi_icerigi": f"""
                <p><strong>{hastalik_adi}</strong> hakkında bilgi alınırken bir hata oluştu.</p>
                <p><strong>Kalıtım Şekli:</strong> {kalitim_sekli}</p>
                <p><strong>Durumunuz:</strong> {durum}</p>
                <p class="text-muted">Detaylı bilgi için bir genetik danışmana başvurmanız önerilir.</p>
            """,
            "basarili": False
        }


def get_multiple_diseases_info(hastalik_listesi):
    """
    Birden fazla hastalık için bilgi alır.
    Rate limiting ile korunur - her çağrı arasında bekleme süresi eklenir.
    
    Args:
        hastalik_listesi: [{"hastalik": "Hastalık Adı", "durum": "Hasta/Taşıyıcı", "kalitim_sekli": "Çekinik/X-Bağlı Çekinik"}, ...]
    
    Returns:
        list: Hastalık bilgileri listesi
    """
    hastalik_bilgileri = []
    
    for index, hastalik in enumerate(hastalik_listesi):
        hastalik_adi = hastalik.get("hastalik", "")
        durum = hastalik.get("durum", "Taşıyıcı")
        kalitim_sekli = hastalik.get("kalitim_sekli", "Çekinik")
        
        if hastalik_adi:
            # Rate limiting - her çağrı arasında bekleme (ilk çağrı hariç)
            if index > 0:
                time.sleep(_min_call_interval)
            
            bilgi = get_disease_information(hastalik_adi, kalitim_sekli, durum)
            hastalik_bilgileri.append(bilgi)
            
            # Eğer rate limit hatası alındıysa, diğer hastalıklar için devam etme
            if bilgi.get("rate_limit_error"):
                print(f">>> UYARI: Rate limit hatası alındı, kalan hastalıklar için varsayılan mesaj kullanılacak.", file=sys.stderr)
                # Kalan hastalıklar için varsayılan mesaj ekle
                for remaining in hastalik_listesi[index + 1:]:
                    remaining_adi = remaining.get("hastalik", "")
                    remaining_durum = remaining.get("durum", "Taşıyıcı")
                    remaining_kalitim = remaining.get("kalitim_sekli", "Çekinik")
                    hastalik_bilgileri.append({
                        "hastalik_adi": remaining_adi,
                        "kalitim_sekli": remaining_kalitim,
                        "durum": remaining_durum,
                        "bilgi_icerigi": f"""
                            <p><strong>{remaining_adi}</strong> hakkında bilgi alınamadı (API kotası limitine ulaşıldı).</p>
                            <p><strong>Kalıtım Şekli:</strong> {remaining_kalitim}</p>
                            <p><strong>Durumunuz:</strong> {remaining_durum}</p>
                            <p class="text-muted">Lütfen daha sonra tekrar deneyin veya bir genetik danışmana başvurun.</p>
                        """,
                        "basarili": False,
                        "rate_limit_error": True
                    })
                break
    
    return hastalik_bilgileri

