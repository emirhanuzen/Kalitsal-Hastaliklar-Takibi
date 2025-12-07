// app/api/register/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // --- MOCK DOĞRULAMA ---
    // Basit bir validasyon yapalım
    if (!body.kendi_tc || body.kendi_tc.length !== 11) {
      return NextResponse.json({
        durum: 'hata',
        mesaj: 'TC Kimlik numarası 11 haneli olmalıdır.'
      }, { status: 400 });
    }

    // --- MOCK KAYIT (SAHTE İŞLEM) ---
    // Frontend'e "Kayıt oldun, işte kullanıcın bu" diyoruz.
    // Frontend bu veriyi alıp localStorage'a yazacak.
    
    const yeniKullanici = {
      ...body, // Formdan gelen tüm verileri (isim, soyad vs.) geri döndür
      // Rastgele bir ID uyduruyoruz (Backend simülasyonu)
      birey_id: Math.floor(Math.random() * 10000), 
      role: 'user',
      kayit_tarihi: new Date().toISOString()
    };

    // Simüle edilmiş gecikme (Gerçekçi hissettirsin diye yarım saniye bekletelim)
    await new Promise(resolve => setTimeout(resolve, 500));

    return NextResponse.json({
      durum: 'basarili',
      mesaj: 'Kayıt işlemi başarılı (Mock)',
      user: yeniKullanici
    }, { status: 201 });

  } catch (error) {
    return NextResponse.json({ durum: 'hata', mesaj: 'Sunucu hatası' }, { status: 500 });
  }
}