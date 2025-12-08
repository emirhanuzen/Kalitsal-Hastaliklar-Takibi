// app/api/login/route.ts
import { NextResponse } from 'next/server';

const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Flask backend'e proxy yap
    const response = await fetch(`${FLASK_BACKEND_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });

  } catch (error) {
    console.error('Login API hatası:', error);
    return NextResponse.json({ 
      durum: 'hata', 
      mesaj: 'Sunucuya bağlanılamadı. Flask backend çalışıyor mu?' 
    }, { status: 500 });
  }
}