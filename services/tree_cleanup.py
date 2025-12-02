import sys
from bson import ObjectId


def remove_duplicate_bireyler(mongo_db, family_tree_id_str: str):
    """
    Yardımcı TEMİZLİK fonksiyonu.
    Verilen FamilyTree dokümanındaki 'agac_verisi' listesini,
    'birey_id' alanına göre tekilleştirir.

    NOT: Bu fonksiyon otomatik olarak çağrılmıyor; gerekirse
    elle bir bakım/temizlik script'inde kullanılmalıdır.
    """
    try:
        family_trees_collection = mongo_db["FamilyTrees"]
        tree_object_id = ObjectId(family_tree_id_str)
        tree_doc = family_trees_collection.find_one({"_id": tree_object_id})

        if not tree_doc or "agac_verisi" not in tree_doc:
            print(f"!!! cleanup: FamilyTree {family_tree_id_str} bulunamadı veya 'agac_verisi' eksik.", file=sys.stderr)
            return False

        agac_verisi = tree_doc.get("agac_verisi", [])
        birey_map = {}
        for birey in agac_verisi:
            birey_id = birey.get("birey_id")
            if birey_id is None:
                continue
            if birey_id not in birey_map:
                birey_map[birey_id] = birey

        if len(birey_map) == len(agac_verisi):
            print(f">>> cleanup: FamilyTree {family_tree_id_str} için mükerrer birey bulunmadı.")
            return True

        yeni_liste = list(birey_map.values())
        family_trees_collection.update_one(
            {"_id": tree_object_id},
            {"$set": {"agac_verisi": yeni_liste}},
        )

        print(
            f">>> cleanup: FamilyTree {family_tree_id_str} için "
            f"{len(agac_verisi) - len(yeni_liste)} adet mükerrer birey temizlendi."
        )
        return True

    except Exception as e:
        print(f"!!! cleanup: Hata oluştu: {e}", file=sys.stderr)
        return False


