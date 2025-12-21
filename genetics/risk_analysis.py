# genetics/risk_analysis.py
# Kullanıcı için risk analizi fonksiyonları

import sys
import os
import pandas as pd
import joblib
from genetics.genetics import get_hastalik_detaylari, determine_phenotype
from services.local_ai_service import get_recommended_department

# Model yükleme cache'i
_model_cache = {'model': None, 'le': None, 'train_columns': None, 'loaded': False}

def _load_model():
    """Model'i yükle (cache'lenmiş)"""
    global _model_cache
    if _model_cache['loaded']:
        return _model_cache['model'], _model_cache['le'], _model_cache['train_columns']
    
    try:
        # app.py ile aynı dizinde model dosyasını bul
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(current_dir, "genetik_beyin.pkl")
        
        if os.path.exists(model_path):
            paket = joblib.load(model_path)
            _model_cache['model'] = paket["model"]
            _model_cache['le'] = paket["encoder"]
            _model_cache['train_columns'] = paket["columns"]
            _model_cache['loaded'] = True
            print(">>> DEBUG (risk_analysis): Model başarıyla yüklendi!", file=sys.stderr)
            return _model_cache['model'], _model_cache['le'], _model_cache['train_columns']
        else:
            print(f">>> DEBUG (risk_analysis): Model dosyası bulunamadı: {model_path}", file=sys.stderr)
            return None, None, None
    except Exception as e:
        print(f">>> DEBUG (risk_analysis): Model yükleme hatası: {e}", file=sys.stderr)
        return None, None, None

def _tekli_durum_cozumle(kisi_hastaliklari, aranan_hastalik):
    """Gelen listede (örn: ['Hemofili A (Taşıyıcı)']) aranan hastalık var mı?"""
    if not kisi_hastaliklari: 
        return "Sağlam"
    
    if isinstance(kisi_hastaliklari, list):
        for h in kisi_hastaliklari:
            if isinstance(h, dict):
                h_temiz = h.get("hastalik", "").split(' (')[0].strip()
                if h_temiz == aranan_hastalik:
                    durum = h.get("durum", "")
                    # Model eğitiminde "Hasta" veya "Taşıyıcı" durumları risk olarak kabul ediliyor
                    if durum in ["Hasta", "Taşıyıcı"]:
                        return "Hasta"
                    return "Sağlam"
            elif isinstance(h, str):
                h_temiz = h.split(' (')[0].strip()
                if h_temiz == aranan_hastalik:
                    return "Hasta"
    return "Sağlam"

# Hastalık bilgi bankası (app.py'dekiyle aynı olmalı)
DISEASES = {
    'Akdeniz Anemisi': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Kistik Fibrozis': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'SMA': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Orak Hücreli Anemi': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Fenilketonüri (PKU)': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Tay-Sachs': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Albinizm': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Galaktozemi': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Wilson Hastalığı': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Ailevi Akdeniz Ateşi': {'Type': 'Autosomal', 'Mode': 'Recessive'},
    'Hemofili A': {'Type': 'X-Linked', 'Mode': 'Recessive'},
    'Hemofili B': {'Type': 'X-Linked', 'Mode': 'Recessive'},
    'Renk Körlüğü': {'Type': 'X-Linked', 'Mode': 'Recessive'},
    'Duchenne MD': {'Type': 'X-Linked', 'Mode': 'Recessive'},
    'G6PD Eksikliği': {'Type': 'X-Linked', 'Mode': 'Recessive'},
    'Huntington': {'Type': 'Autosomal', 'Mode': 'Dominant'},
    'Marfan Sendromu': {'Type': 'Autosomal', 'Mode': 'Dominant'},
    'Akondroplazi': {'Type': 'Autosomal', 'Mode': 'Dominant'},
    'Polikistik Böbrek': {'Type': 'Autosomal', 'Mode': 'Dominant'},
    'Nörofibromatozis': {'Type': 'Autosomal', 'Mode': 'Dominant'}
}


