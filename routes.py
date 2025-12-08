# routes.py
# API endpoint'leri
# DÜZELTME: Gereksiz/hatalı import kaldırıldı ve başlangıç kontrolü düzeltildi.

from flask import jsonify, request
import pyodbc  # SQL bağlantısı bu dosyada oluşturuluyor
import sys
from bson import ObjectId

# Bu importların çalışması için database.py, validators.py ve services/ klasörünün
# bu dosyayla aynı dizin yapısında olması gerekir.
from database import SQL_SERVER_CONNECTION_STRING, mongo_db, get_hastalik_listesi
from validators import validate_register_data
from services.registration_service import register_new_family, register_existing_family


# !!! KALDIRILDI: Bu import hem gereksizdi (kullanılmıyordu) hem de 'dainamik' yazım hatası vardı.
# from soy_agaci_ureteci import uret_dainamik_soy_agaci


def register_user():
    """Ana kayıt API endpoint'i"""

    # <<< DÜZELTME: Kontrol, algoritma fonksiyonuna değil, veritabanı bağlantılarına bakmalı >>>
    if SQL_SERVER_CONNECTION_STRING is None or mongo_db is None:
        return jsonify({
            "durum": "hata",
            "mesaj": "Sunucu başlangıç hatası: Veritabanı bağlantısı kurulamadı."
        }), 500

    # JSON verisini al
    data = request.get_json()
    if not data:
        return jsonify({
            "durum": "hata",
            "mesaj": "İstek gövdesi (body) boş olamaz. JSON verisi gönderin."
        }), 400

    # Veriyi doğrula
    validated_data, error_msg, status_code = validate_register_data(data)
    if error_msg:
        return jsonify({"durum": "hata", "mesaj": error_msg}), status_code

    # SQL bağlantısını aç
    sql_conn = None
    try:
        sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING, autocommit=False)
        cursor = sql_conn.cursor()
        print(">>> DEBUG: SQL Bağlantısı açıldı (autocommit=False).")
    except Exception as e:
        print(f"!!! SQL Server bağlantı hatası (kayıt sırasında): {e}", file=sys.stderr)
        return jsonify({"durum": "hata", "mesaj": f"Veritabanı bağlantı hatası."}), 500

    try:
        # Senaryo seçimi: Ebeveyn TC boş mu dolu mu?
        if not validated_data['ebeveyn_tc']:
            result, status_code = register_new_family(validated_data, sql_conn, cursor)
        else:
            result, status_code = register_existing_family(validated_data, sql_conn, cursor)

        return jsonify(result), status_code

    except Exception as e:
        # Beklenmedik bir hata olursa (örn: register_new_family içinde)
        print(f"!!! Ana kayıt bloğunda beklenmedik hata: {e}", file=sys.stderr)
        try:
            sql_conn.rollback()  # SQL işlemini geri al
        except:
            pass
        return jsonify({"durum": "hata", "mesaj": f"İşlem sırasında beklenmedik bir sunucu hatası oluştu: {e}"}), 500

    finally:
        if sql_conn:
            try:
                sql_conn.close()
            except:
                pass
            print(">>> DEBUG: SQL Bağlantısı kapatıldı.")


