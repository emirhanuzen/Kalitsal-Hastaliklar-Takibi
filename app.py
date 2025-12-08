# app.py
# Flask uygulaması ana dosyası - API Backend
# Next.js frontend kullanıldığı için sadece API endpoint'leri içerir

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

from config import JSON_AS_ASCII
from routes import register_user, test_connection, debug_my_children, get_my_children
from database import SQL_SERVER_CONNECTION_STRING, mongo_db

# Algoritma modülünü kontrol et
try:
    from soy_agaci_ureteci import uret_dinamik_soy_agaci
except ImportError:
    print("!!! HATA: soy_agaci_ureteci.py dosyası bulunamadı veya içe aktarılamadı.", file=sys.stderr)
    uret_dinamik_soy_agaci = None

# Flask uygulamasını oluştur
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = JSON_AS_ASCII
app.secret_key = 'kalitsal-hastalik-takibi-secret-key-2024'

# CORS ayarları - Next.js frontend için
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]},
}, supports_credentials=True)

# ============================================
# API ENDPOINT'LERİ - Next.js Frontend için
# ============================================

@app.route('/api/login', methods=['POST'])
def api_login():
    """JSON API - Giriş işlemi"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "durum": "hata",
                "mesaj": "İstek gövdesi boş olamaz."
            }), 400
        
        kurgusal_tc = data.get('kurgusal_tc')
        password = data.get('password')
        
        if not kurgusal_tc or not password:
            return jsonify({
                "durum": "hata",
                "mesaj": "TC kimlik numarası ve şifre zorunludur."
            }), 400
        
        # TC kontrolü
        if len(kurgusal_tc) != 11 or not kurgusal_tc.isdigit():
            return jsonify({
                "durum": "hata",
                "mesaj": "TC kimlik numarası 11 haneli olmalıdır."
            }), 400
        
        # Veritabanından kullanıcıyı bul
        import pyodbc
        import bcrypt
        
        sql_conn = None
        try:
            sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
            cursor = sql_conn.cursor()
            cursor.execute("""
                SELECT UserID, Email, KurgusalTC, PasswordHash, DogumTarihi, Isim, Soyad,
                       FamilyTreeID_Mongo, BireyID_Mongo
                FROM Users 
                WHERE KurgusalTC = ?
            """, (kurgusal_tc,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return jsonify({
                    "durum": "hata",
                    "mesaj": "TC kimlik numarası veya şifre hatalı."
                }), 401
            
            # Şifre kontrolü
            stored_password_hash = user_row[3]
            
            if stored_password_hash is None:
                return jsonify({
                    "durum": "hata",
                    "mesaj": "Kullanıcı şifre bilgisi bulunamadı."
                }), 401
            
            import base64
            password_hash_bytes = None
            
            if isinstance(stored_password_hash, bytes):
                try:
                    hash_str = stored_password_hash.decode('utf-8')
                    password_hash_bytes = base64.b64decode(hash_str)
                except:
                    password_hash_bytes = stored_password_hash
            elif isinstance(stored_password_hash, bytearray):
                try:
                    hash_str = bytes(stored_password_hash).decode('utf-8')
                    password_hash_bytes = base64.b64decode(hash_str)
                except:
                    password_hash_bytes = bytes(stored_password_hash)
            elif isinstance(stored_password_hash, str):
                try:
                    password_hash_bytes = base64.b64decode(stored_password_hash)
                except:
                    password_hash_bytes = stored_password_hash.encode('utf-8')
            else:
                hash_str = str(stored_password_hash)
                try:
                    password_hash_bytes = base64.b64decode(hash_str)
                except:
                    password_hash_bytes = hash_str.encode('utf-8')
            
            if not bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes):
                return jsonify({
                    "durum": "hata",
                    "mesaj": "TC kimlik numarası veya şifre hatalı."
                }), 401
            
            # Giriş başarılı
            user_id = user_row[0]
            dogum_tarihi = user_row[4]
            dogum_tarihi_str = dogum_tarihi.strftime('%Y-%m-%d') if dogum_tarihi else None
            
            return jsonify({
                "durum": "basarili",
                "user": {
                    "birey_id": user_id,
                    "user_id": user_id,
                    "isim": user_row[5] or "",
                    "soyad": user_row[6] or "",
                    "email": user_row[1] or "",
                    "kurgusal_tc": kurgusal_tc,
                    "dogum_tarihi": dogum_tarihi_str,
                    "family_tree_id": str(user_row[7]) if user_row[7] else None,
                    "birey_id_mongo": str(user_row[8]) if user_row[8] else None
                }
            }), 200
            
        except Exception as e:
            print(f"!!! Veritabanı hatası: {e}", file=sys.stderr)
            return jsonify({
                "durum": "hata",
                "mesaj": f"Veritabanı hatası: {str(e)}"
            }), 500
        finally:
            if sql_conn:
                sql_conn.close()
                
    except Exception as e:
        return jsonify({
            "durum": "hata",
            "mesaj": f"Giriş işlemi sırasında bir hata oluştu: {str(e)}"
        }), 500

@app.route('/api/hastalik-bilgisi', methods=['POST'])
def hastalik_bilgisi():
    """Gemini API ile hastalık bilgisi al - tek hastalık için"""
    try:
        from flask import jsonify
        from services.gemini_service import get_disease_information
        
        data = request.get_json()
        if not data:
            return jsonify({
                "basarili": False,
                "bilgi_icerigi": "İstek gövdesi boş olamaz."
            }), 400
        
        hastalik_adi = data.get('hastalik_adi', '')
        kalitim_sekli = data.get('kalitim_sekli', 'Çekinik')
        durum = data.get('durum', 'Taşıyıcı')
        
        if not hastalik_adi:
            return jsonify({
                "basarili": False,
                "bilgi_icerigi": "Hastalık adı belirtilmedi."
            }), 400
        
        # Gemini API'den bilgi al
        result = get_disease_information(hastalik_adi, kalitim_sekli, durum)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"!!! Hastalık bilgisi API hatası: {e}", file=sys.stderr)
        return jsonify({
            "basarili": False,
            "bilgi_icerigi": f"Hata: {str(e)}"
        }), 500

@app.route('/api/profil', methods=['GET'])
def api_profil():
    """JSON API - Kullanıcı profil bilgileri"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                "durum": "hata",
                "mesaj": "user_id parametresi gerekli."
            }), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                "durum": "hata",
                "mesaj": "Geçersiz user_id formatı."
            }), 400
        
        import pyodbc
        from bson import ObjectId
        from genetics.risk_analysis import calculate_user_risk
        
        sql_conn = None
        try:
            sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
            cursor = sql_conn.cursor()
            cursor.execute("""
                SELECT UserID, Email, KurgusalTC, DogumTarihi, Isim, Soyad, 
                       FamilyTreeID_Mongo, BireyID_Mongo
                FROM Users 
                WHERE UserID = ?
            """, (user_id,))
            
            user_row = cursor.fetchone()
            if not user_row:
                return jsonify({
                    "durum": "hata",
                    "mesaj": "Kullanıcı bulunamadı."
                }), 404
            
            dogum_tarihi = user_row[3]
            dogum_tarihi_str = dogum_tarihi.strftime('%Y-%m-%d') if dogum_tarihi else None
            
            user_data = {
                'user_id': user_row[0],
                'email': user_row[1],
                'kurgusal_tc': user_row[2],
                'dogum_tarihi': dogum_tarihi_str,
                'isim': user_row[4],
                'soyad': user_row[5],
                'family_tree_id': str(user_row[6]) if user_row[6] else None,
                'birey_id': str(user_row[7]) if user_row[7] else None
            }
            
        except Exception as e:
            return jsonify({
                "durum": "hata",
                "mesaj": f"Veritabanı hatası: {str(e)}"
            }), 500
        finally:
            if sql_conn:
                sql_conn.close()
        
        # MongoDB'den soy ağacını çek
        soy_agaci_data = None
        risk_analizi = []
        
        if user_data['family_tree_id']:
            try:
                from database import get_hastalik_listesi
                from genetics.genetics import calculate_allele_frequencies
                
                risk_sql_conn = None
                try:
                    risk_sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
                    hastalik_listesi = get_hastalik_listesi(risk_sql_conn)
                    print(f">>> DEBUG: Hastalık listesi SQL'den çekildi: {len(hastalik_listesi) if hastalik_listesi else 0} hastalık", file=sys.stderr)
                    if hastalik_listesi:
                        calculate_allele_frequencies(hastalik_listesi)
                        from genetics.genetics import get_hastalik_detaylari
                        detaylar = get_hastalik_detaylari()
                        print(f">>> DEBUG: Alel frekansları hesaplandı: {len(detaylar)} hastalık detayı", file=sys.stderr)
                    else:
                        print(f"!!! UYARI: Hastalık listesi boş!", file=sys.stderr)
                except Exception as e:
                    print(f"!!! Risk analizi için hastalık listesi yüklenirken hata: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
                finally:
                    if risk_sql_conn:
                        risk_sql_conn.close()
                
                family_trees_collection = mongo_db["FamilyTrees"]
                tree_object_id = ObjectId(user_data['family_tree_id'])
                tree_doc = family_trees_collection.find_one({"_id": tree_object_id})
                
                if tree_doc and "agac_verisi" in tree_doc:
                    soy_agaci_data = tree_doc["agac_verisi"]
                    
                    kullanici_birey = None
                    user_birey_id_str = str(user_data['birey_id'])
                    for birey in soy_agaci_data:
                        birey_id_str = str(birey.get("birey_id", ""))
                        if birey_id_str == user_birey_id_str:
                            kullanici_birey = birey
                            break
                    
                    if not kullanici_birey:
                        print(f"!!! UYARI: Kullanıcı bireyi bulunamadı. user_birey_id: {user_birey_id_str}", file=sys.stderr)
                        print(f"!!! DEBUG: Soy ağacında {len(soy_agaci_data)} birey var", file=sys.stderr)
                    
                    kullanici_cinsiyet = kullanici_birey.get("cinsiyet") if kullanici_birey else 'Erkek'
                    
                    print(f">>> DEBUG: Risk analizi başlatılıyor. user_birey_id: {user_birey_id_str}, cinsiyet: {kullanici_cinsiyet}", file=sys.stderr)
                    risk_analizi = calculate_user_risk(
                        soy_agaci_data, 
                        user_birey_id_str,  # String olarak gönder
                        kullanici_cinsiyet
                    )
                    print(f">>> DEBUG: Risk analizi tamamlandı. {len(risk_analizi)} risk bulundu.", file=sys.stderr)
                    
                    # Eğer risk analizi boşsa, debug bilgisi ver
                    if not risk_analizi:
                        print(f"!!! UYARI: Risk analizi boş döndü. Kullanıcı birey: {kullanici_birey is not None}, Soy ağacı: {len(soy_agaci_data) if soy_agaci_data else 0} birey", file=sys.stderr)
                    
                    # Risk analizini Gemini API ile zenginleştir
                    from services.gemini_service import get_disease_information
                    for idx, risk in enumerate(risk_analizi):
                        print(f">>> DEBUG: Risk {idx+1}/{len(risk_analizi)} işleniyor: {risk.get('hastalik', 'Bilinmeyen')}", file=sys.stderr)
                        risk['kalitim_sekli'] = risk.get('kalitim_sekli', 'Çekinik')
                        # Gemini API'den hastalık bilgisi al
                        try:
                            hastalik_adi = risk.get('hastalik', risk.get('hastalik_adi', ''))
                            if not hastalik_adi:
                                print(f"!!! UYARI: Risk analizinde hastalık adı bulunamadı: {risk}", file=sys.stderr)
                                risk['bilgi_icerigi'] = risk.get('aciklama', 'Risk analizi yapıldı.')
                                continue
                            
                            # Durum belirleme - risk seviyesine göre
                            durum = 'Taşıyıcı'
                            if risk.get('risk_seviyesi') in ['Çok Yüksek', 'Yüksek']:
                                durum = 'Yüksek Risk'
                            elif risk.get('risk_seviyesi') == 'Orta':
                                durum = 'Orta Risk'
                            
                            # Geçme olasılığını hesapla ve ekle
                            tasiyici_olabilirlik = risk.get('tasiyici_olabilirlik', 0)
                            risk['gecme_olasiligi'] = f"%{tasiyici_olabilirlik}"
                            
                            print(f">>> DEBUG: Gemini API çağrılıyor: {hastalik_adi}, {risk['kalitim_sekli']}, {durum}, geçme olasılığı: %{tasiyici_olabilirlik}", file=sys.stderr)
                            gemini_result = get_disease_information(hastalik_adi, risk['kalitim_sekli'], durum)
                            if gemini_result.get('basarili'):
                                # Gemini'den gelen bilgiyi temizle (HTML tag'lerini kaldır, sadece metin al)
                                bilgi_metni = gemini_result.get('bilgi_icerigi', '').strip()
                                # HTML tag'lerini kaldır
                                import re
                                bilgi_metni = re.sub(r'<[^>]+>', '', bilgi_metni)
                                bilgi_metni = bilgi_metni.strip()
                                # Eğer boşsa veya çok uzunsa, kısalt
                                if len(bilgi_metni) > 200:
                                    bilgi_metni = bilgi_metni[:200] + "..."
                                risk['bilgi_icerigi'] = bilgi_metni if bilgi_metni else risk.get('aciklama', f"{hastalik_adi} hakkında genel bilgi.")
                            else:
                                risk['bilgi_icerigi'] = risk.get('aciklama', f"{hastalik_adi} hakkında genel bilgi.")
                        except Exception as e:
                            print(f"!!! Gemini API hatası (risk analizi): {e}", file=sys.stderr)
                            import traceback
                            traceback.print_exc()
                            risk['bilgi_icerigi'] = risk.get('aciklama', f"{risk.get('hastalik', 'Hastalık')} için risk analizi yapıldı.")
            except Exception as e:
                print(f"!!! MongoDB hatası: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
        
        print(f">>> DEBUG: API profil response hazırlanıyor. Risk analizi sayısı: {len(risk_analizi)}", file=sys.stderr)
        if risk_analizi:
            print(f">>> DEBUG: İlk risk örneği: hastalik={risk_analizi[0].get('hastalik', 'Yok')}, risk_seviyesi={risk_analizi[0].get('risk_seviyesi', 'Yok')}", file=sys.stderr)
        else:
            print(f"!!! UYARI: API profil response'da risk_analizi BOŞ! user_id={user_data.get('user_id')}, family_tree_id={user_data.get('family_tree_id')}, birey_id={user_data.get('birey_id')}", file=sys.stderr)
            print(f"!!! DEBUG: soy_agaci_data var mı? {soy_agaci_data is not None}, uzunluk: {len(soy_agaci_data) if soy_agaci_data else 0}", file=sys.stderr)
        
        response_data = {
            "durum": "basarili",
            "user": user_data,
            "soy_agaci": soy_agaci_data,
            "risk_analizi": risk_analizi if risk_analizi else []
        }
        print(f">>> DEBUG: Response data hazır: risk_analizi uzunluğu={len(response_data['risk_analizi'])}", file=sys.stderr)
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "durum": "hata",
            "mesaj": f"Profil yüklenirken hata: {str(e)}"
        }), 500

