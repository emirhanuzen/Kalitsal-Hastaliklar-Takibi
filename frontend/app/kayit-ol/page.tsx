// app/kayit-ol/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function KayitSayfasi() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [isChildAccount, setIsChildAccount] = useState(false);
  const [parentTc, setParentTc] = useState<string | null>(null);
  const [childTc, setChildTc] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    isim: '', soyad: '', cinsiyet: '', dogum_tarihi: '',
    kendi_tc: '', email: '', password: '', ebeveyn_tc: ''
  });
  const [profilePhoto, setProfilePhoto] = useState<string | null>(null);

  // Check URL parameters for Scenario 2 (Child Account Creation)
  useEffect(() => {
    try {
      const parent_tc = searchParams?.get('parent_tc');
      const ebeveyn_tc = searchParams?.get('ebeveyn_tc');
      const child_tc = searchParams?.get('child_tc');
      const tc = searchParams?.get('tc');
      
      // Support both parent_tc and ebeveyn_tc for backward compatibility
      const parentTcValue = parent_tc || ebeveyn_tc;
      const childTcValue = child_tc || tc;
      
      if (parentTcValue) {
        setIsChildAccount(true);
        setParentTc(parentTcValue);
        // Pre-fill ebeveyn_tc in form data
        setFormData(prev => ({ ...prev, ebeveyn_tc: parentTcValue }));
      }
      
      if (childTcValue) {
        setChildTc(childTcValue);
        // Pre-fill child's TC if provided
        setFormData(prev => ({ ...prev, kendi_tc: childTcValue }));
      }
    } catch (error) {
      console.error('Error reading URL parameters:', error);
    }
  }, [searchParams]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    if (name === 'kendi_tc' || name === 'ebeveyn_tc') {
        setFormData(prev => ({ ...prev, [name]: value.replace(/[^0-9]/g, '') }));
    } else {
        setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Lütfen bir resim dosyası seçin.');
      return;
    }
    const reader = new FileReader();
    reader.onloadend = () => setProfilePhoto(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.kendi_tc.length !== 11) {
      alert('TC kimlik numarası 11 haneli olmalıdır!');
      return;
    }

    // Validate parent TC if it's a child account
    if (isChildAccount && formData.ebeveyn_tc && formData.ebeveyn_tc.length !== 11) {
      alert('Ebeveyn TC kimlik numarası 11 haneli olmalıdır!');
      return;
    }

    setLoading(true);
    try {
      // Prepare payload - ensure ebeveyn_tc is included if it's a child account
      const payload: any = { ...formData };
      
      // If it's a child account, ensure ebeveyn_tc is sent (even if empty, backend will handle it)
      if (isChildAccount && parentTc) {
        payload.ebeveyn_tc = parentTc;
      }
      
      // Remove ebeveyn_tc if it's empty and not a child account (Scenario 1)
      if (!isChildAccount && !payload.ebeveyn_tc) {
        payload.ebeveyn_tc = '';
      }
      
      const response = await fetch('/api/register', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload), 
      });

      const data = await response.json();

      if (response.ok) {
        const userFromApi = data.user;
        const userWithPhoto = profilePhoto ? { ...userFromApi, profilePhoto } : userFromApi;

        // Fotoğrafı TC ile eşleştirip localStorage'da sakla ki girişte geri yüklenebilsin
        if (profilePhoto && userFromApi?.kurgusal_tc) {
          const storedPhotos = JSON.parse(localStorage.getItem('userPhotos') || '{}');
          storedPhotos[userFromApi.kurgusal_tc] = profilePhoto;
          localStorage.setItem('userPhotos', JSON.stringify(storedPhotos));
        }

        // Kayıt başarılı, kullanıcıyı giriş sayfasına yönlendir
        alert('Kayıt Başarılı! Lütfen giriş yapın.'); 
        router.push('/'); 
      } else {
        alert('Hata: ' + (data.mesaj || 'Kayıt yapılamadı.'));
      }
    } catch (error) {
      console.error('Kayıt hatası:', error);
      alert('Sunucu hatası.');
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="container d-flex align-items-center justify-content-center min-vh-100 py-5">
      <div className="modern-card animate-fade-in" style={{maxWidth: '800px'}}>
        <h2 className="header-title mb-4">
            <i className="bi bi-person-plus-fill me-2"></i> 
            {isChildAccount ? 'Çocuk Hesabı Kaydı' : 'Yeni Kullanıcı Kaydı'}
        </h2>

        {/* Child Account Info Banner */}
        {isChildAccount && parentTc && (
          <div className="alert alert-info d-flex align-items-center mb-4" role="alert">
            <i className="bi bi-info-circle-fill me-2 fs-5"></i>
            <div>
              <strong>Çocuk Hesabı Kaydı</strong>
              <br />
              <small>Ebeveyn TC: <code>{parentTc}</code></small>
              {childTc && (
                <>
                  <br />
                  <small>Çocuk TC: <code>{childTc}</code></small>
                </>
              )}
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
            <div className="row mb-3">
                <div className="col-md-6 mb-3">
                    <label className="form-label">İsim <span className="text-danger">*</span></label>
                    <input type="text" className="form-control" name="isim" required placeholder="Adınız" value={formData.isim} onChange={handleChange} />
                </div>
                <div className="col-md-6 mb-3">
                    <label className="form-label">Soyad <span className="text-danger">*</span></label>
                    <input type="text" className="form-control" name="soyad" required placeholder="Soyadınız" value={formData.soyad} onChange={handleChange} />
                </div>
            </div>
            
            <div className="row mb-3">
                <div className="col-md-6 mb-3">
                    <label className="form-label">Cinsiyet <span className="text-danger">*</span></label>
                    <select className="form-select" name="cinsiyet" required value={formData.cinsiyet} onChange={handleChange}>
                        <option value="">Seçiniz</option>
                        <option value="Erkek">Erkek</option>
                        <option value="Kadın">Kadın</option>
                    </select>
                </div>
                <div className="col-md-6 mb-3">
                    <label className="form-label">Doğum Tarihi <span className="text-danger">*</span></label>
                    <input type="date" className="form-control" name="dogum_tarihi" required value={formData.dogum_tarihi} onChange={handleChange} />
                </div>
            </div>

            <div className="mb-4">
                <label className="form-label">
                    {isChildAccount ? 'Çocuk TC Kimlik No' : 'TC Kimlik No'} (11 Hane) <span className="text-danger">*</span>
                </label>
                <input 
                    type="text" 
                    className="form-control" 
                    name="kendi_tc" 
                    required 
                    maxLength={11} 
                    placeholder="11122233344" 
                    value={formData.kendi_tc} 
                    onChange={handleChange}
                    readOnly={!!childTc}  // Read-only if pre-filled from URL
                />
                {isChildAccount && (
                    <small className="form-text text-muted">
                        Bu TC, simülasyon sonucunda oluşturulan çocuk TC'sidir.
                    </small>
                )}
            </div>

            {/* Ebeveyn TC Field - Show only for child accounts or if manually entered */}
            {(isChildAccount || formData.ebeveyn_tc) && (
                <div className="mb-4">
                    <label className="form-label">Ebeveyn TC Kimlik No (11 Hane) <span className="text-danger">*</span></label>
                    <input 
                        type="text" 
                        className="form-control" 
                        name="ebeveyn_tc" 
                        required={isChildAccount}
                        maxLength={11} 
                        placeholder="Ebeveyn TC'si" 
                        value={formData.ebeveyn_tc} 
                        onChange={handleChange}
                        readOnly={isChildAccount && !!parentTc}  // Read-only if from URL
                    />
                    {isChildAccount && (
                        <small className="form-text text-muted">
                            Bu TC, hesabınızın bağlı olduğu ebeveyn hesabının TC'sidir.
                        </small>
                    )}
                </div>
            )}

            <div className="mb-4">
                <label className="form-label">Profil Fotoğrafı (isteğe bağlı)</label>
                <div className="d-flex align-items-center gap-3">
                    <div className="avatar-circle preview">
                        {profilePhoto ? (
                            <img src={profilePhoto} alt="Profil önizleme" />
                        ) : (
                            <span className="avatar-initial">{formData.isim?.[0]?.toUpperCase() || '✚'}</span>
                        )}
                    </div>
                    <input type="file" accept="image/*" className="form-control" onChange={handlePhotoChange} />
                </div>
            </div>

            <h5 className="section-title mt-4 mb-3 text-secondary pb-2 border-bottom">Hesap Bilgileri</h5>
            
            <div className="mb-3">
                <label className="form-label">E-posta <span className="text-danger">*</span></label>
                <input type="email" className="form-control" name="email" required placeholder="ornek@email.com" value={formData.email} onChange={handleChange} />
            </div>
            <div className="mb-4">
                <label className="form-label">Şifre <span className="text-danger">*</span></label>
                <input type="password" className="form-control" name="password" required placeholder="Güvenli bir şifre girin" value={formData.password} onChange={handleChange} />
            </div>

            <div className="d-flex justify-content-between align-items-center mt-5">
                <a href="/" className="btn btn-link text-decoration-none text-secondary">
                    <i className="bi bi-arrow-left me-2"></i> Geri Dön
                </a>
                <button type="submit" className="btn-primary-custom w-auto px-5" disabled={loading}>
                    {loading ? 'Kaydediliyor...' : 'Kayıt Ol'}
                </button>
            </div>
        </form>
      </div>
    </div>
  );
}