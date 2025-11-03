# app.py
# Flask uygulaması ana dosyası
# Modüler yapıda yeniden düzenlenmiştir

from flask import Flask, render_template, request, redirect, url_for, session
import sys

from config import JSON_AS_ASCII
from routes import register_user, test_connection
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

# Frontend Route'ları
@app.route('/')
def index():
    """Ana sayfa - Giriş sayfası"""
    # Eğer kullanıcı zaten giriş yaptıysa profil sayfasına yönlendir
    if 'user_id' in session:
        return redirect(url_for('profil', user_id=session['user_id']))
    return render_template('index.html')

@app.route('/kayit-ol')
def kayit_ol():
    """Kayıt ol sayfası"""
    return render_template('kayit.html')

@app.route('/giris', methods=['POST'])
def giris():
    """Giriş işlemi - TC ve şifre kontrolü"""
    try:
        kurgusal_tc = request.form.get('kurgusal_tc')
        password = request.form.get('password')
        
        if not kurgusal_tc or not password:
            return render_template('index.html', 
                                 message="TC kimlik numarası ve şifre zorunludur.", 
                                 message_type='danger')
        
        # TC kontrolü
        if len(kurgusal_tc) != 11 or not kurgusal_tc.isdigit():
            return render_template('index.html', 
                                 message="TC kimlik numarası 11 haneli olmalıdır.", 
                                 message_type='danger')
        
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
                return render_template('index.html', 
                                     message="TC kimlik numarası veya şifre hatalı.", 
                                     message_type='danger')
            
            # Şifre kontrolü
            stored_password_hash = user_row[3]  # PasswordHash
            
            # bcrypt ile şifreyi kontrol et
            try:
                # SQL Server'dan gelen hash'i işle
                # Hash VARBINARY olarak saklanıyorsa bytes/bytearray gelir
                # Hash VARCHAR olarak saklanıyorsa string gelir
                
                if stored_password_hash is None:
                    return render_template('index.html', 
                                         message="Kullanıcı şifre bilgisi bulunamadı.", 
                                         message_type='danger')
                
                # Tip kontrolü ve dönüşüm
                # Hem yeni format (base64 encoded) hem eski format (direkt bytes) destekleniyor
                import base64
                
                password_hash_bytes = None
                decode_method = None
                
                # Önce tip kontrolü yap
                if isinstance(stored_password_hash, bytes):
                    # bytes geliyorsa - eski format olabilir veya base64 encoded string bytes'a çevrilmiş olabilir
                    try:
                        # Önce base64 decode dene (yeni format)
                        hash_str = stored_password_hash.decode('utf-8')
                        password_hash_bytes = base64.b64decode(hash_str)
                        decode_method = "base64_from_bytes"
                    except:
                        # Başarısız olursa direkt bytes kullan (eski format)
                        password_hash_bytes = stored_password_hash
                        decode_method = "direct_bytes"
                        
                elif isinstance(stored_password_hash, bytearray):
                    # bytearray ise bytes'a çevir ve yukarıdaki mantığı uygula
                    try:
                        hash_str = bytes(stored_password_hash).decode('utf-8')
                        password_hash_bytes = base64.b64decode(hash_str)
                        decode_method = "base64_from_bytearray"
                    except:
                        password_hash_bytes = bytes(stored_password_hash)
                        decode_method = "direct_bytearray"
                        
                elif isinstance(stored_password_hash, str):
                    # String ise - yeni format (base64 encoded) olmalı
                    try:
                        password_hash_bytes = base64.b64decode(stored_password_hash)
                        decode_method = "base64_from_string"
                    except Exception as decode_error:
                        # Base64 decode başarısız - eski format olabilir (direkt encode edilmiş)
                        # Bu durumda encode etmeyi dene
                        try:
                            password_hash_bytes = stored_password_hash.encode('utf-8')
                            decode_method = "encode_string_fallback"
                        except:
                            raise Exception(f"Hash decode edilemedi: {decode_error}")
                else:
                    # Diğer tipler için string'e çevirip dene
                    hash_str = str(stored_password_hash)
                    try:
                        password_hash_bytes = base64.b64decode(hash_str)
                        decode_method = "base64_from_other"
                    except:
                        password_hash_bytes = hash_str.encode('utf-8')
                        decode_method = "encode_other_fallback"
                
                # Debug bilgisi
                print(f">>> DEBUG: Hash decode yöntemi: {decode_method}, Tip: {type(password_hash_bytes)}", file=sys.stderr)
                
                # Şifre kontrolü
                if not bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes):
                    return render_template('index.html', 
                                         message="TC kimlik numarası veya şifre hatalı.", 
                                         message_type='danger')
            except Exception as e:
                print(f"!!! Şifre kontrol hatası: {e}", file=sys.stderr)
                print(f"!!! Hash tipi: {type(stored_password_hash)}", file=sys.stderr)
                print(f"!!! Hash değeri (ilk 50 karakter): {str(stored_password_hash)[:50]}", file=sys.stderr)
                return render_template('index.html', 
                                     message="Giriş sırasında bir hata oluştu.", 
                                     message_type='danger')
            
            # Giriş başarılı - session'a kaydet
            user_id = user_row[0]
            session['user_id'] = user_id
            session['kurgusal_tc'] = kurgusal_tc
            
            # Profil sayfasına yönlendir
            return redirect(url_for('profil', user_id=user_id))
            
        except Exception as e:
            print(f"!!! Veritabanı hatası: {e}", file=sys.stderr)
            return render_template('index.html', 
                                 message=f"Veritabanı hatası: {str(e)}", 
                                 message_type='danger')
        finally:
            if sql_conn:
                sql_conn.close()
                
    except Exception as e:
        return render_template('index.html', 
                             message=f"Giriş işlemi sırasında bir hata oluştu: {str(e)}", 
                             message_type='danger')

