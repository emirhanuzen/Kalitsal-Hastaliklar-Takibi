// app/api/login/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { kurgusal_tc, password } = body;

    // --- MOCK MANTIK (SAHTE KONTROL) ---
    // Burada istediğin kuralı koyabilirsin.
    // Örneğin: Şifre '123456' ise ve TC 11 haneliyse kabul et.
    
    if (kurgusal_tc.length === 11 && password === '123456') {
      
      // Başarılı giriş senaryosu
      return NextResponse.json({
        durum: 'basarili',
        user: {
          birey_id: 101,
          isim: 'Muhammet',  // İstediğin ismi ver
          soyad: 'Sümen',
          email: 'muhammet@frontend.com',
          kurgusal_tc: kurgusal_tc,
          dogum_tarihi: '1998-05-20',
          role: 'admin'
        }
      }, { status: 200 });

    } else {
      // Hatalı giriş senaryosu
      return NextResponse.json({
        durum: 'hata',
        mesaj: 'Hatalı TC veya Şifre! (Mock API: Şifre 123456 olmalı)'
      }, { status: 401 });
    }

  } catch (error) {
    return NextResponse.json({ durum: 'hata', mesaj: 'Sunucu hatası' }, { status: 500 });
  }
}