# genetics/carrier_guarantee.py
# Soy ağacında en az bir taşıyıcı birey garantileme

import random
import sys
from genetics.genetics import get_hastalik_detaylari, determine_phenotype
from genetics.family_tree import get_bireyler


def ensure_at_least_one_carrier(kullanici_birey_id):
    """
    Soy ağacında en az bir taşıyıcı birey olduğundan emin olur.
    Eğer hiç taşıyıcı yoksa, kullanıcının atalarından birini taşıyıcı yapar.
    
    Args:
        kullanici_birey_id: Kullanıcının birey ID'si
    
    Returns:
        bool: Taşıyıcı birey oluşturuldu mu?
    """
    TUM_BIREYLER = get_bireyler()
    hastalik_detaylari = get_hastalik_detaylari()
    
    if not hastalik_detaylari:
        return False
    
    kullanici_birey = TUM_BIREYLER.get(kullanici_birey_id)
    if not kullanici_birey:
        return False
    
    # Kullanıcının atalarını bul (kullanıcı hariç)
    atalar = []
    
    def collect_ancestors(birey_id, depth=0, max_depth=10):
        """Kullanıcının tüm atalarını toplar"""
        if depth > max_depth:
            return
        
        birey = TUM_BIREYLER.get(birey_id)
        if not birey:
            return
        
        # Kullanıcı kendisi değilse ata listesine ekle
        if birey_id != kullanici_birey_id:
            atalar.append(birey)
        
        # Ebeveynleri bul ve özyinelemeli olarak topla
        anne_id = birey.get("anne_id")
        baba_id = birey.get("baba_id")
        
        if anne_id:
            collect_ancestors(anne_id, depth + 1, max_depth)
        if baba_id:
            collect_ancestors(baba_id, depth + 1, max_depth)
    
    # Kullanıcının atalarını topla
    collect_ancestors(kullanici_birey_id)
    
    if not atalar:
        # Kullanıcının atası yoksa, garanti etmek için yeni atalar oluşturmalıyız
        # Bu durum normalde olmamalı ama yine de kontrol edelim
        return False
    
    # Her hastalık için kontrol et
    tasiyici_var = False
    
    for hastalik_adi, details in hastalik_detaylari.items():
        sekil = details['sekil']
        
        # Bu hastalık için taşıyıcı var mı kontrol et
        hastalik_tasiyicisi_var = False
        
        for birey in atalar:
            if birey.get("birey_id") == kullanici_birey_id:
                continue  # Kullanıcıyı atla
            
            birey_genotipleri = birey.get("genotip", {})
            genotype = birey_genotipleri.get(hastalik_adi)
            
            if genotype:
                fenotip = determine_phenotype(hastalik_adi, genotype, birey["cinsiyet"])
                if fenotip == "Taşıyıcı" or fenotip == "Hasta":
                    hastalik_tasiyicisi_var = True
                    tasiyici_var = True
                    break
        
        # Eğer bu hastalık için taşıyıcı yoksa, bir tane oluştur
        if not hastalik_tasiyicisi_var:
            # Kullanıcının ebeveynlerinden birini seç (tercih edilen)
            # Eğer ebeveyn yoksa, rastgele bir atayı seç
            secilecek_bireyler = []
            
            anne_id = kullanici_birey.get("anne_id")
            baba_id = kullanici_birey.get("baba_id")
            
            if anne_id and TUM_BIREYLER.get(anne_id):
                secilecek_bireyler.append(TUM_BIREYLER[anne_id])
            if baba_id and TUM_BIREYLER.get(baba_id):
                secilecek_bireyler.append(TUM_BIREYLER[baba_id])
            
            # Eğer ebeveyn yoksa, diğer atalardan birini seç
            if not secilecek_bireyler:
                secilecek_bireyler = [b for b in atalar if b.get("birey_id") != kullanici_birey_id]
            
            if secilecek_bireyler:
                # Rastgele bir birey seç (ebeveyn tercih edilir)
                secilen_birey = random.choice(secilecek_bireyler)
                
                # Bu bireyin genotipini taşıyıcı yap
                if not secilen_birey.get("genotip"):
                    secilen_birey["genotip"] = {}
                
                if sekil == 'Çekinik':
                    # Otozomal çekinik: NT (Taşıyıcı) genotipi ata
                    secilen_birey["genotip"][hastalik_adi] = "NT"
                elif sekil == 'X-Bağlı Çekinik':
                    if secilen_birey["cinsiyet"] == 'Erkek':
                        # Erkek için X-bağlı çekinik hastalıkta taşıyıcı olamaz
                        # Erkekler sadece bir X kromozomu alır (anneden), eğer mutant ise hasta olur
                        # Bu durumda, annesini taşıyıcı yapmalıyız (çünkü erkek anneden X alır)
                        anne_id_secilen = secilen_birey.get("anne_id")
                        if anne_id_secilen and TUM_BIREYLER.get(anne_id_secilen):
                            anne_birey_secilen = TUM_BIREYLER[anne_id_secilen]
                            if not anne_birey_secilen.get("genotip"):
                                anne_birey_secilen["genotip"] = {}
                            # Anneyi taşıyıcı yap (XnXt)
                            anne_birey_secilen["genotip"][hastalik_adi] = "XnXt"
                            # Oğlunu da hasta yap (çünkü anneden mutant X alacak)
                            secilen_birey["genotip"][hastalik_adi] = "XtY"
                            print(f">>> DEBUG: {anne_birey_secilen.get('isim', 'Bilinmeyen')} {anne_birey_secilen.get('soyad', '')} (anne) {hastalik_adi} için taşıyıcı yapıldı.", file=sys.stderr)
                            print(f">>> DEBUG: {secilen_birey.get('isim', 'Bilinmeyen')} {secilen_birey.get('soyad', '')} (oğul) {hastalik_adi} için hasta yapıldı (X-bağlı çekinik).", file=sys.stderr)
                        else:
                            # Anne yoksa, başka bir kadın atayı taşıyıcı yap
                            kadin_atalar = [b for b in atalar if b.get("cinsiyet") == "Kadın" and b.get("birey_id") != kullanici_birey_id]
                            if kadin_atalar:
                                alternatif_kadin = random.choice(kadin_atalar)
                                if not alternatif_kadin.get("genotip"):
                                    alternatif_kadin["genotip"] = {}
                                alternatif_kadin["genotip"][hastalik_adi] = "XnXt"
                                print(f">>> DEBUG: {alternatif_kadin.get('isim', 'Bilinmeyen')} {alternatif_kadin.get('soyad', '')} (alternatif kadın) {hastalik_adi} için taşıyıcı yapıldı.", file=sys.stderr)
                    else:  # Kadın
                        # Kadın için: XnXt (Taşıyıcı) genotipi ata
                        secilen_birey["genotip"][hastalik_adi] = "XnXt"
                
                tasiyici_var = True
                print(f">>> DEBUG: {secilen_birey.get('isim', 'Bilinmeyen')} {secilen_birey.get('soyad', '')} bireyi {hastalik_adi} için taşıyıcı yapıldı.", file=sys.stderr)
    
    return tasiyici_var

