# KRAP Frontend - Next.js

Bu klasör, KRAP (Kalıtsal Risk Analiz Platformu) projesinin Next.js frontend uygulamasını içerir.

## Kurulum

1. Bağımlılıkları yükleyin:
```bash
cd frontend
npm install
```

2. Flask backend'in çalıştığından emin olun (varsayılan: http://localhost:5000)

3. Frontend'i başlatın:
```bash
npm run dev
```

Frontend uygulaması http://localhost:3000 adresinde çalışacaktır.

## Yapı

- `app/` - Next.js App Router sayfaları ve route'ları
  - `api/` - API route'ları (Flask backend'e proxy yapar)
  - `page.tsx` - Ana giriş sayfası
  - `kayit-ol/page.tsx` - Kayıt sayfası
  - `profil/page.tsx` - Kullanıcı profil sayfası
- `public/` - Statik dosyalar
- `globals.css` - Global stiller

## API Entegrasyonu

Frontend, Flask backend'e proxy yapan Next.js API route'ları kullanır:
- `/api/login` → Flask `/api/login`
- `/api/register` → Flask `/api/register`
- `/api/hastalik-bilgileri` → Flask `/api/hastalik-bilgileri`
- `/api/family-tree` → Flask `/api/family-tree`

Backend URL'i `next.config.ts` dosyasında veya `FLASK_BACKEND_URL` environment variable ile ayarlanabilir.

## Geliştirme

```bash
# Development server
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint

# Formatting
npm run format
```
