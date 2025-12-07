// app/profil/page.tsx
"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ProfilSayfasi() {
  const router = useRouter();
  
  const [user, setUser] = useState<any>(null);
  const [hastalikBilgileri, setHastalikBilgileri] = useState<any[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  // --- 1. Kullanıcıyı ve Hastalık Verilerini Yükle ---
  useEffect(() => {
    const savedUserString = localStorage.getItem('currentUser');
    
    if (savedUserString) {
      setUser(JSON.parse(savedUserString));
      fetchDiseaseInfo(); // Kullanıcı varsa AI servisini çağır
    } else {
      router.push('/');
    }
  }, []);

  // --- 2. API'den Veri Çekme (Yapay Zeka Simülasyonu) ---
  const fetchDiseaseInfo = async () => {
    try {
      setYukleniyor(true);
      // Mock AI servisine istek atıyoruz
      const response = await fetch('/api/hastalik-bilgileri', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ test: 'veri' }) 
      });
      const data = await response.json();
      
      if (data.basarili) {
        setHastalikBilgileri(data.hastalik_bilgileri);
      }
    } catch (error) {
      console.error("Veri çekilemedi:", error);
    } finally {
      setYukleniyor(false);
    }
  };

  if (!user) return <div className="d-flex justify-content-center align-items-center vh-100"><div className="spinner-border text-primary"></div></div>;

  return (
    <div className="container-fluid py-5">
        <div className="row justify-content-center">
            <div className="col-lg-10 col-xl-9">
                
                {/* 1. KART: Profil Bilgileri (Animasyonlu) */}
                <div className="modern-card animate-fade-in mb-4">
                    <h2 className="header-title text-start mb-4">
                        <i className="bi bi-person-circle me-2"></i> Profil Bilgileri
                    </h2>
                    
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <div className="info-card">
                                <div className="info-label"><i className="bi bi-person-fill me-2"></i> İsim Soyad</div>
                                <div className="info-value text-uppercase">{user.isim} {user.soyad}</div>
                            </div>
                        </div>
                        <div className="col-md-6 mb-3">
                            <div className="info-card">
                                <div className="info-label"><i className="bi bi-envelope-fill me-2"></i> E-posta</div>
                                <div className="info-value">{user.email}</div>
                            </div>
                        </div>
                        <div className="col-md-6 mb-3">
                            <div className="info-card">
                                <div className="info-label"><i className="bi bi-calendar-event me-2"></i> Doğum Tarihi</div>
                                <div className="info-value">{user.dogum_tarihi}</div>
                            </div>
                        </div>
                        <div className="col-md-6 mb-3">
                            <div className="info-card">
                                <div className="info-label"><i className="bi bi-credit-card me-2"></i> Kurgusal TC</div>
                                <div className="info-value">{user.kurgusal_tc || user.kendi_tc}</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. KART: Yapay Zeka Risk Analizi (Gecikmeli Animasyon: delay-1) */}
                <div className="modern-card animate-fade-in delay-1 mb-4">
                    <h3 className="header-title text-start mb-3">
                        <i className="bi bi-robot me-2 text-accent"></i> Yapay Zeka Risk Analizi
                    </h3>
                    
                    {yukleniyor ? (
                        <div className="text-center py-5">
                            <div className="spinner-border text-primary" style={{width: '3rem', height: '3rem'}} role="status"></div>
                            <p className="mt-3 text-muted">Genetik verileriniz Gemini AI tarafından analiz ediliyor...</p>
                        </div>
                    ) : (
                        <div>
                            <p className="text-muted mb-4">
                                Aşağıdaki rapor, soy ağacı verileriniz üzerinden yapay zeka destekli olarak oluşturulmuştur.
                            </p>
                            
                            {hastalikBilgileri.map((risk, index) => (
                                <div key={index} className="hastalik-item">
                                    <div className="d-flex justify-content-between align-items-center mb-2">
                                        <div>
                                            <strong className="h5 me-2" style={{color: '#4a5568'}}>{risk.hastalik_adi}</strong>
                                            <span className="badge bg-secondary">{risk.kalitim_sekli}</span>
                                        </div>
                                        <div>
                                            {risk.risk_seviyesi === "Yüksek" && <span className="node-badge" style={{background: '#dc3545', color:'white'}}>Yüksek Risk</span>}
                                            {risk.risk_seviyesi === "Orta" && <span className="node-badge" style={{background: '#fd7e14', color:'white'}}>Orta Risk</span>}
                                            {risk.risk_seviyesi === "Düşük" && <span className="node-badge" style={{background: '#28a745', color:'white'}}>Düşük Risk</span>}
                                        </div>
                                    </div>
                                    
                                    <div className="alert alert-light border-0 bg-light mt-2 mb-0 py-3">
                                        <i className="bi bi-info-circle-fill me-2 text-primary"></i> 
                                        {risk.bilgi_icerigi}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Çıkış Butonu */}
                <div className="text-center mt-5 mb-5 animate-fade-in delay-2">
                    <button 
                        onClick={() => { localStorage.removeItem('currentUser'); router.push('/'); }}
                        className="btn btn-outline-danger px-5 py-2 rounded-pill fw-bold">
                        <i className="bi bi-box-arrow-right me-2"></i> Oturumu Kapat
                    </button>
                </div>

            </div>
        </div>
    </div>
  );
}