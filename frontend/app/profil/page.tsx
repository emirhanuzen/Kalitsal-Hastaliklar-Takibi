// app/profil/page.tsx
"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilSayfasi() {
  const router = useRouter();
  
  const [user, setUser] = useState<any>(null);
  const [hastalikBilgileri, setHastalikBilgileri] = useState<any[]>([]);
  const [soyAgaci, setSoyAgaci] = useState<any>(null);
  
  const [yukleniyorAI, setYukleniyorAI] = useState(false);
  const [yukleniyorAgac, setYukleniyorAgac] = useState(false);

  // Ana Sekmeler
  const [activeTab, setActiveTab] = useState('profil');
  
  // Soy Ağacı Alt Sekmesi (false: Geçmiş, true: Gelecek/Çocuklar)
  const [showChildren, setShowChildren] = useState(false);

  useEffect(() => {
    const savedUserString = localStorage.getItem('currentUser');
    if (savedUserString) {
      const parsedUser = JSON.parse(savedUserString);
      setUser(parsedUser);
    } else {
      router.push('/');
    }
  }, []);

  useEffect(() => {
    if (user) {
      fetchDiseaseInfo();
      fetchFamilyTree();
    }
  }, [user]);

  const fetchDiseaseInfo = async () => {
    if (!user || !user.user_id) return;
    try {
      setYukleniyorAI(true);
      // Profil API'sinden risk analizini al
      const response = await fetch(`/api/profil?user_id=${user.user_id}`);
      
      // Response'un JSON olup olmadığını kontrol et
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('❌ API JSON döndürmedi! Content-Type:', contentType);
        console.error('❌ Response (ilk 500 karakter):', text.substring(0, 500));
        throw new Error(`API JSON döndürmedi. Status: ${response.status}, Content-Type: ${contentType}`);
      }
      
      const data = await response.json();
      console.log('Profil API Response:', data); // Debug için
      console.log('Risk analizi var mı?', data.risk_analizi ? 'Evet' : 'Hayır');
      console.log('Risk analizi tipi:', typeof data.risk_analizi);
      console.log('Risk analizi uzunluğu:', data.risk_analizi ? (Array.isArray(data.risk_analizi) ? data.risk_analizi.length : 'Array değil') : 'Yok');
      if (data.durum === 'basarili') {
        if (data.risk_analizi && Array.isArray(data.risk_analizi) && data.risk_analizi.length > 0) {
          // Risk analizini hastalık bilgileri formatına çevir
          const hastalikBilgileri = data.risk_analizi.map((risk: any) => ({
            hastalik_adi: risk.hastalik || risk.hastalik_adi || 'Bilinmeyen Hastalık',
            kalitim_sekli: risk.kalitim_sekli || 'Çekinik',
            durum: risk.durum || risk.risk_seviyesi || 'Bilinmiyor',
            risk_seviyesi: risk.risk_seviyesi || 'Orta',
            gecme_olasiligi: risk.gecme_olasiligi || risk.tasiyici_olabilirlik ? `%${risk.tasiyici_olabilirlik}` : '%0',
            bilgi_icerigi: risk.bilgi_icerigi || risk.aciklama || 'Risk analizi yapıldı.',
            gecis_kaynagi: risk.gecis_kaynagi || null // Hastalığın hangi aile üyesinden geçtiği
          }));
          console.log('Risk analizi işlendi:', hastalikBilgileri);
          setHastalikBilgileri(hastalikBilgileri);
        } else {
          console.error('❌ Risk analizi boş veya bulunamadı!');
          console.error('API Response:', JSON.stringify(data, null, 2));
          console.error('risk_analizi değeri:', data.risk_analizi);
          console.error('risk_analizi tipi:', typeof data.risk_analizi);
          console.error('risk_analizi uzunluğu:', data.risk_analizi ? (Array.isArray(data.risk_analizi) ? data.risk_analizi.length : 'Array değil') : 'null/undefined');
          setHastalikBilgileri([]);
        }
      } else {
        console.error('API hatası:', data.mesaj || 'Bilinmeyen hata');
        setHastalikBilgileri([]);
      }
    } catch (error) { 
      console.error('Risk analizi hatası:', error); 
      setHastalikBilgileri([]);
    } finally { 
      setYukleniyorAI(false); 
    }
  };

  const fetchFamilyTree = async () => {
    if (!user || !user.user_id) return;
    try {
      setYukleniyorAgac(true);
      const response = await fetch(`/api/family-tree?user_id=${user.user_id}`);
      
      // Response'un JSON olup olmadığını kontrol et
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        const text = await response.text();
        console.error('❌ Family Tree API JSON döndürmedi! Status:', response.status);
        console.error('❌ Content-Type:', contentType);
        console.error('❌ Response (ilk 500 karakter):', text.substring(0, 500));
        throw new Error(`API JSON döndürmedi. Status: ${response.status}`);
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Family Tree API hata döndü! Status:', response.status);
        throw new Error(`API hatası: ${response.status}`);
      }
      
      const res = await response.json();
      console.log('Family Tree API Response:', res); // Debug için
      if (res.durum === 'basarili' && res.data) {
        setSoyAgaci(res.data);
      } else {
        console.log('Soy ağacı bulunamadı:', res);
        setSoyAgaci(null);
      }
    } catch (error) { 
      console.error('Soy ağacı hatası:', error); 
      setSoyAgaci(null);
    } finally { 
      setYukleniyorAgac(false); 
    }
  };

  const getStatusBadge = (durum: string) => {
    if (durum.includes("Hasta") || durum.includes("Riskli")) return <span className="badge bg-danger">{durum}</span>;
    if (durum.includes("Taşıyıcı")) return <span className="badge bg-warning text-dark">{durum}</span>;
    return <span className="badge bg-success">{durum}</span>;
  };

  const getCardBorder = (durum: string) => {
    if (durum.includes("Hasta") || durum.includes("Riskli")) return "3px solid #dc3545";
    if (durum.includes("Taşıyıcı")) return "3px solid #ffc107";
    return "3px solid #28a745";
  };

  if (!user) return <div className="d-flex justify-content-center align-items-center vh-100"><div className="spinner-border text-primary"></div></div>;

  return (
    <div className="container-fluid py-5">
        <div className="row justify-content-center">
            <div className="col-lg-10 col-xl-10">
                
                {/* ÜST BİLGİ */}
                <div className="modern-card animate-fade-in mb-4 d-flex justify-content-between align-items-center">
                    <div>
                        <h2 className="mb-0" style={{color: '#764ba2', fontWeight: 700}}>Merhaba, {user.isim}!</h2>
                        <p className="text-muted mb-0">Genetik analiz panelindesin.</p>
                    </div>
                    <button onClick={() => { localStorage.removeItem('currentUser'); router.push('/'); }} className="btn btn-outline-danger rounded-pill px-4">Çıkış Yap</button>
                </div>

                {/* ANA SEKMELER */}
                <div className="d-flex justify-content-center mb-4 animate-fade-in delay-1">
                    <div className="btn-group shadow-sm" style={{background: 'white', borderRadius: '50px', padding: '5px'}}>
                        <button type="button" className={`btn rounded-pill px-4 py-2 fw-bold ${activeTab === 'profil' ? 'btn-primary-custom text-white' : 'text-muted'}`} onClick={() => setActiveTab('profil')}>
                            <i className="bi bi-person-vcard me-2"></i> Profil ve Riskler
                        </button>
                        <button type="button" className={`btn rounded-pill px-4 py-2 fw-bold ${activeTab === 'soyagaci' ? 'btn-primary-custom text-white' : 'text-muted'}`} onClick={() => setActiveTab('soyagaci')}>
                            <i className="bi bi-diagram-3 me-2"></i> Soy Ağacı Analizi
                        </button>
                    </div>
                </div>

                {/* SEKME İÇERİĞİ: PROFİL */}
                {activeTab === 'profil' && (
                    <div className="animate-fade-in">
                        <div className="row mb-4">
                            <div className="col-md-6 mb-3"><div className="info-card"><div className="info-label">İsim Soyad</div><div className="info-value text-uppercase">{user.isim} {user.soyad}</div></div></div>
                            <div className="col-md-6 mb-3"><div className="info-card"><div className="info-label">TC Kimlik</div><div className="info-value">{user.kurgusal_tc || user.kendi_tc}</div></div></div>
                            <div className="col-md-6 mb-3"><div className="info-card"><div className="info-label">E-posta</div><div className="info-value">{user.email}</div></div></div>
                            <div className="col-md-6 mb-3"><div className="info-card"><div className="info-label">Doğum Tarihi</div><div className="info-value">{user.dogum_tarihi}</div></div></div>
                        </div>
                        <div className="modern-card">
                            <h3 className="header-title text-start mb-3"><i className="bi bi-robot me-2 text-accent"></i> Yapay Zeka Risk Analizi</h3>
                            {yukleniyorAI ? (
                                <div className="text-center py-4">
                                    <div className="spinner-border text-primary"></div>
                                    <p className="mt-2 text-muted">Analiz ediliyor...</p>
                                </div>
                            ) : hastalikBilgileri.length > 0 ? (
                                <div>
                                    {hastalikBilgileri.map((risk, index) => (
                                        <div key={index} className="hastalik-item mb-3 p-3 border rounded position-relative">
                                            {/* Sol üst köşede geçiş kaynağı */}
                                            {risk.gecis_kaynagi && (
                                                <div className="position-absolute top-0 start-0 bg-primary text-white px-2 py-1 rounded-bottom-end" style={{ fontSize: '0.75rem', zIndex: 10 }}>
                                                    <i className="bi bi-arrow-down-right me-1"></i>
                                                    {risk.gecis_kaynagi}
                                                </div>
                                            )}
                                            <div className="d-flex justify-content-between align-items-center mb-2" style={{ marginTop: risk.gecis_kaynagi ? '1.5rem' : '0' }}>
                                                <strong className="h5 mb-0">{risk.hastalik_adi}</strong>
                                                <div>
                                                    <span className="badge bg-secondary me-2">{risk.kalitim_sekli}</span>
                                                    <span className="badge bg-info text-dark">
                                                        <i className="bi bi-percent me-1"></i>
                                                        Geçme Olasılığı: {risk.gecme_olasiligi}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="mt-2">
                                                <p className="mb-0 text-muted">
                                                    <i className="bi bi-info-circle-fill me-2 text-primary"></i> 
                                                    {risk.bilgi_icerigi}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-4">
                                    <div className="alert alert-warning">
                                        <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                        <strong>Risk analizi bulunamadı veya henüz yapılmadı.</strong>
                                        <p className="mb-0 mt-2 small text-muted">
                                            Lütfen browser console'u (F12) açarak detaylı hata mesajlarını kontrol edin.
                                        </p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* SEKME İÇERİĞİ: SOY AĞACI */}
                {activeTab === 'soyagaci' && (
                    <div className="animate-fade-in">
                        <div className="modern-card text-center">
                            
                            {/* ALT SEKME (Geçmiş vs Gelecek) */}
                            <div className="d-flex justify-content-center mb-4">
                                <div className="btn-group" role="group">
                                    <input type="radio" className="btn-check" name="btnradio" id="btnradio1" autoComplete="off" checked={!showChildren} onChange={() => setShowChildren(false)} />
                                    <label className="btn btn-outline-primary" htmlFor="btnradio1">Atalarım (Geçmiş)</label>

                                    <input type="radio" className="btn-check" name="btnradio" id="btnradio2" autoComplete="off" checked={showChildren} onChange={() => setShowChildren(true)} />
                                    <label className="btn btn-outline-primary" htmlFor="btnradio2">Çocuklarım (Gelecek Simülasyonu)</label>
                                </div>
                            </div>

                            {yukleniyorAgac ? (
                                <div className="py-5"><div className="spinner-border text-primary"></div><p>Veriler yükleniyor...</p></div>
                            ) : soyAgaci ? (
                                <div>
                                    {/* SENARYO 1: GEÇMİŞ (Atalar) */}
                                    {!showChildren && soyAgaci.gecmis_kusaklar && soyAgaci.gecmis_kusaklar.length > 0 ? (
                                        soyAgaci.gecmis_kusaklar.map((kusak: any, index: number) => (
                                        <div key={index} className="generation-row mb-5 position-relative">
                                            <div className="generation-badge mb-3 d-inline-block px-3 py-1 rounded-pill bg-light border text-muted small">{kusak.baslik}</div>
                                            <div className="d-flex justify-content-center gap-4 flex-wrap position-relative" style={{zIndex: 2}}>
                                                {kusak.bireyler.map((birey: any) => (
                                                    <div key={birey.id} className="tree-node-card p-3 shadow-sm text-center" style={{background: 'white', borderRadius: '15px', minWidth: '160px', borderBottom: getCardBorder(birey.durum)}}>
                                                        <div className="mb-2">{birey.cinsiyet === 'Erkek' ? <i className="bi bi-gender-male fs-4 text-primary"></i> : <i className="bi bi-gender-female fs-4 text-danger"></i>}</div>
                                                        <div className="fw-bold text-dark">{birey.isim}</div>
                                                        <div className="small text-muted mb-2">({birey.rol})</div>
                                                        <div>{getStatusBadge(birey.durum)}</div>
                                                    </div>
                                                ))}
                                            </div>
                                            {index < soyAgaci.gecmis_kusaklar.length - 1 && <div className="connection-lines" style={{position: 'absolute', bottom: '-30px', left: '50%', transform: 'translateX(-50%)', width: '2px', height: '30px', background: '#e2e8f0', zIndex: 1}}></div>}
                                        </div>
                                        ))
                                    ) : (
                                        <div className="text-center py-4">
                                            <p className="text-muted">Geçmiş kuşak verisi bulunamadı.</p>
                                        </div>
                                    )}

                                    {/* SENARYO 2: GELECEK (Çocuklar) */}
                                    {showChildren && soyAgaci && soyAgaci.gelecek_kusak ? (
                                        <div className="animate-fade-in">
                                            <div className="alert alert-warning d-inline-block mb-4">
                                                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                                Bu bölüm, sizin ve potansiyel eşinizin genetik verilerine dayalı <strong>olasılıksal</strong> bir simülasyondur.
                                            </div>

                                            {/* Ebeveynler (Siz ve Eşiniz) */}
                                            <div className="d-flex justify-content-center gap-5 mb-5">
                                                {soyAgaci.gelecek_kusak.ebeveynler.map((ebeveyn: any, i: number) => (
                                                    <div key={i} className="tree-node-card p-4 shadow text-center" style={{background: '#f8fafc', borderRadius: '15px', minWidth: '180px', border: '2px dashed #667eea'}}>
                                                        <div className="mb-2">{ebeveyn.cinsiyet === 'Erkek' ? <i className="bi bi-gender-male fs-3 text-primary"></i> : <i className="bi bi-gender-female fs-3 text-danger"></i>}</div>
                                                        <div className="fw-bold h5">{ebeveyn.isim}</div>
                                                        <div className="text-muted mb-2">{ebeveyn.rol}</div>
                                                        {getStatusBadge(ebeveyn.durum)}
                                                    </div>
                                                ))}
                                            </div>

                                            {/* Bağlantı Çizgisi */}
                                            <div className="position-relative mb-5" style={{height: '40px'}}>
                                                <div style={{position: 'absolute', top: '-20px', left: '50%', transform: 'translateX(-50%)', width: '2px', height: '40px', background: '#cbd5e0'}}></div>
                                                <div style={{position: 'absolute', top: '20px', left: '25%', right: '25%', height: '2px', background: '#cbd5e0'}}></div> {/* Yatay çizgi */}
                                                <div style={{position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', width: '10px', height: '10px', background: '#667eea', borderRadius: '50%'}}></div> {/* Düğüm */}
                                            </div>

                                            {/* Çocuklar */}
                                            <div className="d-flex justify-content-center gap-4 flex-wrap">
                                                {soyAgaci.gelecek_kusak.cocuklar.map((cocuk: any) => (
                                                    <div key={cocuk.id} className="tree-node-card p-3 shadow-sm text-center animate-fade-in delay-1" style={{background: 'white', borderRadius: '15px', minWidth: '200px', borderBottom: getCardBorder(cocuk.durum)}}>
                                                        <div className="mb-2">{cocuk.cinsiyet === 'Erkek' ? <i className="bi bi-gender-male fs-4 text-primary"></i> : <i className="bi bi-gender-female fs-4 text-danger"></i>}</div>
                                                        <div className="fw-bold text-dark">{cocuk.isim}</div>
                                                        <div className="badge bg-light text-dark border mb-2 mt-1">Risk: {cocuk.risk_orani}</div>
                                                        <div>{getStatusBadge(cocuk.durum)}</div>
                                                        <div className="small text-muted mt-2 fst-italic" style={{fontSize: '0.85em'}}>{cocuk.aciklama}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="text-center py-4">
                                            <p className="text-muted">Gelecek kuşak verisi bulunamadı.</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="text-center py-4">
                                    <p className="text-muted">Soy ağacı verisi bulunamadı.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

            </div>
        </div>
    </div>
  );
}