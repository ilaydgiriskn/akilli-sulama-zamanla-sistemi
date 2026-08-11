document.addEventListener('DOMContentLoaded', () => {
    const parcelListEl = document.getElementById('parcel-list');
    const addParcelForm = document.getElementById('add-parcel-form');
    const activeParcelName = document.getElementById('active-parcel-name');
    const dashboardContent = document.getElementById('dashboard-content');
    const btnCheck = document.getElementById('btn-check');
    const historyList = document.getElementById('history-list');

    let currentParcelId = null;

    // Load Parcels
    function loadParcels() {
        fetch('/api/parcels')
            .then(res => res.json())
            .then(data => {
                parcelListEl.innerHTML = '';
                if(data.length === 0) {
                    parcelListEl.innerHTML = '<li class="empty-state">Henüz parsel yok.</li>';
                    return;
                }
                data.forEach(p => {
                    const li = document.createElement('li');
                    li.className = 'parcel-item';
                    if(p.id === currentParcelId) li.classList.add('active');
                    li.innerHTML = `
                        <div class="parcel-name">${p.name}</div>
                        <div class="parcel-meta">${p.crop_type.toUpperCase()} | Bütçe: ${p.water_budget.toFixed(1)}mm</div>
                    `;
                    li.onclick = () => selectParcel(p);
                    parcelListEl.appendChild(li);
                });
            });
    }

    // Add Parcel
    addParcelForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('p-name').value,
            latitude: document.getElementById('p-lat').value,
            longitude: document.getElementById('p-lon').value,
            crop_type: document.getElementById('p-crop').value
        };

        fetch('/api/parcels', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(res => {
            if(res.success) {
                addParcelForm.reset();
                loadParcels();
            }
        });
    });

    // Check Irrigation Logic
    function runIrrigationCheck(parcelId) {
        const btnOriginalText = btnCheck.innerHTML;
        btnCheck.innerHTML = '<i class="ph ph-spinner ph-spin"></i> İşleniyor...';
        btnCheck.disabled = true;

        // "Sistem Bekleniyor" yazısını "Yapay Zeka Analiz Ediyor..." olarak değiştir
        const resultBox = document.getElementById('ai-result-box');
        resultBox.style.backgroundColor = 'transparent';
        resultBox.style.color = 'inherit';
        document.getElementById('decision-icon').className = 'ph ph-spinner ph-spin';
        document.getElementById('decision-text').textContent = 'Yapay Zeka Analiz Ediyor...';

        fetch(`/api/parcels/${parcelId}/check_irrigation`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                btnCheck.innerHTML = '<i class="ph ph-arrows-clockwise"></i> Yeniden Analiz Et';
                btnCheck.disabled = false;

                if(data.success) {
                    // Update UI
                    document.getElementById('val-temp').textContent = data.weather.temp_max + ' °C';
                    document.getElementById('val-rain').textContent = data.weather.precipitation + ' mm';
                    document.getElementById('val-budget').textContent = data.new_budget.toFixed(1) + ' mm';
                    
                    document.getElementById('ai-need').textContent = data.predicted_need.toFixed(1) + ' mm';
                    document.getElementById('ai-rain').textContent = data.weather.precipitation + ' mm';
                    document.getElementById('ai-budget').textContent = data.new_budget.toFixed(1) + ' mm';

                    const isIrrigate = data.decision.includes('ÖNERİLİR');
                    
                    if(isIrrigate) {
                        resultBox.style.backgroundColor = '#fee2e2';
                        resultBox.style.color = '#ef4444';
                        document.getElementById('decision-icon').className = 'ph ph-drop';
                        document.getElementById('decision-text').textContent = '🔴 Sulama Öneriliyor';
                    } else {
                        resultBox.style.backgroundColor = '#d1fae5';
                        resultBox.style.color = '#10b981';
                        document.getElementById('decision-icon').className = 'ph ph-check-circle';
                        document.getElementById('decision-text').textContent = '🟢 Sulama Gerekmiyor';
                    }
                    
                    const explanation = `Makine öğrenmesi modeli mevcut hava ve parsel koşullarına göre günlük su ihtiyacını ${data.predicted_need.toFixed(1)} mm olarak tahmin etmiştir. Beklenen yağış ve mevcut su bütçesi birlikte değerlendirildiğinde ${isIrrigate ? 'sulama yapılması gerekmektedir.' : 'sulama yapılmasına gerek yoktur.'}`;
                    document.getElementById('ai-explanation').textContent = explanation;

                    loadHistory(parcelId);
                    loadParcels(); // To update the budget in the sidebar
                } else {
                    document.getElementById('decision-icon').className = 'ph ph-warning';
                    document.getElementById('decision-text').textContent = 'Analiz Hatası!';
                    alert("Hata: " + data.error);
                }
            })
            .catch(err => {
                btnCheck.innerHTML = '<i class="ph ph-arrows-clockwise"></i> Tekrar Dene';
                btnCheck.disabled = false;
                document.getElementById('decision-icon').className = 'ph ph-warning';
                document.getElementById('decision-text').textContent = 'Bağlantı Hatası!';
            });
    }

    // Select Parcel
    function selectParcel(parcel) {
        currentParcelId = parcel.id;
        loadParcels(); // Update active class
        
        activeParcelName.textContent = parcel.name;
        dashboardContent.classList.remove('hidden');
        
        // Reset dashboard values
        document.getElementById('val-temp').textContent = '- °C';
        document.getElementById('val-rain').textContent = '- mm';
        document.getElementById('val-budget').textContent = parcel.water_budget.toFixed(1) + ' mm';
        
        const decisionBox = document.getElementById('decision-box');
        decisionBox.className = 'decision-box mt-2';
        document.getElementById('decision-icon').className = 'ph ph-info';
        document.getElementById('decision-text').textContent = 'Sistem Bekleniyor...';
        
        document.getElementById('ai-need').textContent = '- mm';
        document.getElementById('ai-rain').textContent = '- mm';
        document.getElementById('ai-budget').textContent = '- mm';
        document.getElementById('ai-explanation').textContent = '';

        loadHistory(parcel.id);
        
        // PARSEL SEÇİLDİĞİ ANDA OTOMATİK OLARAK ANALİZİ BAŞLAT
        runIrrigationCheck(parcel.id);
    }

    // Check Irrigation Button (Yenileme işlevi görecek)
    btnCheck.addEventListener('click', () => {
        if(!currentParcelId) return;
        runIrrigationCheck(currentParcelId);
    });

    // Init
    loadParcels();
});
