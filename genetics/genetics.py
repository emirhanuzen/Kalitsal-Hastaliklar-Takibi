# genetics/genetics.py
# Genetik hesaplamalar (alel frekansları, genotip, fenotip)

import random
import math
import sys

# Global hastalık detayları (modül seviyesinde)
HASTALIK_DETAYLARI = {}


def calculate_allele_frequencies(hastalik_listesi_sql):
    """Hastalık listesinden alel frekanslarını hesaplar."""
    global HASTALIK_DETAYLARI
    HASTALIK_DETAYLARI = {}
    
    if not hastalik_listesi_sql:
        print("--- UYARI (ureteci): Boş hastalık listesi alındı.", file=sys.stderr)
        return
    
    for hastalik_tuple in hastalik_listesi_sql:
        if len(hastalik_tuple) < 3:
            print(f"--- UYARI (ureteci): Beklenenden eksik veri geldi: {hastalik_tuple}, atlanıyor.", file=sys.stderr)
            continue
        
        ad, oran, sekil = hastalik_tuple[:3]

        if oran is None or not isinstance(oran, (float, int)) or oran <= 0 or oran >= 1:
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için geçersiz oran ({oran}), atlanıyor.", file=sys.stderr)
            continue
        if not sekil or not isinstance(sekil, str):
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için geçersiz kalıtım şekli ({sekil}), atlanıyor.", file=sys.stderr)
            continue

        q = 0
        p = 1
        try:
            if sekil == 'Çekinik':
                q = math.sqrt(oran)
                p = 1 - q
            elif sekil == 'X-Bağlı Çekinik':
                q = oran
                p = 1 - q
            else:
                print(f"--- UYARI (ureteci): '{ad}' hastalığı için desteklenmeyen kalıtım şekli: {sekil}", file=sys.stderr)
                continue
        except ValueError:
            print(f"--- UYARI (ureteci): '{ad}' hastalığı için oran ({oran}) karekök alınamaz, atlanıyor.", file=sys.stderr)
            continue

        HASTALIK_DETAYLARI[ad] = {'oran': oran, 'sekil': sekil, 'q': q, 'p': p}
    
    print(f">>> DEBUG (ureteci): Hesaplanan alel frekansları: {HASTALIK_DETAYLARI}")


def determine_initial_genotype(hastalik_adi, cinsiyet):
    """Başlangıç genotipini belirler."""
    details = HASTALIK_DETAYLARI.get(hastalik_adi)
    if not details:
        return None
    
    p = details['p']
    q = details['q']
    sekil = details['sekil']
    rand_num = random.random()

    if sekil == 'Çekinik':
        if rand_num < p*p:
            return "NN"
        elif rand_num < p*p + 2*p*q:
            return "NT"
        else:
            return "TT"
    elif sekil == 'X-Bağlı Çekinik':
        if cinsiyet == 'Erkek':
            return "XnY" if rand_num < p else "XtY"
        else:  # Kadın
            if rand_num < p*p:
                return "XnXn"
            elif rand_num < p*p + 2*p*q:
                return "XnXt"
            else:
                return "XtXt"
    return None


def determine_phenotype(hastalik_adi, genotype, cinsiyet):
    """Genotipten fenotipi belirler."""
    details = HASTALIK_DETAYLARI.get(hastalik_adi)
    if not details or genotype is None:
        return None
    
    sekil = details['sekil']

    if sekil == 'Çekinik':
        if genotype == "TT":
            return "Hasta"
        elif genotype == "NT":
            return "Taşıyıcı"
        else:
            return None
    elif sekil == 'X-Bağlı Çekinik':
        if cinsiyet == 'Erkek':
            return "Hasta" if genotype == "XtY" else None
        else:  # Kadın
            if genotype == "XtXt":
                return "Hasta"
            elif genotype == "XnXt":
                return "Taşıyıcı"
            else:
                return None
    return None


def inherit_allele(parent_genotype, sekil, parent_cinsiyet):
    """Ebeveynden çocuğa geçecek tek bir aleli (geni) seçer."""
    if not parent_genotype:
        return None

    # Otozomal (Çekinik)
    if sekil == 'Çekinik':
        if len(parent_genotype) == 2:
            return random.choice(list(parent_genotype))
        else:
            print(f"--- UYARI (ureteci): Beklenmeyen otozomal genotip formatı: {parent_genotype}", file=sys.stderr)
            return None

    # X-Bağlı Çekinik
    elif sekil == 'X-Bağlı Çekinik':
        if parent_cinsiyet == 'Erkek':  # Baba XY (XnY veya XtY)
            x_allele = parent_genotype[:2]  # Xn veya Xt
            return random.choice([x_allele, 'Y'])
        else:  # Anne XX (XnXn, XnXt, XtXt)
            if len(parent_genotype) == 4 and parent_genotype.startswith("X"):
                allele1 = parent_genotype[0:2]  # Xn veya Xt
                allele2 = parent_genotype[2:4]  # Xn veya Xt
                return random.choice([allele1, allele2])
            else:
                print(f"--- UYARI (ureteci): Beklenmeyen X-bağlı kadın genotip formatı: {parent_genotype}", file=sys.stderr)
                return None
    
    return None


def get_hastalik_detaylari():
    """Hastalık detaylarını döndürür."""
    return HASTALIK_DETAYLARI

