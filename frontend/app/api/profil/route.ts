// app/api/profil/route.ts
import { NextResponse } from 'next/server';

const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const user_id = searchParams.get('user_id');
    
    if (!user_id) {
      return NextResponse.json({ 
        durum: 'hata', 
        mesaj: 'user_id parametresi gerekli.' 
      }, { status: 400 });
    }
    
    // Flask backend'e proxy yap
    const response = await fetch(`${FLASK_BACKEND_URL}/api/profil?user_id=${user_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });

  } catch (error) {
    console.error('Profil API hatası:', error);
    return NextResponse.json({ 
      durum: 'hata', 
      mesaj: 'Sunucuya bağlanılamadı. Flask backend çalışıyor mu?' 
    }, { status: 500 });
  }
}