@app.route('/kayit', methods=['POST'])
def kayit():
    """Kayıt işlemi - Form verilerini al ve kaydet"""
    try:
        # Form verilerini al ve JSON formatına çevir
        data = {
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'kendi_tc': request.form.get('kendi_tc'),
            'dogum_tarihi': request.form.get('dogum_tarihi'),
            'isim': request.form.get('isim'),
            'soyad': request.form.get('soyad'),
            'cinsiyet': request.form.get('cinsiyet'),
            'ebeveyn_tc': request.form.get('ebeveyn_tc') or None
        }
        
        # Veritabanı kontrolü
        if SQL_SERVER_CONNECTION_STRING is None or mongo_db is None:
            error_msg = "Sunucu başlangıç hatası: Veritabanı bağlantısı kurulamadı."
            return render_template('index.html', message=error_msg, message_type='danger')
        
        # Veriyi doğrula
        from validators import validate_register_data
        from services.registration_service import register_new_family, register_existing_family
        import pyodbc
        
        validated_data, error_msg, status_code = validate_register_data(data)
        if error_msg:
            return render_template('kayit.html', message=error_msg, message_type='danger')
        
        # SQL bağlantısını aç
        sql_conn = None
        try:
            sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING, autocommit=False)
            cursor = sql_conn.cursor()
            
            # Senaryo seçimi: Ebeveyn TC boş mu dolu mu?
            if not validated_data['ebeveyn_tc']:
                result, result_status_code = register_new_family(validated_data, sql_conn, cursor)
            else:
                result, result_status_code = register_existing_family(validated_data, sql_conn, cursor)
            
            if result_status_code in [200, 201] and result.get('durum') == 'basarili':
                # Kayıt başarılı, kullanıcıyı session'a ekle ve profil sayfasına yönlendir
                user_id = result.get('UserID')
                if user_id:
                    session['user_id'] = user_id
                    session['kurgusal_tc'] = data.get('kendi_tc')
                    return redirect(url_for('profil', user_id=user_id))
                else:
                    return render_template('kayit.html', 
                                         message=result.get('mesaj', 'Kayıt başarıyla tamamlandı!'), 
                                         message_type='success')
            else:
                error_msg = result.get('mesaj', 'Kayıt sırasında bir hata oluştu.')
                return render_template('kayit.html', message=error_msg, message_type='danger')
                
        except Exception as e:
            error_msg = f"Kayıt sırasında bir hata oluştu: {str(e)}"
            if sql_conn:
                try:
                    sql_conn.rollback()
                except:
                    pass
            return render_template('kayit.html', message=error_msg, message_type='danger')
        finally:
            if sql_conn:
                try:
                    sql_conn.close()
                except:
                    pass
                
    except Exception as e:
        error_msg = f"Kayıt işlemi sırasında bir hata oluştu: {str(e)}"
        return render_template('kayit.html', message=error_msg, message_type='danger')

