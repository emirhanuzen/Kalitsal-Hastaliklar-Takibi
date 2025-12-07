// app/api/hastalik-bilgileri/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    // Simülasyon: Yapay zeka düşünüyor... (1.5 saniye bekle)
    await new Promise(resolve => setTimeout(resolve, 1500));

    // --- MOCK AI CEVABI ---
    const yapayZekaCevabi = [
      {
        hastalik_adi: "Kistik Fibrozis", // DÜZELTİLDİ: Tutarlı anahtar ismi
        kalitim_sekli: "Otozomal Resesif",
        durum: "Taşıyıcı",
        risk_seviyesi: "Yüksek",
        bilgi_icerigi: "Genetik analizlere göre bu hastalık için taşıyıcı genlere sahipsiniz. Eşinizin de taşıyıcı olması durumunda çocuklarda %25 hastalık riski oluşabilir. Solunum testleri önerilir."
      },
      {
        hastalik_adi: "Akdeniz Anemisi (Talasemi)", // DÜZELTİLDİ: 'hastalik' yerine 'hastalik_adi' yapıldı
        kalitim_sekli: "Otozomal Resesif",
        durum: "Sağlıklı",
        risk_seviyesi: "Düşük",
        bilgi_icerigi: "Soy ağacınızdaki taramada bu hastalıkla ilgili riskli bir gene rastlanmamıştır. Ancak bölgesel yatkınlık nedeniyle rutin kan sayımı (Hemogram) yaptırmanız faydalı olabilir."
      },
      {
        hastalik_adi: "Fenilketonüri", // DÜZELTİLDİ: 'hastalik' yerine 'hastalik_adi' yapıldı
        kalitim_sekli: "Otozomal Resesif",
        durum: "Riskli",
        risk_seviyesi: "Orta",
        bilgi_icerigi: "Uzak kuşak akrabalarınızda bu hastalığa rastlanmıştır. Doğrudan bir taşıyıcılık tespit edilmese de, genetik danışmanlık almanız önerilir."
      }
    ];

    return NextResponse.json({
      basarili: true,
      hastalik_bilgileri: yapayZekaCevabi
    }, { status: 200 });

  } catch (error) {
    return NextResponse.json({ basarili: false, mesaj: 'AI Servisi Hatası' }, { status: 500 });
  }
}