// app/page.tsx
"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  
  const [tc, setTc] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/g, '');
    setTc(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (tc.length !== 11) {
      alert('TC kimlik numarası 11 haneli olmalıdır!');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kurgusal_tc: tc, password: password }),
      });

      const data = await response.json();

      if (response.ok) {
        const userFromApi = data.user || data.kullanici;
        const storedPhotos = JSON.parse(localStorage.getItem('userPhotos') || '{}');
        const tcKey = userFromApi?.kurgusal_tc || userFromApi?.kendi_tc;
        const profilePhoto = tcKey ? storedPhotos[tcKey] : undefined;
        const userWithPhoto = profilePhoto ? { ...userFromApi, profilePhoto } : userFromApi;

        localStorage.setItem('currentUser', JSON.stringify(userWithPhoto)); 
        //alert('Giriş başarılı! Yönlendiriliyorsunuz...'); // İstersen bunu açabilirsin
        router.push('/profil');
      } else {
        alert('Giriş Başarısız: ' + (data.mesaj || 'Bilinmeyen hata'));
      }

    } catch (error) {
      console.error('Bağlantı hatası:', error);
      alert('Sunucuya bağlanılamadı!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container d-flex align-items-center justify-content-center min-vh-100">
      <div className="modern-card animate-fade-in" style={{maxWidth: '450px'}}>
        <div className="login-header">
          <h1 className="header-title">
            <i className="bi bi-heart-pulse-fill me-2 icon-red"></i> 
            Kalıtsal Risk Analizi Platformu
          </h1>
          <p className="text-muted">Güvenli giriş yapın</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="kurgusal_tc" className="form-label">
              <i className="bi bi-credit-card me-2"></i> TC Kimlik No
            </label>
            <input
              type="text"
              className="form-control"
              id="kurgusal_tc"
              required
              pattern="[0-9]{11}"
              maxLength={11}
              placeholder="11 haneli numaranız"
              value={tc}
              onChange={handleTcChange}
            />
          </div>

          <div className="mb-4">
            <label htmlFor="password" className="form-label">
              <i className="bi bi-lock-fill me-2"></i> Şifre
            </label>
            <input
              type="password"
              className="form-control"
              id="password"
              required
              placeholder="Şifrenizi girin"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="btn-primary-custom" disabled={loading}>
            {loading ? (
              <span><span className="spinner-border spinner-border-sm me-2"></span>Giriş Yapılıyor...</span>
            ) : (
              <span><i className="bi bi-box-arrow-in-right me-2"></i> Giriş Yap</span>
            )}
          </button>
        </form>

        <div className="divider">
          <span>veya</span>
        </div>

        <a href="/kayit-ol" className="btn-register">
          <i className="bi bi-person-plus-fill me-2"></i> Yeni Hesap Oluştur
        </a>
      </div>
    </div>
  );
}