@app.route('/profil/<int:user_id>')
def profil(user_id):
    """Kullanıcı profil sayfası"""
    # Session kontrolü
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('index'))
    
    try:
        import pyodbc
        from bson import ObjectId
        from genetics.risk_analysis import calculate_user_risk
        
        # SQL Server'dan kullanıcı bilgilerini çek
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
                # Session'dan çıkış yap
                session.clear()
                return render_template('index.html', 
                                   message="Kullanıcı bulunamadı.", 
                                   message_type='danger')
            
            user_data = {
                'user_id': user_row[0],
                'email': user_row[1],
                'kurgusal_tc': user_row[2],
                'dogum_tarihi': user_row[3],
                'isim': user_row[4],
                'soyad': user_row[5],
                'family_tree_id': user_row[6],
                'birey_id': user_row[7]
            }
            
        except Exception as e:
            session.clear()
            return render_template('index.html', 
                                 message=f"Veritabanı hatası: {str(e)}", 
                                 message_type='danger')
        finally:
            if sql_conn:
                sql_conn.close()
        
        # MongoDB'den soy ağacını çek
        soy_agaci_data = None
        kullanici_birey = None
        
        if user_data['family_tree_id']:
            try:
                # Risk analizi için hastalık detaylarını yükle
                from database import get_hastalik_listesi
                from genetics.genetics import calculate_allele_frequencies
                
                # SQL bağlantısı açık değilse yeniden aç
                risk_sql_conn = None
                try:
                    risk_sql_conn = pyodbc.connect(SQL_SERVER_CONNECTION_STRING)
                    hastalik_listesi = get_hastalik_listesi(risk_sql_conn)
                    if hastalik_listesi:
                        calculate_allele_frequencies(hastalik_listesi)
                        print(f">>> DEBUG: Risk analizi için {len(hastalik_listesi)} hastalık yüklendi.", file=sys.stderr)
                    else:
                        print(f">>> UYARI: Hastalık listesi boş, risk analizi yapılamayabilir.", file=sys.stderr)
                except Exception as e:
                    print(f"!!! Risk analizi için hastalık listesi yüklenirken hata: {e}", file=sys.stderr)
                finally:
                    if risk_sql_conn:
                        risk_sql_conn.close()
                
                family_trees_collection = mongo_db["FamilyTrees"]
                tree_object_id = ObjectId(user_data['family_tree_id'])
                tree_doc = family_trees_collection.find_one({"_id": tree_object_id})
                
                if tree_doc and "agac_verisi" in tree_doc:
                    soy_agaci_data = tree_doc["agac_verisi"]
                    
                    # Kullanıcının kendi birey bilgisini bul
                    for birey in soy_agaci_data:
                        if birey.get("birey_id") == user_data['birey_id']:
                            kullanici_birey = birey
                            break
                    
                    # Kullanıcı için risk analizi yap
                    kullanici_cinsiyet = kullanici_birey.get("cinsiyet") if kullanici_birey else None
                    if not kullanici_cinsiyet:
                        # Kullanıcı birey bilgisi yoksa SQL'den cinsiyeti al (eğer varsa)
                        # Şimdilik varsayılan olarak 'Erkek' kullan
                        kullanici_cinsiyet = 'Erkek'
                    
                    risk_analizi = calculate_user_risk(
                        soy_agaci_data, 
                        user_data['birey_id'],
                        kullanici_cinsiyet
                    )
                    print(f">>> DEBUG: Risk analizi tamamlandı, {len(risk_analizi)} risk bulundu.", file=sys.stderr)
                else:
                    risk_analizi = []
                    kullanici_birey = None
            except Exception as e:
                print(f"!!! MongoDB hatası: {e}", file=sys.stderr)
                risk_analizi = []
                kullanici_birey = None
        else:
            risk_analizi = []
            kullanici_birey = None
        
        # Risk analizinden kalıtım şekillerini ekle
        if risk_analizi:
            for risk in risk_analizi:
                # Risk analizindeki hastalıklara kalıtım şeklini ekle
                risk['kalitim_sekli'] = risk.get('kalitim_sekli', 'Çekinik')
        
        return render_template('profil.html', 
                             user=user_data, 
                             soy_agaci=soy_agaci_data,
                             kullanici_birey=kullanici_birey,
                             risk_analizi=risk_analizi)
        
    except Exception as e:
        session.clear()
        return render_template('index.html', 
                             message=f"Profil yüklenirken hata: {str(e)}", 
                             message_type='danger')

@app.route('/cikis')
def cikis():
    """Çıkış işlemi"""
    session.clear()
    return redirect(url_for('index'))

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

# Sunucuyu Başlatma Bloğu
if __name__ == '__main__':
    app.run(debug=True)
