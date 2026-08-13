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
                        <div class="parcel-meta">${p.crop_type} | ${p.soil_type} | Nem: %${p.soil_moisture}</div>
                    `;
                    li.onclick = () => selectParcel(p);
                    parcelListEl.appendChild(li);
                });
            });
    }

    // Add Parcel (7 Static ML Features)
    addParcelForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('p-name').value,
            latitude: document.getElementById('p-lat').value,
            longitude: document.getElementById('p-lon').value,
            crop_type: document.getElementById('p-crop').value,
            crop_growth_stage: document.getElementById('p-stage').value,
            soil_type: document.getElementById('p-soil-type').value,
            soil_moisture: document.getElementById('p-soil-moisture').value,
            soil_ph: document.getElementById('p-soil-ph').value,
            season: document.getElementById('p-season').value,
            mulching_used: document.getElementById('p-mulching').value
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
            } else {
                alert("Hata: " + res.error);
            }
        });
    });

    // Check Irrigation Logic
    function runIrrigationCheck(parcelId) {
        const btnOriginalText = btnCheck.innerHTML;
        btnCheck.innerHTML = '<i class="ph ph-spinner ph-spin"></i> İşleniyor...';
        btnCheck.disabled = true;

        const resultBox = document.getElementById('ai-result-box');
        resultBox.style.backgroundColor = 'transparent';
        resultBox.style.color = 'inherit';
        document.getElementById('decision-icon').className = 'ph ph-spinner ph-spin';
        document.getElementById('decision-text').textContent = 'Yapay Zeka Analiz Ediyor...';
        document.getElementById('ai-confidence').textContent = '';
        document.getElementById('ai-explanation').textContent = '';

        fetch(`/api/parcels/${parcelId}/check_irrigation`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                btnCheck.innerHTML = '<i class="ph ph-arrows-clockwise"></i> Yeniden Analiz Et';
                btnCheck.disabled = false;

                if(data.success) {
                    // Update UI (Open-Meteo Weather)
                    document.getElementById('val-temp').textContent = data.weather.temp_max + ' °C';
                    document.getElementById('val-rain').textContent = data.weather.precipitation + ' mm';
                    document.getElementById('val-wind').textContent = data.weather.wind_speed_kmh + ' km/h';
                    
                    const decision = data.decision; // "Low", "Medium", "High"
                    
                    if(decision === 'High') {
                        resultBox.style.backgroundColor = '#fee2e2';
                        resultBox.style.color = '#ef4444';
                        document.getElementById('decision-icon').className = 'ph ph-warning-circle';
                        document.getElementById('decision-text').textContent = '🔴 Yüksek İhtiyaç';
                    } else if(decision === 'Medium') {
                        resultBox.style.backgroundColor = '#fef3c7';
                        resultBox.style.color = '#d97706'; // Darker amber for contrast
                        document.getElementById('decision-icon').className = 'ph ph-info';
                        document.getElementById('decision-text').textContent = '🟡 Orta İhtiyaç';
                    } else { // Low
                        resultBox.style.backgroundColor = '#d1fae5';
                        resultBox.style.color = '#10b981';
                        document.getElementById('decision-icon').className = 'ph ph-check-circle';
                        document.getElementById('decision-text').textContent = '🟢 Düşük İhtiyaç';
                    }
                    
                    document.getElementById('ai-confidence').textContent = 'Model Güven Skoru: %' + data.confidence;
                    document.getElementById('ai-explanation').textContent = data.message;

                    loadHistory(parcelId);
                } else {
                    document.getElementById('decision-icon').className = 'ph ph-warning';
                    document.getElementById('decision-text').textContent = 'Analiz Hatası!';
                    document.getElementById('ai-explanation').textContent = data.error;
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
        document.getElementById('val-wind').textContent = '- km/h';
        
        const decisionBox = document.getElementById('decision-box');
        decisionBox.className = 'decision-box mt-2';
        document.getElementById('decision-icon').className = 'ph ph-info';
        document.getElementById('decision-text').textContent = 'Sistem Bekleniyor...';
        
        document.getElementById('ai-confidence').textContent = '';
        document.getElementById('ai-explanation').textContent = '';

        loadHistory(parcel.id);
        
        // PARSEL SEÇİLDİĞİ ANDA OTOMATİK OLARAK ANALİZİ BAŞLAT
        runIrrigationCheck(parcel.id);
    }

    // Load History
    function loadHistory(parcelId) {
        fetch(`/api/parcels/${parcelId}/history`)
            .then(res => res.json())
            .then(data => {
                historyList.innerHTML = '';
                if(data.length === 0) {
                    historyList.innerHTML = '<li class="empty-state">Geçmiş kayıt yok.</li>';
                    return;
                }
                data.forEach(record => {
                    const li = document.createElement('li');
                    
                    let decisionIcon = '';
                    let decisionClass = '';
                    
                    if(record.decision === 'High') {
                        decisionIcon = '🔴'; decisionClass = 'text-red';
                    } else if(record.decision === 'Medium') {
                        decisionIcon = '🟡'; decisionClass = 'text-orange';
                    } else {
                        decisionIcon = '🟢'; decisionClass = 'text-green';
                    }

                    li.innerHTML = `
                        <div class="h-date">${record.date}</div>
                        <div class="h-decision ${decisionClass}">
                            ${decisionIcon} ${record.decision}
                        </div>
                    `;
                    historyList.appendChild(li);
                });
            });
    }

    // Check Irrigation Button (Yenileme işlevi görecek)
    btnCheck.addEventListener('click', () => {
        if(!currentParcelId) return;
        runIrrigationCheck(currentParcelId);
    });

    // Init
    loadParcels();
});
