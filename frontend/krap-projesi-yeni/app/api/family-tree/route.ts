// app/api/family-tree/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  await new Promise(resolve => setTimeout(resolve, 1000));

  const soyAgaci = {
    // MEVCUT SOY AĞACI (GEÇMİŞ)
    gecmis_kusaklar: [
      {
        seviye: 1,
        baslik: "1. Kuşak (Büyük Ebeveynler)",
        bireyler: [
          // Baba Tarafı (Soyad: Sümen)
          { id: 1, isim: "Sultan Sümen", rol: "Babaanne", durum: "Taşıyıcı", cinsiyet: "Kadın" },
          { id: 2, isim: "Osman Sümen", rol: "Dede (Baba)", durum: "Sağlıklı", cinsiyet: "Erkek" },
          
          // Anne Tarafı (Soyad: Öztürk - Farklı olsun ki karışmasın)
          { id: 3, isim: "Fatma Öztürk", rol: "Anneanne", durum: "Sağlıklı", cinsiyet: "Kadın" },
          { id: 4, isim: "Mehmet Öztürk", rol: "Dede (Anne)", durum: "Hasta", cinsiyet: "Erkek" }
        ]
      },
      {
        seviye: 2,
        baslik: "2. Kuşak (Ebeveynler)",
        bireyler: [
          // Baban senin soyadını taşır
          { id: 5, isim: "Ali Sümen", rol: "Baba", durum: "Taşıyıcı", cinsiyet: "Erkek", ebeveynler: [1, 2] },
          // Annen evlenince soyadı değişmiş olsun
          { id: 6, isim: "Ayşe Sümen", rol: "Anne", durum: "Taşıyıcı", cinsiyet: "Kadın", ebeveynler: [3, 4] }
        ]
      },
      {
        seviye: 3,
        baslik: "3. Kuşak (Siz)",
        bireyler: [
          // Sen
          { id: 7, isim: "Muhammet Sümen", rol: "Kendisi", durum: "Riskli", cinsiyet: "Erkek", ebeveynler: [5, 6] } 
        ]
      }
    ],

    // GELECEK SİMÜLASYONU (ÇOCUKLARIM)
    gelecek_kusak: {
      ebeveynler: [
        { isim: "Muhammet Sümen", rol: "Baba (Siz)", durum: "Riskli (Taşıyıcı)", cinsiyet: "Erkek" },
        { isim: "Nursena Sümen", rol: "Anne (Eş)", durum: "Taşıyıcı", cinsiyet: "Kadın" }
      ],
      cocuklar: [
        { id: 101, isim: "Ahmet (Olasılık)", cinsiyet: "Erkek", durum: "Hasta", risk_orani: "%25", aciklama: "Her iki ebeveynden hatalı gen aktarımı riski." },
        { id: 102, isim: "Zeynep (Olasılık)", cinsiyet: "Kadın", durum: "Taşıyıcı", risk_orani: "%50", aciklama: "Tek bir ebeveynden hatalı gen aktarımı riski." },
        { id: 103, isim: "Yusuf (Olasılık)", cinsiyet: "Erkek", durum: "Sağlıklı", risk_orani: "%25", aciklama: "Sağlıklı gen aktarımı şansı." }
      ]
    }
  };

  return NextResponse.json({
    basarili: true,
    data: soyAgaci
  }, { status: 200 });
}