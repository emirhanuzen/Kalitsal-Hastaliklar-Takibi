"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilSayfasi() {
  const router = useRouter();
  
  const [user, setUser] = useState<any>(null);
  const [hastalikBilgileri, setHastalikBilgileri] = useState<any[]>([]);
  const [soyAgaci, setSoyAgaci] = useState<any>(null);
  
  // Pop-up için seçilen hastalık durumu
  const [selectedRisk, setSelectedRisk] = useState<any>(null);
  
  const [yukleniyorAI, setYukleniyorAI] = useState(false);
  const [yukleniyorAgac, setYukleniyorAgac] = useState(false);

  // Ana Sekmeler
  const [activeTab, setActiveTab] = useState('profil');
  
  // Soy Ağacı Alt Sekmesi (false: Geçmiş, true: Gelecek/Çocuklar)
  const [showChildren, setShowChildren] = useState(false);

  // --- 1. GİRİŞ KONTROLÜ (TEST İÇİN BYPASS EDİLDİ) ---
  useEffect(() => {
    const testKullanici = {
        user_id: "test-1",
        isim: "Test",
        soyad: "Kullanıcısı",
        email: "test@genetik.com",
        kendi_tc: "12345678901",
        dogum_tarihi: "01.01.1990",
        cinsiyet: "Erkek", // veya 'Kadın'
        profilePhoto: null // Varsa base64 string
    };

    console.log("🛠️ TEST MODU: Sahte kullanıcı ile giriş yapıldı.");
    setUser(testKullanici);
  }, []);

  // --- 2. VERİ ÇEKME TETİKLEYİCİSİ ---
  useEffect(() => {
    if (user) {
      fetchDiseaseInfo();
      fetchFamilyTree();
    }
  }, [user]);

  // --- 3. RİSK ANALİZİ (GÜNCELLENMİŞ TEST VERİSİ) ---
  const fetchDiseaseInfo = async () => {
    setYukleniyorAI(true);
    
    setTimeout(() => {
        const testRiskVerileri = [
            {
                hastalik_adi: "Kistik Fibrozis (Test Verisi)",
                kalitim_sekli: "Otozomal Çekinik",
                durum: "Taşıyıcı",
                risk_seviyesi: "Orta",
                gecme_olasiligi: "%25",
                bilgi_icerigi: "Bu genetik varyasyon, akciğer ve sindirim sistemini etkileyebilir.",
                gecis_kaynagi: "Anne Tarafı",
                // Yeni Eklenen Detaylar
                onerilen_bolum: "Tıbbi Genetik ve Göğüs Hastalıkları",
                detayli_aciklama: "Kistik fibrozis taşıyıcılığı tespit edilmiştir. Klinik belirti göstermeseniz bile, çocuk sahibi olmadan önce genetik danışmanlık almanız önerilir."
            },
            {
                hastalik_adi: "Akdeniz Anemisi",
                kalitim_sekli: "Otozomal Çekinik",
                durum: "Risk Yok",
                risk_seviyesi: "Düşük",
                gecme_olasiligi: "%0",
                bilgi_icerigi: "Genetik taramada herhangi bir risk faktörüne rastlanmamıştır.",
                gecis_kaynagi: null,
                // Yeni Eklenen Detaylar
                onerilen_bolum: "Hematoloji (Kan Hastalıkları)",
                detayli_aciklama: "Yapılan analizlerde beta talasemi (akdeniz anemisi) ile ilgili riskli bir gen dizilimine rastlanmamıştır."
            }
        ];
        
        setHastalikBilgileri(testRiskVerileri);
        setYukleniyorAI(false);
    }, 1000);
  };

  // --- 4. SOY AĞACI (TEST VERİSİ) ---
  const fetchFamilyTree = async () => {
    setYukleniyorAgac(true);

    setTimeout(() => {
        const testSoyAgaci = {
            gelecek_kusak: {
                ebeveynler: [
                    { isim: user?.isim || "Baba", rol: "Baba", tc: user?.kendi_tc, durum: "Sağlıklı", cinsiyet: "Erkek" },
                    { isim: "Eş (Simülasyon)", rol: "Anne", tc: "Temsili", durum: "Taşıyıcı", cinsiyet: "Kadın" }
                ],
                cocuklar: [
                    { 
                        id: 1, 
                        isim: "1. Çocuk (Simülasyon)", 
                        tc_no: "99988877766", 
                        risk_orani: "%25", 
                        durum: "Hasta", 
                        aciklama: "Kistik fibrozis riski yüksek.", 
                        cinsiyet: "Erkek" 
                    },
                    { 
                        id: 2, 
                        isim: "2. Çocuk (Simülasyon)", 
                        tc_no: "Simülasyon", 
                        risk_orani: "%50", 
                        durum: "Taşıyıcı", 
                        aciklama: "Hastalık belirtisi yok ancak gen taşıyor.", 
                        cinsiyet: "Kadın" 
                    },
                    { 
                        id: 3, 
                        isim: "3. Çocuk (Simülasyon)", 
                        tc_no: "Simülasyon", 
                        risk_orani: "%25", 
                        durum: "Sağlıklı", 
                        aciklama: "Tamamen sağlıklı gen dizilimi.", 
                        cinsiyet: "Erkek" 
                    }
                ]
            },
            gecmis_kusaklar: [
                {
                    baslik: "1. Kuşak (Dedeler)",
                    bireyler: [
                        { id: "g1", isim: "Büyükbaba", rol: "Dede", tc: "111", durum: "Sağlıklı", cinsiyet: "Erkek" },
                        { id: "g2", isim: "Büyükanne", rol: "Nine", tc: "222", durum: "Taşıyıcı", cinsiyet: "Kadın" }
                    ]
                }
            ]
        };

        setSoyAgaci(testSoyAgaci);
        setYukleniyorAgac(false);
    }, 1000);
  };

  // --- HELPER FONKSİYONLAR ---
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

  const handlePhotoUpdate = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Lütfen bir resim dosyası seçin.');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => {
      const photo = reader.result as string;
      setUser((prev: any) => ({ ...prev, profilePhoto: photo }));
    };
    reader.readAsDataURL(file);
  };

  if (!user) return <div className="d-flex justify-content-center align-items-center vh-100"><div className="spinner-border text-primary"></div></div>;

  return (
    <div className="container-fluid py-5">
        <div className="row justify-content-center">
            <div className="col-lg-10 col-xl-10">
                
                {/* ÜST BİLGİ */}
                <div className="modern-card animate-fade-in mb-4 d-flex justify-content-between align-items-center">
                    <div className="d-flex align-items-center">
                        <div className="avatar-circle me-3">
                            {user.profilePhoto ? (
                                <img src={user.profilePhoto} alt="Profil fotoğrafı" />
                            ) : (
                                <span className="avatar-initial">{user.isim?.[0]?.toUpperCase() || 'K'}</span>
                            )}
                        </div>
                        <div>
                            <h2 className="mb-0" style={{color: 'var(--primary-color)', fontWeight: 700}}>Merhaba, {user.isim}!</h2>
                            <p className="text-muted mb-0">Genetik analiz panelindesin (TEST MODU).</p>
                            <label className="btn btn-sm btn-outline-primary mt-2">
                                <i className="bi bi-camera-fill me-2"></i> Fotoğrafı Güncelle
                                <input type="file" accept="image/*" className="d-none" onChange={handlePhotoUpdate} />
                            </label>
                        </div>
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
                                    <p className="small text-muted mb-3"><i className="bi bi-info-circle me-1"></i> Detaylı bilgi ve hastane önerisi için risk kutucuklarına tıklayınız.</p>
                                    
                                    {hastalikBilgileri.map((risk, index) => (
                                        <div 
                                            key={index} 
                                            className="hastalik-item mb-3 p-3 border rounded position-relative shadow-sm-hover" 
                                            style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                                            onClick={() => setSelectedRisk(risk)}
                                        >
                                            {risk.gecis_kaynagi && (
                                                <div className="position-absolute top-0 start-0 bg-primary text-white px-2 py-1 rounded-bottom-end" style={{ fontSize: '0.75rem', zIndex: 10 }}>
                                                    <i className="bi bi-arrow-down-right me-1"></i>
                                                    {risk.gecis_kaynagi}
                                                </div>
                                            )}
                                            <div className="d-flex justify-content-between align-items-center mb-2" style={{ marginTop: risk.gecis_kaynagi ? '1.5rem' : '0' }}>
                                                <strong className="h5 mb-0 text-primary">{risk.hastalik_adi}</strong>
                                                <div>
                                                    <span className="badge bg-secondary me-2">{risk.kalitim_sekli}</span>
                                                    <span className={`badge ${risk.durum === 'Risk Yok' ? 'bg-success' : risk.durum === 'Taşıyıcı' ? 'bg-warning text-dark' : 'bg-danger'}`}>
                                                        <i className="bi bi-activity me-1"></i>
                                                        {risk.durum}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="mt-2">
                                                <p className="mb-0 text-muted">
                                                    {risk.bilgi_icerigi}
                                                </p>
                                            </div>
                                            <div className="text-end mt-2">
                                                <span className="btn btn-sm btn-link text-decoration-none p-0">Detayları Gör <i className="bi bi-chevron-right"></i></span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-4">
                                    <div className="alert alert-warning">
                                        <i className="bi bi-exclamation-triangle-fill me-2"></i>
                                        <strong>Risk analizi bulunamadı.</strong>
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
                                        !showChildren && <div className="text-center py-4"><p className="text-muted">Geçmiş kuşak verisi bulunamadı.</p></div>
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
                                                <div style={{position: 'absolute', top: '20px', left: '25%', right: '25%', height: '2px', background: '#cbd5e0'}}></div>
                                                <div style={{position: 'absolute', top: '20px', left: '50%', transform: 'translateX(-50%)', width: '10px', height: '10px', background: '#667eea', borderRadius: '50%'}}></div>
                                            </div>

                                            {/* Çocuklar */}
                                            <div className="d-flex justify-content-center gap-4 flex-wrap">
                                                {soyAgaci.gelecek_kusak.cocuklar.map((cocuk: any) => (
                                                    <div key={cocuk.id} className="tree-node-card p-3 shadow-sm text-center animate-fade-in delay-1" style={{background: 'white', borderRadius: '15px', minWidth: '200px', borderBottom: getCardBorder(cocuk.durum)}}>
                                                        <div className="mb-2">{cocuk.cinsiyet === 'Erkek' ? <i className="bi bi-gender-male fs-4 text-primary"></i> : <i className="bi bi-gender-female fs-4 text-danger"></i>}</div>
                                                        <div className="fw-bold text-dark">{cocuk.isim}</div>
                                                        <div className="small text-primary fw-bold mb-1" style={{fontSize: '0.8rem'}}>TC: {cocuk.tc_no || cocuk.tc || 'Simülasyon'}</div>
                                                        <div className="badge bg-light text-dark border mb-2">Risk: {cocuk.risk_orani}</div>
                                                        <div>{getStatusBadge(cocuk.durum)}</div>
                                                        <div className="small text-muted mt-2 fst-italic" style={{fontSize: '0.85em'}}>{cocuk.aciklama}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ) : (
                                        showChildren && <div className="text-center py-4"><p className="text-muted">Gelecek kuşak verisi bulunamadı.</p></div>
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

                {/* --- POP-UP (MODAL) BİLEŞENİ --- */}
                {selectedRisk && (
                    <div className="modal-backdrop fade show" style={{ backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1050 }}></div>
                )}
                
                {selectedRisk && (
                    <div className="modal fade show d-block" tabIndex={-1} style={{ zIndex: 1055 }}>
                        <div className="modal-dialog modal-dialog-centered">
                            <div className="modal-content border-0 shadow-lg" style={{ borderRadius: '15px' }}>
                                <div className={`modal-header text-white ${selectedRisk.durum === 'Risk Yok' ? 'bg-success' : selectedRisk.durum === 'Taşıyıcı' ? 'bg-warning' : 'bg-danger'}`} style={{ borderRadius: '15px 15px 0 0' }}>
                                    <h5 className="modal-title fw-bold">
                                        {selectedRisk.durum === 'Risk Yok' ? <i className="bi bi-shield-check me-2"></i> : <i className="bi bi-exclamation-triangle-fill me-2"></i>}
                                        {selectedRisk.hastalik_adi}
                                    </h5>
                                    <button type="button" className="btn-close btn-close-white" onClick={() => setSelectedRisk(null)}></button>
                                </div>
                                <div className="modal-body p-4">
                                    <div className="mb-4">
                                        <h6 className="fw-bold text-muted text-uppercase small">Hastalık / Durum Hakkında</h6>
                                        <p className="fs-6">{selectedRisk.detayli_aciklama || selectedRisk.bilgi_icerigi}</p>
                                    </div>
                                    
                                    <div className="p-3 bg-light rounded border-start border-4 border-primary">
                                        <h6 className="fw-bold text-primary mb-2">
                                            <i className="bi bi-hospital-fill me-2"></i>
                                            Önerilen Hastane Bölümü
                                        </h6>
                                        <p className="mb-0 fw-bold text-dark">
                                            {selectedRisk.onerilen_bolum || "Tıbbi Genetik Bölümü"}
                                        </p>
                                        <small className="text-muted d-block mt-1">
                                            Randevu alırken bu bölümü tercih etmeniz önerilir.
                                        </small>
                                    </div>
                                </div>
                                <div className="modal-footer border-0">
                                    <button type="button" className="btn btn-secondary rounded-pill px-4" onClick={() => setSelectedRisk(null)}>Kapat</button>
                                    <button type="button" className="btn btn-primary rounded-pill px-4">
                                        <i className="bi bi-calendar-check me-2"></i>Randevu Ara
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </div>
        </div>
    </div>
  );
}