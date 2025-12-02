// static/js/main.js
// GEÇİCİ / DEBUG AMAÇLI "Çocuklarım" özelliği

// API /register_user cevabında dönen ID'leri tarayıcıya yazmak için
// dışarıdan çağrılabilen yardımcı fonksiyon.
// Örnek kullanım: handleRegisterSuccess(apiResponseJson);
window.handleRegisterSuccess = function (result) {
    try {
        if (result.FamilyTreeID) {
            localStorage.setItem('family_tree_id', result.FamilyTreeID);
        }
        if (result.BireyID_Mongo) {
            localStorage.setItem('user_birey_id', result.BireyID_Mongo);
        }
    } catch (e) {
        console.warn('handleRegisterSuccess -> localStorage yazılamadı:', e);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('cocuklarimiGetirBtn');
    const liste = document.getElementById('cocuklarListesi');

    if (!btn || !liste) {
        return; // Bu sayfada ilgili alan yok
    }

    btn.addEventListener('click', async () => {
        // Önce listeyi temizle
        liste.innerHTML = '';

        // Kayıt / profil sürecinde tarayıcıya kaydedildiği varsayılan ID'ler
        const familyTreeId = localStorage.getItem('family_tree_id');
        const parentBireyId = localStorage.getItem('user_birey_id');

        if (!familyTreeId || !parentBireyId) {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-warning';
            li.textContent = 'family_tree_id veya user_birey_id tarayıcıda bulunamadı. (DEBUG: Lütfen kayıt sonrasında bu değerleri localStorage\'a yazın.)';
            liste.appendChild(li);
            return;
        }

        try {
            const params = new URLSearchParams({
                family_tree_id: familyTreeId,
                parent_birey_id: parentBireyId
            });
            const response = await fetch(`/api/get-my-children?${params.toString()}`);

            if (!response.ok) {
                const li = document.createElement('li');
                li.className = 'list-group-item list-group-item-danger';
                li.textContent = `Sunucu hatası: ${response.status}`;
                liste.appendChild(li);
                return;
            }

            const data = await response.json();

            if (data.durum !== 'basarili') {
                const li = document.createElement('li');
                li.className = 'list-group-item list-group-item-danger';
                li.textContent = data.mesaj || 'Bilinmeyen bir hata oluştu.';
                liste.appendChild(li);
                return;
            }

            if (!data.cocuklar || data.cocuklar.length === 0) {
                const li = document.createElement('li');
                li.className = 'list-group-item list-group-item-info';
                li.textContent = 'Bu kullanıcıya ait çocuk bulunamadı.';
                liste.appendChild(li);
                return;
            }

            data.cocuklar.forEach((cocuk) => {
                const li = document.createElement('li');
                li.className = 'list-group-item';

                const isim = (cocuk.ad_soyad || `${cocuk.isim || ''} ${cocuk.soyad || ''}`).trim() || 'İsimsiz Çocuk';
                const cinsiyet = cocuk.cinsiyet || 'Bilinmiyor';
                const dogumYili = cocuk.dogum_yili || '—';
                const tc = cocuk.kurgusal_tc || '—';

                // Hastalık durumuna göre renk belirle
                let durumText = 'Sağlık durumu bilinmiyor';
                let badgeClass = 'badge bg-secondary';

                const hastaliklar = cocuk.hastaliklar;
                if (typeof hastaliklar === 'string') {
                    if (hastaliklar === 'Sağlıklı') {
                        durumText = 'Sağlıklı';
                        badgeClass = 'badge bg-success';
                    } else {
                        durumText = hastaliklar;
                        badgeClass = 'badge bg-warning text-dark';
                    }
                } else if (Array.isArray(hastaliklar) && hastaliklar.length > 0) {
                    const durumlar = hastaliklar.map(h => h.durum).filter(Boolean);
                    if (durumlar.includes('Hasta')) {
                        durumText = 'Hasta';
                        badgeClass = 'badge bg-danger';
                    } else if (durumlar.includes('Taşıyıcı')) {
                        durumText = 'Taşıyıcı';
                        badgeClass = 'badge bg-warning text-dark';
                    } else {
                        durumText = 'Sağlıklı';
                        badgeClass = 'badge bg-success';
                    }
                }

                const riskNotu = cocuk.risk_analizi || 'Risk bilgisi yok.';

                li.innerHTML = `
                    <div>
                        <div>
                            <strong>${isim}</strong>
                            <span class="text-muted small ms-1">(TC: <span class="child-tc">${tc}</span>)</span>
                            <button type="button" class="btn btn-sm btn-outline-secondary ms-2 copy-tc-btn">
                                Kopyala
                            </button>
                        </div>
                        <div class="text-muted small mt-1">Cinsiyet: ${cinsiyet} • Doğum Yılı: ${dogumYili}</div>
                        <div class="mt-1">
                            <span class="${badgeClass}">Hastalık Durumu: ${durumText}</span>
                        </div>
                        <div class="mt-2 small"><strong>Genetik Risk Notu:</strong> ${riskNotu}</div>
                    </div>
                `;

                const copyBtn = li.querySelector('.copy-tc-btn');
                if (copyBtn) {
                    copyBtn.addEventListener('click', async () => {
                        try {
                            await navigator.clipboard.writeText(tc);
                            copyBtn.textContent = 'Kopyalandı';
                            setTimeout(() => {
                                copyBtn.textContent = 'Kopyala';
                            }, 1500);
                        } catch (e) {
                            alert('TC kopyalanamadı: ' + e);
                        }
                    });
                }

                liste.appendChild(li);
            });
        } catch (err) {
            const li = document.createElement('li');
            li.className = 'list-group-item list-group-item-danger';
            li.textContent = `İstek sırasında hata oluştu: ${err}`;
            liste.appendChild(li);
        }
    });
});


