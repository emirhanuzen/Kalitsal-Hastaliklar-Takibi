// app/api/register/route.ts
import { NextResponse } from 'next/server';

const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Flask backend'e proxy yap
    const response = await fetch(`${FLASK_BACKEND_URL}/api/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    
    // Flask'tan gelen response'u frontend formatına uyarla
    if (response.ok && data.durum === 'basarili') {
      return NextResponse.json({
        durum: 'basarili',
        mesaj: data.mesaj || 'Kayıt işlemi başarılı',
        user: {
          birey_id: data.UserID,
          user_id: data.UserID,
          isim: body.isim,
          soyad: body.soyad,
          email: body.email,
          kurgusal_tc: body.kendi_tc,
          dogum_tarihi: body.dogum_tarihi,
          family_tree_id: data.FamilyTreeID_Mongo ? String(data.FamilyTreeID_Mongo) : null,
          birey_id_mongo: data.BireyID_Mongo ? String(data.BireyID_Mongo) : null
        }
      }, { status: 201 });
    }
    
    return NextResponse.json(data, { status: response.status });

  } catch (error) {
    console.error('Register API hatası:', error);
    return NextResponse.json({ 
      durum: 'hata', 
      mesaj: 'Sunucuya bağlanılamadı. Flask backend çalışıyor mu?' 
    }, { status: 500 });
  }
}