@app.route('/api/family-tree', methods=['GET'])
def api_family_tree():
    """JSON API - Soy ağacı verileri"""
    try:
        user_id = request.args.get('user_id')
        family_tree_id = request.args.get('family_tree_id')
        
        if not user_id and not family_tree_id:
            return jsonify({
                "durum": "hata",
                "mesaj": "user_id veya family_tree_id parametresi gerekli."
            }), 400
        
        import pyodbc
        from bson import ObjectId
        
        # Eğer user_id verilmişse, family_tree_id'yi bul
        if user_id and not family_tree_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({
                    "durum": "hata",
                    "mesaj": "Geçersiz user_id formatı."
                }), 400
            
            sql_conn = None
            try:
                sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
                cursor = sql_conn.cursor()
                cursor.execute("""
                    SELECT FamilyTreeID_Mongo, BireyID_Mongo
                    FROM Users 
                    WHERE UserID = ?
                """, (user_id,))
                
                user_row = cursor.fetchone()
                if not user_row:
                    return jsonify({
                        "durum": "hata",
                        "mesaj": "Kullanıcı bulunamadı."
                    }), 404
                
                family_tree_id = str(user_row[0]) if user_row[0] else None
                birey_id = str(user_row[1]) if user_row[1] else None
                
            except Exception as e:
                return jsonify({
                    "durum": "hata",
                    "mesaj": f"Veritabanı hatası: {str(e)}"
                }), 500
            finally:
                if sql_conn:
                    sql_conn.close()
        
        if not family_tree_id:
            return jsonify({
                "durum": "hata",
                "mesaj": "Kullanıcının soy ağacı bulunamadı."
            }), 404
        
        # MongoDB'den soy ağacını çek
        try:
            family_trees_collection = mongo_db["FamilyTrees"]
            tree_object_id = ObjectId(family_tree_id)
            tree_doc = family_trees_collection.find_one({"_id": tree_object_id})
            
            if not tree_doc:
                return jsonify({
                    "durum": "hata",
                    "mesaj": "Soy ağacı bulunamadı."
                }), 404
            
            agac_verisi = tree_doc.get("agac_verisi", [])
            
            if not agac_verisi:
                return jsonify({
                    "durum": "basarili",
                    "data": {
                        "gecmis_kusaklar": [],
                        "gelecek_kusak": {
                            "ebeveynler": [],
                            "cocuklar": []
                        }
                    }
                }), 200
            
            # Kullanıcının birey ID'sini bul
            user_birey_id = None
            if user_id:
                try:
                    sql_conn_check = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
                    cursor_check = sql_conn_check.cursor()
                    cursor_check.execute("SELECT BireyID_Mongo FROM Users WHERE UserID = ?", (user_id,))
                    user_row = cursor_check.fetchone()
                    if user_row and user_row[0]:
                        user_birey_id = str(user_row[0])
                    sql_conn_check.close()
                except:
                    pass
            
            # Kullanıcı bireyini bul
            kullanici_birey = None
            for birey in agac_verisi:
                if str(birey.get("birey_id")) == user_birey_id:
                    kullanici_birey = birey
                    break
            
            if not kullanici_birey:
                kullanici_birey = agac_verisi[0] if agac_verisi else None
            
            # Kuşaklara göre grupla
            kusaklar = {}
            for birey in agac_verisi:
                kusak = birey.get("kusak", 0)
                if kusak not in kusaklar:
                    kusaklar[kusak] = []
                kusaklar[kusak].append(birey)
            
            # Geçmiş kuşakları formatla (kullanıcının kuşağı dahil)
            kullanici_kusak = kullanici_birey.get("kusak", 0) if kullanici_birey else 0
            gecmis_kusaklar = []
            kusak_isimleri = {
                1: "1. Kuşak (Büyük Büyük Büyük Ebeveynler)",
                2: "2. Kuşak (Büyük Büyük Ebeveynler)",
                3: "3. Kuşak (Büyük Ebeveynler)",
                4: "4. Kuşak (Dede/Nene)",
                5: "5. Kuşak (Ebeveynler)",
                6: "6. Kuşak (Siz)"
            }
            
            # Kullanıcının kuşağı dahil tüm geçmiş kuşakları göster
            for kusak_num in sorted([k for k in kusaklar.keys() if k <= kullanici_kusak], reverse=True):
                bireyler = []
                for birey in kusaklar[kusak_num]:
                    # Kullanıcının kendisi mi kontrol et
                    if str(birey.get("birey_id")) == user_birey_id:
                        rol = "Kendisi"
                    elif birey.get("birey_id") == kullanici_birey.get("anne_id"):
                        rol = "Anne"
                    elif birey.get("birey_id") == kullanici_birey.get("baba_id"):
                        rol = "Baba"
                    elif kullanici_birey:
                        anne = next((b for b in agac_verisi if b.get("birey_id") == kullanici_birey.get("anne_id")), None)
                        baba = next((b for b in agac_verisi if b.get("birey_id") == kullanici_birey.get("baba_id")), None)
                        if anne and birey.get("birey_id") == anne.get("anne_id"):
                            rol = "Anneanne"
                        elif anne and birey.get("birey_id") == anne.get("baba_id"):
                            rol = "Dede (Anne)"
                        elif baba and birey.get("birey_id") == baba.get("anne_id"):
                            rol = "Babaanne"
                        elif baba and birey.get("birey_id") == baba.get("baba_id"):
                            rol = "Dede (Baba)"
                    
                    durum = "Sağlıklı"
                    hastaliklar = birey.get("hastaliklar", "Sağlıklı")
                    if isinstance(hastaliklar, list) and hastaliklar:
                        if any(h.get("durum") == "Hasta" for h in hastaliklar):
                            durum = "Hasta"
                        elif any(h.get("durum") == "Taşıyıcı" for h in hastaliklar):
                            durum = "Taşıyıcı"
                    elif hastaliklar != "Sağlıklı":
                        durum = "Riskli"
                    
                    bireyler.append({
                        "id": str(birey.get("birey_id", "")),
                        "isim": f"{birey.get('isim', '')} {birey.get('soyad', '')}".strip(),
                        "rol": rol,
                        "durum": durum,
                        "cinsiyet": birey.get("cinsiyet", "Bilinmiyor")
                    })
                
                gecmis_kusaklar.append({
                    "seviye": kusak_num,
                    "baslik": kusak_isimleri.get(kusak_num, f"{kusak_num}. Kuşak"),
                    "bireyler": bireyler
                })
            
            # Gelecek kuşak (çocuklar)
            cocuklar = []
            ebeveynler = []
            
            if kullanici_birey:
                kullanici_durum = "Sağlıklı"
                kullanici_hastaliklar = kullanici_birey.get("hastaliklar", "Sağlıklı")
                if isinstance(kullanici_hastaliklar, list) and kullanici_hastaliklar:
                    if any(h.get("durum") == "Hasta" for h in kullanici_hastaliklar):
                        kullanici_durum = "Hasta"
                    elif any(h.get("durum") == "Taşıyıcı" for h in kullanici_hastaliklar):
                        kullanici_durum = "Taşıyıcı"
                
                ebeveynler.append({
                    "isim": f"{kullanici_birey.get('isim', '')} {kullanici_birey.get('soyad', '')}".strip(),
                    "rol": "Baba (Siz)" if kullanici_birey.get("cinsiyet") == "Erkek" else "Anne (Siz)",
                    "durum": kullanici_durum,
                    "cinsiyet": kullanici_birey.get("cinsiyet", "Bilinmiyor")
                })
                
                for birey in agac_verisi:
                    if (birey.get("anne_id") == kullanici_birey.get("birey_id") or 
                        birey.get("baba_id") == kullanici_birey.get("birey_id")):
                        cocuk_durum = "Sağlıklı"
                        cocuk_hastaliklar = birey.get("hastaliklar", "Sağlıklı")
                        if isinstance(cocuk_hastaliklar, list) and cocuk_hastaliklar:
                            if any(h.get("durum") == "Hasta" for h in cocuk_hastaliklar):
                                cocuk_durum = "Hasta"
                            elif any(h.get("durum") == "Taşıyıcı" for h in cocuk_hastaliklar):
                                cocuk_durum = "Taşıyıcı"
                        
                        cocuklar.append({
                            "id": str(birey.get("birey_id", "")),
                            "isim": f"{birey.get('isim', '')} {birey.get('soyad', '')}".strip(),
                            "cinsiyet": birey.get("cinsiyet", "Bilinmiyor"),
                            "durum": cocuk_durum,
                            "risk_orani": "%25",
                            "aciklama": "Genetik risk analizi yapıldı."
                        })
            
            return jsonify({
                "durum": "basarili",
                "data": {
                    "gecmis_kusaklar": gecmis_kusaklar,
                    "gelecek_kusak": {
                        "ebeveynler": ebeveynler,
                        "cocuklar": cocuklar
                    }
                }
            }), 200
            
        except Exception as e:
            return jsonify({
                "durum": "hata",
                "mesaj": f"MongoDB hatası: {str(e)}"
            }), 500
        
    except Exception as e:
        return jsonify({
            "durum": "hata",
            "mesaj": f"Soy ağacı yüklenirken hata: {str(e)}"
        }), 500

