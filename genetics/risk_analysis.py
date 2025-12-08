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
                    risk_bilgisi['tasiyici_olabilirlik'] = 0
        
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
        
        # Ebeveynlerde hastalık yoksa, daha uzak atalara bak
        ata_hastalik_var = False
        ata_bilgisi = None
        if not anne_durumu and not baba_durumu:
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
        
        # Risk varsa ekle (taşıyıcı olabilirlik > 0, atalarda hastalık var, ebeveynlerde hastalık var, veya risk seviyesi düşük değil)
        # NOT: risk_seviyesi != 'Çok Düşük' kontrolü her zaman True olacak çünkü risk_seviyesi zaten 'Düşük', 'Orta', 'Yüksek', 'Çok Yüksek' veya 'Çok Düşük' olabilir
        # Bu yüzden bu kontrolü kaldıralım ve sadece gerçek risk belirtilerine bakalım
        has_risk = tasiyici_olabilirlik > 0 or ata_hastalik_var or anne_durumu or baba_durumu
        
        if has_risk:
            # Geçiş kaynağını risk bilgisine ekle
            risk_bilgisi['gecis_kaynagi'] = gecis_kaynagi if gecis_kaynagi else "Bilinmeyen kaynak"
            risk_analizi.append(risk_bilgisi)
            print(f">>> DEBUG (risk_analysis): Risk EKLENDI: {hastalik_adi}, seviye={risk_seviyesi}, tasiyici={tasiyici_olabilirlik}%, ata_var={ata_hastalik_var}, anne={anne_durumu}, baba={baba_durumu}, kaynak={gecis_kaynagi}", file=sys.stderr)
        else:
            print(f">>> DEBUG (risk_analysis): Risk ATLANDI (hiç risk yok): {hastalik_adi}, seviye={risk_seviyesi}, tasiyici={tasiyici_olabilirlik}%, ata_var={ata_hastalik_var}, anne={anne_durumu}, baba={baba_durumu}", file=sys.stderr)
    
    # Eğer hiç risk analizi yoksa (hastalık listesi boşsa), en azından bir genel mesaj döndür
    if not risk_analizi:
        print("!!! UYARI: Risk analizi boş döndü. Hastalık listesi kontrol edilmeli veya soy ağacında hastalık yok.", file=sys.stderr)
    
    print(f">>> DEBUG (risk_analysis): Toplam {len(risk_analizi)} anlamlı risk bulundu.", file=sys.stderr)
    return risk_analizi

