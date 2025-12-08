// app/api/hastalik-bilgileri/route.ts
import { NextResponse } from 'next/server';

const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Flask backend'e proxy yap
    const response = await fetch(`${FLASK_BACKEND_URL}/api/hastalik-bilgileri`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });

  } catch (error) {
    console.error('Hastalık bilgileri API hatası:', error);
    return NextResponse.json({ 
      basarili: false, 
      mesaj: 'Sunucuya bağlanılamadı. Flask backend çalışıyor mu?' 
    }, { status: 500 });
  }
}