@app.route('/api/hastalik-bilgileri', methods=['POST'])
def hastalik_bilgileri():
    """Gemini API ile birden fazla hastalık bilgisi al"""
    try:
        from flask import jsonify
        from services.gemini_service import get_multiple_diseases_info
        
        data = request.get_json()
        if not data:
            return jsonify({
                "basarili": False,
                "mesaj": "İstek gövdesi boş olamaz."
            }), 400
        
        hastalik_listesi = data.get('hastalik_listesi', [])
        
        if not hastalik_listesi or not isinstance(hastalik_listesi, list):
            return jsonify({
                "basarili": False,
                "mesaj": "Geçerli hastalık listesi belirtilmedi."
            }), 400
        
        # Gemini API'den tüm hastalıklar için bilgi al
        hastalik_bilgileri = get_multiple_diseases_info(hastalik_listesi)
        
        return jsonify({
            "basarili": True,
            "hastalik_bilgileri": hastalik_bilgileri
        }), 200
        
    except Exception as e:
        print(f"!!! Hastalık bilgileri API hatası: {e}", file=sys.stderr)
        return jsonify({
            "basarili": False,
            "mesaj": f"Hata: {str(e)}"
        }), 500

# API Route'ları (mevcut)
app.add_url_rule('/api/register', 'register_user', register_user, methods=['POST'])
app.add_url_rule('/test-baglanti', 'test_connection', test_connection, methods=['GET'])
app.add_url_rule(
    '/api/debug/my-children/<family_tree_id>/<user_birey_id>',
    'debug_my_children',
    debug_my_children,
    methods=['GET']
)
app.add_url_rule('/api/get-my-children', 'get_my_children', get_my_children, methods=['GET'])

# Sunucuyu Başlatma Bloğu
if __name__ == '__main__':
    app.run(debug=True)