def calculate_user_risk(soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet):
    """
    Algoritma ile risk analizi yapar.
    """
    return calculate_user_risk_algorithmic(soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet)


def calculate_user_risk_algorithmic(soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet, hastalik_detaylari=None):
    """
    Kullanıcının önceki kuşaklardaki bireylerden hastalık geçme olasılığını hesaplar.
    Kullanıcının kendisine doğrudan hastalık atanmaz, sadece risk analizi yapılır.
    
    Args:
        soy_agaci_listesi: Tüm soy ağacı bireyleri listesi
        kullanici_birey_id: Kullanıcının birey ID'si
        kullanici_cinsiyet: Kullanıcının cinsiyeti
    
    Returns:
        risk_analizi: Her hastalık için risk bilgileri içeren liste
    """
    # Bireyleri ID'ye göre indeksle (string karşılaştırması için)
    birey_map = {}
    for birey in soy_agaci_listesi:
        birey_id = str(birey.get("birey_id", ""))
        birey_map[birey_id] = birey
    
    # Kullanıcıyı bul (string karşılaştırması)
    kullanici_birey_id_str = str(kullanici_birey_id)
    kullanici_birey = birey_map.get(kullanici_birey_id_str)
    if not kullanici_birey:
        print(f"!!! UYARI (risk_analysis): Kullanıcı bireyi bulunamadı. ID: {kullanici_birey_id_str}", file=sys.stderr)
        print(f"!!! DEBUG: Mevcut birey ID'leri: {list(birey_map.keys())[:5]}...", file=sys.stderr)
        return []
    
    # Kullanıcının ebeveynlerini bul (string karşılaştırması)
    anne_id = str(kullanici_birey.get("anne_id", "")) if kullanici_birey.get("anne_id") else None
    baba_id = str(kullanici_birey.get("baba_id", "")) if kullanici_birey.get("baba_id") else None
    
    anne = birey_map.get(anne_id) if anne_id else None
    baba = birey_map.get(baba_id) if baba_id else None
    
    # Hastalık detaylarını al
    if hastalik_detaylari is None:
        hastalik_detaylari = get_hastalik_detaylari()
    if not hastalik_detaylari:
        print("!!! UYARI (risk_analysis): Hastalık detayları boş. calculate_allele_frequencies çağrılmış mı?", file=sys.stderr)
        return []
    
    print(f">>> DEBUG (risk_analysis): {len(hastalik_detaylari)} hastalık için risk analizi yapılacak.", file=sys.stderr)
    
    risk_analizi = []
    
    # Her hastalık için risk hesapla
    for hastalik_adi, details in hastalik_detaylari.items():
        sekil = details['sekil']
        oran = details.get('oran', 0)
        
        # Önerilen bölümü belirle
        onerilen_bolum = get_recommended_department(hastalik_adi)
        print(f">>> DEBUG (risk_analysis): Hastalık: {hastalik_adi}, Önerilen Bölüm: {onerilen_bolum}", file=sys.stderr)
        
        risk_bilgisi = {
            'hastalik': hastalik_adi,
            'kalitim_sekli': sekil,
            'risk_seviyesi': 'Düşük',
            'risk_yuzdesi': 0,
            'aciklama': '',
            'ebeveyn_durumu': {},
            'onerilen_bolum': onerilen_bolum
        }
        
        # Ebeveyn durumlarını kontrol et
        anne_durumu = None
        baba_durumu = None
        anne_ismi = None
        baba_ismi = None
        
        # Dede/Nine bilgilerini de al (model için gerekli)
        anne_dede_durumu = None
        anne_nine_durumu = None
        baba_dede_durumu = None
        baba_nine_durumu = None
        
        if anne:
            anne_ismi = f"{anne.get('isim', 'Bilinmeyen')} {anne.get('soyad', '')}".strip()
            anne_hastaliklar = anne.get("hastaliklar", "Sağlıklı")
            if anne_hastaliklar != "Sağlıklı" and isinstance(anne_hastaliklar, list):
                for h in anne_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        anne_durumu = h.get("durum")
                        break
            
            # Anne tarafı dede/nine
            anne_anne_id = str(anne.get("anne_id", "")) if anne.get("anne_id") else None
            anne_baba_id = str(anne.get("baba_id", "")) if anne.get("baba_id") else None
            
            if anne_anne_id:
                anne_nine_birey = birey_map.get(anne_anne_id)
                if anne_nine_birey:
                    nine_hastaliklar = anne_nine_birey.get("hastaliklar", "Sağlıklı")
                    if nine_hastaliklar != "Sağlıklı" and isinstance(nine_hastaliklar, list):
                        for h in nine_hastaliklar:
                            if h.get("hastalik") == hastalik_adi:
                                anne_nine_durumu = h.get("durum")
                                break
            
            if anne_baba_id:
                anne_dede_birey = birey_map.get(anne_baba_id)
                if anne_dede_birey:
                    dede_hastaliklar = anne_dede_birey.get("hastaliklar", "Sağlıklı")
                    if dede_hastaliklar != "Sağlıklı" and isinstance(dede_hastaliklar, list):
                        for h in dede_hastaliklar:
                            if h.get("hastalik") == hastalik_adi:
                                anne_dede_durumu = h.get("durum")
                                break
        
        if baba:
            baba_ismi = f"{baba.get('isim', 'Bilinmeyen')} {baba.get('soyad', '')}".strip()
            baba_hastaliklar = baba.get("hastaliklar", "Sağlıklı")
            if baba_hastaliklar != "Sağlıklı" and isinstance(baba_hastaliklar, list):
                for h in baba_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        baba_durumu = h.get("durum")
                        break
            
            # Baba tarafı dede/nine
            baba_anne_id = str(baba.get("anne_id", "")) if baba.get("anne_id") else None
            baba_baba_id = str(baba.get("baba_id", "")) if baba.get("baba_id") else None
            
            if baba_anne_id:
                baba_nine_birey = birey_map.get(baba_anne_id)
                if baba_nine_birey:
                    nine_hastaliklar = baba_nine_birey.get("hastaliklar", "Sağlıklı")
                    if nine_hastaliklar != "Sağlıklı" and isinstance(nine_hastaliklar, list):
                        for h in nine_hastaliklar:
                            if h.get("hastalik") == hastalik_adi:
                                baba_nine_durumu = h.get("durum")
                                break
            
            if baba_baba_id:
                baba_dede_birey = birey_map.get(baba_baba_id)
                if baba_dede_birey:
                    dede_hastaliklar = baba_dede_birey.get("hastaliklar", "Sağlıklı")
                    if dede_hastaliklar != "Sağlıklı" and isinstance(dede_hastaliklar, list):
                        for h in dede_hastaliklar:
                            if h.get("hastalik") == hastalik_adi:
                                baba_dede_durumu = h.get("durum")
                                break
        
        risk_bilgisi['ebeveyn_durumu'] = {
            'anne': anne_durumu if anne_durumu else 'Sağlıklı',
            'baba': baba_durumu if baba_durumu else 'Sağlıklı'
        }
        
        # Hastalığın hangi aile üyesinden geçtiğini belirle
        gecis_kaynagi = None
        kaynak_listesi = []
        if anne_durumu and anne_durumu != "Sağlıklı":
            kaynak_listesi.append(f"Anne: {anne_ismi}")
        if baba_durumu and baba_durumu != "Sağlıklı":
            kaynak_listesi.append(f"Baba: {baba_ismi}")
        
        if kaynak_listesi:
            gecis_kaynagi = ", ".join(kaynak_listesi)
        
        # MODEL İLE RİSK ANALİZİ
        model_tahmin = None
        model_olasilik = None
        model_risk_seviyesi = None
        model_var_mi = False
        
        # Model ile tahmin yap (eğer hastalık mapping'de varsa)
        if hastalik_adi in DISEASES:
            model, le, train_columns = _load_model()
            if model and le and train_columns:
                try:
                    info = DISEASES[hastalik_adi]
                    
                    # Model için veri hazırla - durumları "Hasta" veya "Sağlam" olarak çevir
                    def durum_cevir(durum):
                        """Durumu model formatına çevir: Hasta/Taşıyıcı -> Hasta, diğerleri -> Sağlam"""
                        if durum and durum in ["Hasta", "Taşıyıcı"]:
                            return "Hasta"
                        return "Sağlam"
                    
                    veri = {
                        'Hastalık_Tipi': [info['Type']],
                        'Kalıtım_Modeli': [info['Mode']],
                        'Anne_Dede': [durum_cevir(anne_dede_durumu)],
                        'Anne_Nine': [durum_cevir(anne_nine_durumu)],
                        'Baba_Dede': [durum_cevir(baba_dede_durumu)],
                        'Baba_Nine': [durum_cevir(baba_nine_durumu)],
                        'Anne': [durum_cevir(anne_durumu)],
                        'Baba': [durum_cevir(baba_durumu)],
                        'Cocuk_Cinsiyet': [kullanici_cinsiyet]
                    }
                    
                    # DataFrame oluştur
                    input_df = pd.DataFrame(veri)
                    input_df = pd.get_dummies(input_df)
                    input_df = input_df.reindex(columns=train_columns, fill_value=0)
                    
                    # Tahmin yap
                    tahmin_idx = model.predict(input_df)[0]
                    model_tahmin = le.inverse_transform([tahmin_idx])[0]
                    
                    # Olasılık (Güven Oranı)
                    probs = model.predict_proba(input_df)[0]
                    model_olasilik = max(probs) * 100
                    
                    # Model çıktısına göre risk seviyesi belirle
                    if model_tahmin == 'Hasta':
                        if model_olasilik >= 80:
                            model_risk_seviyesi = 'Çok Yüksek'
                        elif model_olasilik >= 60:
                            model_risk_seviyesi = 'Yüksek'
                        else:
                            model_risk_seviyesi = 'Orta'
                    elif model_tahmin == 'Taşıyıcı':
                        if model_olasilik >= 70:
                            model_risk_seviyesi = 'Yüksek'
                        elif model_olasilik >= 50:
                            model_risk_seviyesi = 'Orta'
                        else:
                            model_risk_seviyesi = 'Düşük'
                    else:  # Sağlam
                        model_risk_seviyesi = 'Çok Düşük'
                    
                    print(f">>> DEBUG (risk_analysis): Model tahmin: {hastalik_adi} -> {model_tahmin}, Olasılık: %{model_olasilik:.1f}, Risk: {model_risk_seviyesi}", file=sys.stderr)
                    model_var_mi = True
                except Exception as e:
                    print(f">>> DEBUG (risk_analysis): Model tahmin hatası: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
        
        # Risk hesaplama (Model varsa model kullan, yoksa algoritma)
        if not model_var_mi:
            if sekil == 'Çekinik':
                # Otozomal çekinik kalıtım
                anne_hasta = anne_durumu == "Hasta"
                anne_tasiyici = anne_durumu == "Taşıyıcı"
                baba_hasta = baba_durumu == "Hasta"
                baba_tasiyici = baba_durumu == "Taşıyıcı"
                
                if anne_hasta and baba_hasta:
                    # Her ikisi de hasta ise çocuk kesinlikle taşıyıcı
                    risk_yuzdesi = 0  # Hastalık görülme olasılığı gösterilmez
                    risk_bilgisi['risk_seviyesi'] = 'Çok Yüksek'
                    risk_bilgisi['aciklama'] = 'Her iki ebeveyn de hasta. Kesinlikle taşıyıcısınız (%100).'
                    risk_bilgisi['tasiyici_olabilirlik'] = 100
                elif (anne_hasta and baba_tasiyici) or (anne_tasiyici and baba_hasta):
                    risk_yuzdesi = 0  # Hastalık görülme olasılığı gösterilmez
                    risk_bilgisi['risk_seviyesi'] = 'Yüksek'
                    risk_bilgisi['aciklama'] = 'Bir ebeveyn hasta, diğeri taşıyıcı. Taşıyıcı olma olasılığınız %50.'
                    risk_bilgisi['tasiyici_olabilirlik'] = 50
                elif anne_hasta or baba_hasta:
                    risk_yuzdesi = 0
                    risk_bilgisi['risk_seviyesi'] = 'Orta'
                    risk_bilgisi['aciklama'] = 'Bir ebeveyn hasta. Kesinlikle taşıyıcısınız (%100).'
                    risk_bilgisi['tasiyici_olabilirlik'] = 100
                elif anne_tasiyici and baba_tasiyici:
                    risk_yuzdesi = 0  # Hastalık görülme olasılığı gösterilmez
                    risk_bilgisi['risk_seviyesi'] = 'Orta'
                    risk_bilgisi['aciklama'] = 'Her iki ebeveyn de taşıyıcı. Taşıyıcı olma olasılığınız %50.'
                    risk_bilgisi['tasiyici_olabilirlik'] = 50
                elif anne_tasiyici or baba_tasiyici:
                    risk_yuzdesi = 0
                    risk_bilgisi['risk_seviyesi'] = 'Düşük'
                    risk_bilgisi['aciklama'] = 'Bir ebeveyn taşıyıcı. Taşıyıcı olma olasılığınız %50.'
                    risk_bilgisi['tasiyici_olabilirlik'] = 50
                else:
                    risk_yuzdesi = 0
                    risk_bilgisi['risk_seviyesi'] = 'Çok Düşük'
                    risk_bilgisi['aciklama'] = 'Ebeveynlerde hastalık belirtisi yok. Taşıyıcı olma riski düşük.'
                    risk_bilgisi['tasiyici_olabilirlik'] = 0
                
        elif sekil == 'X-Bağlı Çekinik':
                # X-bağlı çekinik kalıtım (cinsiyete bağlı)
                if kullanici_cinsiyet == 'Erkek':
                    # Erkek için: Anneden X kromozomu alır
                    if anne_durumu == "Hasta":
                        risk_yuzdesi = 0  # Hastalık görülme olasılığı gösterilmez
                        risk_bilgisi['risk_seviyesi'] = 'Çok Yüksek'
                        risk_bilgisi['aciklama'] = 'Anneniz hasta. X-bağlı hastalıklar için kesinlikle taşıyıcısınız (%100).'
                        risk_bilgisi['tasiyici_olabilirlik'] = 100
                    elif anne_durumu == "Taşıyıcı":
                        risk_yuzdesi = 0  # Hastalık görülme olasılığı gösterilmez
                        risk_bilgisi['risk_seviyesi'] = 'Yüksek'
                        risk_bilgisi['aciklama'] = 'Anneniz taşıyıcı. X-bağlı hastalıklar için taşıyıcı olma olasılığınız %50.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 50
                    else:
                        risk_yuzdesi = 0
                        risk_bilgisi['risk_seviyesi'] = 'Düşük'
                        risk_bilgisi['aciklama'] = 'Annenizde hastalık belirtisi yok. Taşıyıcı olma riski düşük.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 0
                else:  # Kadın
                    # Kadın için: Hem anneden hem babadan X kromozomu alır
                    if baba_durumu == "Hasta":
                        # Baba hasta ise, kız çocuk kesinlikle taşıyıcı
                        risk_yuzdesi = 0
                        risk_bilgisi['risk_seviyesi'] = 'Orta'
                        risk_bilgisi['aciklama'] = 'Babanız hasta. X-bağlı hastalıklar için kesinlikle taşıyıcısınız.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 100
                    elif anne_durumu == "Hasta" and baba_durumu != "Hasta":
                        risk_yuzdesi = 0
                        risk_bilgisi['risk_seviyesi'] = 'Orta'
                        risk_bilgisi['aciklama'] = 'Anneniz hasta. Taşıyıcı olabilirsiniz, ancak babanız hasta olmadığı için hastalık görülme riski düşük.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 50
                    elif anne_durumu == "Taşıyıcı" or baba_durumu == "Taşıyıcı":
                        risk_yuzdesi = 0
                        risk_bilgisi['risk_seviyesi'] = 'Düşük'
                        risk_bilgisi['aciklama'] = 'Bir ebeveyn taşıyıcı. Taşıyıcı olabilirsiniz.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 25
                    else:
                        risk_yuzdesi = 0
                        risk_bilgisi['risk_seviyesi'] = 'Çok Düşük'
                        risk_bilgisi['aciklama'] = 'Ebeveynlerde hastalık belirtisi yok. X-bağlı hastalıklar için kadınlarda risk çok düşük.'
                        risk_bilgisi['tasiyici_olabilirlik'] = 0
        
        # Model sonuçlarını risk bilgisine ekle
        if model_tahmin and model_olasilik is not None:
            risk_bilgisi['model_tahmin'] = model_tahmin
            risk_bilgisi['model_olasilik'] = round(model_olasilik, 1)
            risk_bilgisi['model_kullanildi'] = True
            # Model risk seviyesini kullan (eğer model varsa)
            if model_risk_seviyesi:
                risk_bilgisi['risk_seviyesi'] = model_risk_seviyesi
        else:
            risk_bilgisi['model_kullanildi'] = False
        
        risk_bilgisi['risk_yuzdesi'] = 0  # Hastalık görülme olasılığı her zaman 0 (kullanıcıya hastalık atanmaz)
        
        # Tüm atalarda (sadece ebeveynlerde değil) hastalık kontrolü yap
        # Soy ağacında en az bir taşıyıcı olması garantilendiği için, daha uzak atalara da bak
        def check_ancestors_for_disease(birey_id, depth=0, max_depth=5):
            """Özyinelemeli olarak atalarda hastalık kontrolü yapar ve bulunan ata bilgisini döndürür"""
            if depth > max_depth:
                return None
            
            birey = birey_map.get(birey_id)
            if not birey:
                return None
            
            birey_hastaliklar = birey.get("hastaliklar", "Sağlıklı")
            if birey_hastaliklar != "Sağlıklı" and isinstance(birey_hastaliklar, list):
                for h in birey_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        ata_ismi = f"{birey.get('isim', 'Bilinmeyen')} {birey.get('soyad', '')}".strip()
                        ata_bilgisi = {
                            'isim': ata_ismi,
                            'durum': h.get('durum'),
                            'kusak': birey.get('kusak', 'Bilinmeyen')
                        }
                        print(f">>> DEBUG (risk_analysis): Atalarda hastalık bulundu: {hastalik_adi}, birey_id={birey_id}, durum={h.get('durum')}, depth={depth}", file=sys.stderr)
                        return ata_bilgisi
            
            # Ebeveynlere bak (string karşılaştırması)
            anne_id = str(birey.get("anne_id", "")) if birey.get("anne_id") else None
            baba_id = str(birey.get("baba_id", "")) if birey.get("baba_id") else None
            if anne_id:
                anne_sonuc = check_ancestors_for_disease(anne_id, depth + 1, max_depth)
                if anne_sonuc:
                    return anne_sonuc
            if baba_id:
                baba_sonuc = check_ancestors_for_disease(baba_id, depth + 1, max_depth)
                if baba_sonuc:
                    return baba_sonuc
            
            return None
        
        # Ebeveynlerde hastalık yoksa, daha uzak atalara bak (Model yoksa)
        ata_hastalik_var = False
        ata_bilgisi = None
        if not model_var_mi and not anne_durumu and not baba_durumu:
            ata_bilgisi = check_ancestors_for_disease(kullanici_birey_id_str)
            ata_hastalik_var = ata_bilgisi is not None
            
            # Eğer atalarda hastalık varsa ama ebeveynlerde yoksa, risk bilgisi güncelle
            if ata_hastalik_var:
                risk_bilgisi['risk_seviyesi'] = 'Düşük'
                risk_bilgisi['aciklama'] = 'Önceki kuşaklarda bu hastalık tespit edilmiştir. Taşıyıcı olma olasılığınız değerlendirilmelidir.'
                risk_bilgisi['tasiyici_olabilirlik'] = 25  # Düşük olasılık
                # Atadan geçiş bilgisini ekle (ebeveynlerde yoksa)
                if not gecis_kaynagi and ata_bilgisi:
                    gecis_kaynagi = f"Ata: {ata_bilgisi['isim']} ({ata_bilgisi['kusak']}. kuşak)"
                print(f">>> DEBUG (risk_analysis): Atalarda hastalık bulundu, risk güncellendi: {hastalik_adi}", file=sys.stderr)
        
        # Risk analizini ekle - eğer herhangi bir risk belirtisi varsa ekle
        # Sadece tamamen risk yoksa (Çok Düşük + taşıyıcı olabilirlik 0 + atalarda hastalık yok) ekleme
        tasiyici_olabilirlik = risk_bilgisi.get('tasiyici_olabilirlik', 0)
        risk_seviyesi = risk_bilgisi.get('risk_seviyesi', 'Çok Düşük')
        
        # Risk varsa ekle (taşıyıcı olabilirlik > 0, atalarda hastalık var, ebeveynlerde hastalık var, veya model tahmin var)
        has_risk = tasiyici_olabilirlik > 0 or ata_hastalik_var or anne_durumu or baba_durumu or (model_tahmin and model_tahmin != 'Sağlam')
        
        if has_risk:
            # Geçiş kaynağını risk bilgisine ekle
            risk_bilgisi['gecis_kaynagi'] = gecis_kaynagi if gecis_kaynagi else "Bilinmeyen kaynak"
            risk_analizi.append(risk_bilgisi)
            print(f">>> DEBUG (risk_analysis): Risk EKLENDI: {hastalik_adi}, seviye={risk_seviyesi}, tasiyici={tasiyici_olabilirlik}%, model_tahmin={model_tahmin}, model_olasilik={model_olasilik}, model_kullanildi={risk_bilgisi.get('model_kullanildi')}, ata_var={ata_hastalik_var}, anne={anne_durumu}, baba={baba_durumu}, kaynak={gecis_kaynagi}, onerilen_bolum={risk_bilgisi.get('onerilen_bolum')}", file=sys.stderr)
        else:
            print(f">>> DEBUG (risk_analysis): Risk ATLANDI (hiç risk yok): {hastalik_adi}, seviye={risk_seviyesi}, tasiyici={tasiyici_olabilirlik}%, ata_var={ata_hastalik_var}, anne={anne_durumu}, baba={baba_durumu}", file=sys.stderr)
    
    # Eğer hiç risk analizi yoksa (hastalık listesi boşsa), en azından bir genel mesaj döndür
    if not risk_analizi:
        print("!!! UYARI: Risk analizi boş döndü. Hastalık listesi kontrol edilmeli veya soy ağacında hastalık yok.", file=sys.stderr)
    
    print(f">>> DEBUG (risk_analysis): Toplam {len(risk_analizi)} anlamlı risk bulundu.", file=sys.stderr)
    return risk_analizi

