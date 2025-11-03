# genetics/risk_analysis.py
# Kullanıcı için risk analizi fonksiyonları

import sys
from genetics.genetics import get_hastalik_detaylari, determine_phenotype


def calculate_user_risk(soy_agaci_listesi, kullanici_birey_id, kullanici_cinsiyet):
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
    # Bireyleri ID'ye göre indeksle
    birey_map = {}
    for birey in soy_agaci_listesi:
        birey_map[birey.get("birey_id")] = birey
    
    # Kullanıcıyı bul
    kullanici_birey = birey_map.get(kullanici_birey_id)
    if not kullanici_birey:
        return []
    
    # Kullanıcının ebeveynlerini bul
    anne_id = kullanici_birey.get("anne_id")
    baba_id = kullanici_birey.get("baba_id")
    
    anne = birey_map.get(anne_id) if anne_id else None
    baba = birey_map.get(baba_id) if baba_id else None
    
    # Hastalık detaylarını al
    hastalik_detaylari = get_hastalik_detaylari()
    if not hastalik_detaylari:
        return []
    
    risk_analizi = []
    
    # Her hastalık için risk hesapla
    for hastalik_adi, details in hastalik_detaylari.items():
        sekil = details['sekil']
        oran = details.get('oran', 0)
        
        risk_bilgisi = {
            'hastalik': hastalik_adi,
            'kalitim_sekli': sekil,
            'risk_seviyesi': 'Düşük',
            'risk_yuzdesi': 0,
            'aciklama': '',
            'ebeveyn_durumu': {}
        }
        
        # Ebeveyn durumlarını kontrol et
        anne_durumu = None
        baba_durumu = None
        
        if anne:
            anne_hastaliklar = anne.get("hastaliklar", "Sağlıklı")
            if anne_hastaliklar != "Sağlıklı" and isinstance(anne_hastaliklar, list):
                for h in anne_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        anne_durumu = h.get("durum")
                        break
        
        if baba:
            baba_hastaliklar = baba.get("hastaliklar", "Sağlıklı")
            if baba_hastaliklar != "Sağlıklı" and isinstance(baba_hastaliklar, list):
                for h in baba_hastaliklar:
                    if h.get("hastalik") == hastalik_adi:
                        baba_durumu = h.get("durum")
                        break
        
        risk_bilgisi['ebeveyn_durumu'] = {
            'anne': anne_durumu if anne_durumu else 'Sağlıklı',
            'baba': baba_durumu if baba_durumu else 'Sağlıklı'
        }
        
        # Risk hesaplama
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
        
        risk_bilgisi['risk_yuzdesi'] = 0  # Hastalık görülme olasılığı her zaman 0 (kullanıcıya hastalık atanmaz)
        
        # Tüm atalarda (sadece ebeveynlerde değil) hastalık kontrolü yap
        # Soy ağacında en az bir taşıyıcı olması garantilendiği için, daha uzak atalara da bak
        ata_hastalik_var = False
        if not anne_durumu and not baba_durumu:
            # Ebeveynlerde hastalık yoksa, daha uzak atalara bak
            def check_ancestors_for_disease(birey_id, depth=0, max_depth=5):
                if depth > max_depth:
                    return False
                
                birey = birey_map.get(birey_id)
                if not birey:
                    return False
                
                birey_hastaliklar = birey.get("hastaliklar", "Sağlıklı")
                if birey_hastaliklar != "Sağlıklı" and isinstance(birey_hastaliklar, list):
                    for h in birey_hastaliklar:
                        if h.get("hastalik") == hastalik_adi:
                            return True
                
                # Ebeveynlere bak
                if birey.get("anne_id"):
                    if check_ancestors_for_disease(birey.get("anne_id"), depth + 1, max_depth):
                        return True
                if birey.get("baba_id"):
                    if check_ancestors_for_disease(birey.get("baba_id"), depth + 1, max_depth):
                        return True
                
                return False
            
            ata_hastalik_var = check_ancestors_for_disease(kullanici_birey_id)
            
            # Eğer atalarda hastalık varsa ama ebeveynlerde yoksa, risk bilgisi güncelle
            if ata_hastalik_var:
                risk_bilgisi['risk_seviyesi'] = 'Düşük'
                risk_bilgisi['aciklama'] = 'Önceki kuşaklarda bu hastalık tespit edilmiştir. Taşıyıcı olma olasılığınız değerlendirilmelidir.'
                risk_bilgisi['tasiyici_olabilirlik'] = 25  # Düşük olasılık
        
        # Risk analizini ekle - taşıyıcı olasılığı > 0 veya ebeveynlerde/atalarda hastalık varsa
        if risk_bilgisi.get('tasiyici_olabilirlik', 0) > 0:
            risk_analizi.append(risk_bilgisi)
        elif anne_durumu or baba_durumu or ata_hastalik_var:
            # Ebeveynlerde veya atalarda hastalık var ama taşıyıcı olma olasılığı 0 olsa bile göster
            risk_analizi.append(risk_bilgisi)
    
    return risk_analizi

