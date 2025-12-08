// app/api/family-tree/route.ts
import { NextResponse } from 'next/server';

const FLASK_BACKEND_URL = process.env.FLASK_BACKEND_URL || 'http://localhost:5000';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const user_id = searchParams.get('user_id');
    const family_tree_id = searchParams.get('family_tree_id');
    
    // Query parametrelerini hazırla
    const params = new URLSearchParams();
    if (user_id) params.append('user_id', user_id);
    if (family_tree_id) params.append('family_tree_id', family_tree_id);
    
    // Flask backend'e proxy yap
    const response = await fetch(`${FLASK_BACKEND_URL}/api/family-tree?${params.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });

  } catch (error) {
    console.error('Family tree API hatası:', error);
    return NextResponse.json({ 
      basarili: false, 
      mesaj: 'Sunucuya bağlanılamadı. Flask backend çalışıyor mu?' 
    }, { status: 500 });
  }
}