def test_connection():
    """Test endpoint'i - veritabanı bağlantılarını test eder"""
    results = {}

    if SQL_SERVER_CONNECTION_STRING is not None:
        try:
            with pyodbc.connect(SQL_SERVER_CONNECTION_STRING) as conn:
                results['sql_server'] = "Bağlantı BAŞARILI!"
        except Exception as e:
            results['sql_server'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['sql_server'] = "HATA: Bağlantı dizesi ayarlanamadı."

    if mongo_db is not None:
        try:
            mongo_db.client.admin.command('ping')
            results['mongodb'] = "Bağlantı BAŞARILI!"
        except Exception as e:
            results['mongodb'] = f"BAĞLANTI HATASI: {e}"
    else:
        results['mongodb'] = "HATA: Bağlantı kurulamadı."

    return jsonify(results)


def debug_my_children(family_tree_id, user_birey_id):
    """
    GEÇİCİ / DEBUG ENDPOINT
    Belirli bir soy ağacında, verilen bireyin çocuklarını ve
    onlar için tahmini (simüle) risk raporlarını döner.
    """
    if mongo_db is None:
        return jsonify({
            "durum": "hata",
            "mesaj": "MongoDB bağlantısı bulunamadı."
        }), 500

    try:
        try:
            tree_object_id = ObjectId(family_tree_id)
        except Exception:
            return jsonify({
                "durum": "hata",
                "mesaj": "Geçersiz family_tree_id formatı."
            }), 400

        family_trees_collection = mongo_db["FamilyTrees"]
        tree_doc = family_trees_collection.find_one({"_id": tree_object_id})

        if not tree_doc:
            return jsonify({
                "durum": "hata",
                "mesaj": "Belirtilen soy ağacı bulunamadı."
            }), 404

        agac_verisi = tree_doc.get("agac_verisi", [])
        if not isinstance(agac_verisi, list):
            return jsonify({
                "durum": "hata",
                "mesaj": "Soy ağacı verisi beklenen formatta değil."
            }), 500

        # Kullanıcının çocuklarını bul (anne veya baba olarak)
        cocuklar = []
        for birey in agac_verisi:
            anne_id = birey.get("anne_id")
            baba_id = birey.get("baba_id")
            if anne_id == user_birey_id or baba_id == user_birey_id:
                ad = birey.get("isim", "")
                soyad = birey.get("soyad", "")
                tam_ad = f"{ad} {soyad}".strip()

                # Çocuğun kurgusal TC bilgisi (varsa)
                kurgusal_tc = birey.get("kurgusal_tc") or birey.get("kendi_tc") or ""

                # Basit, sabit bir simüle risk raporu (sadece debug/observe amaçlı)
                simule_risk = "Orak Hücreli Anemi: %25 Hasta Olma İhtimali, %50 Taşıyıcı"

                cocuklar.append({
                    "birey_id": birey.get("birey_id"),
                    "isim": tam_ad or "İsimsiz Çocuk",
                    "kurgusal_tc": kurgusal_tc,
                    "risk_raporu": simule_risk
                })

        return jsonify({
            "durum": "basarili",
            "cocuk_sayisi": len(cocuklar),
            "cocuklar": cocuklar
        }), 200

    except Exception as e:
        print(f"!!! debug_my_children hata: {e}", file=sys.stderr)
        return jsonify({
            "durum": "hata",
            "mesaj": f"Beklenmedik bir hata oluştu: {str(e)}"
        }), 500


def get_my_children():
    """
    Kullanıcının çocuklarını query parametreleri ile dönen API.
    Endpoint: /api/get-my-children?family_tree_id=...&parent_birey_id=...
    (Geriye dönük uyumluluk için user_birey_id de desteklenir.)
    """
    if mongo_db is None:
        return jsonify({
            "durum": "hata",
            "mesaj": "MongoDB bağlantısı bulunamadı."
        }), 500

    family_tree_id = request.args.get("family_tree_id")
    parent_birey_id = request.args.get("parent_birey_id") or request.args.get("user_birey_id")

    if not family_tree_id or not parent_birey_id:
        return jsonify({
            "durum": "hata",
            "mesaj": "family_tree_id ve parent_birey_id parametreleri zorunludur."
        }), 400

    try:
        try:
            tree_object_id = ObjectId(family_tree_id)
        except Exception:
            return jsonify({
                "durum": "hata",
                "mesaj": "Geçersiz family_tree_id formatı."
            }), 400

        family_trees_collection = mongo_db["FamilyTrees"]
        tree_doc = family_trees_collection.find_one({"_id": tree_object_id})

        if not tree_doc:
            return jsonify({
                "durum": "hata",
                "mesaj": "Belirtilen soy ağacı bulunamadı."
            }), 404

        agac_verisi = tree_doc.get("agac_verisi", [])
        if not isinstance(agac_verisi, list):
            return jsonify({
                "durum": "hata",
                "mesaj": "Soy ağacı verisi beklenen formatta değil."
            }), 500

        children = []
        for birey in agac_verisi:
            anne_id = birey.get("anne_id")
            baba_id = birey.get("baba_id")
            if anne_id == parent_birey_id or baba_id == parent_birey_id:
                ad = birey.get("isim", "") or ""
                soyad = birey.get("soyad", "") or ""
                tam_ad = f"{ad} {soyad}".strip() or "İsimsiz Çocuk"

                hastaliklar = birey.get("hastaliklar")
                risk_analizi = "Genetik risk bilgisi bulunamadı."

                # Hastalık durumuna göre basit risk metni üret
                try:
                    if isinstance(hastaliklar, str):
                        if hastaliklar == "Sağlıklı":
                            risk_analizi = "Risk: Düşük. Bilinen kalıtsal hastalık saptanmadı."
                        else:
                            risk_analizi = f"Risk: Orta. {hastaliklar} ile ilişkili genetik risk olabilir."
                    elif isinstance(hastaliklar, list) and hastaliklar:
                        durumlar = [h.get("durum") for h in hastaliklar if isinstance(h, dict)]
                        if any(d == "Hasta" for d in durumlar):
                            risk_analizi = "Risk: Yüksek. Çocuğunuzda kalıtsal hastalık mevcut, üst kuşaklara geçiş ihtimali artmıştır."
                        elif any(d == "Taşıyıcı" for d in durumlar):
                            risk_analizi = "Risk: Orta. Çocuğunuz taşıyıcı, kendi çocuklarına hastalığı %50 civarında aktarma ihtimali vardır."
                        else:
                            risk_analizi = "Risk: Düşük. Ciddi bir kalıtsal hastalık bulgusu saptanmadı."
                except Exception as risk_err:
                    print(f">>> DEBUG: risk_analizi hesaplanırken hata: {risk_err}", file=sys.stderr)

                child_obj = {
                    "birey_id": birey.get("birey_id"),
                    "isim": ad,
                    "soyad": soyad,
                    "ad_soyad": tam_ad,
                    "cinsiyet": birey.get("cinsiyet"),
                    "dogum_yili": birey.get("dogum_yili"),
                    "kurgusal_tc": birey.get("kurgusal_tc") or birey.get("kendi_tc") or "",
                    "hastaliklar": hastaliklar,
                    "risk_analizi": risk_analizi,
                }
                children.append(child_obj)

        print(f">>> DEBUG: Found {len(children)} children", file=sys.stderr)

        return jsonify({
            "durum": "basarili",
            "cocuk_sayisi": len(children),
            "cocuklar": children
        }), 200

    except Exception as e:
        print(f"!!! get_my_children hata: {e}", file=sys.stderr)
        return jsonify({
            "durum": "hata",
            "mesaj": f"Beklenmedik bir hata oluştu: {str(e)}"
        }), 500