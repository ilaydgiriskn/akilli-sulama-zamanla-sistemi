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

        loadHistory(parcel.id);
    }

    // Load History
    function loadHistory(id) {
        fetch(`/api/parcels/${id}/history`)
            .then(res => res.json())
            .then(data => {
                historyList.innerHTML = '';
                if(data.length === 0) {
                    historyList.innerHTML = '<li class="empty-state">Henüz kayıt yok.</li>';
                    return;
                }
                data.forEach(h => {
                    const li = document.createElement('li');
                    const isIrrigate = h.decision.includes('ÖNERİLİR');
                    const icon = isIrrigate ? '<i class="ph ph-drop text-teal"></i>' : '<i class="ph ph-prohibit"></i>';
                    li.innerHTML = `
                        <div>
                            <strong>${h.date.split(' ')[0]}</strong>
                            <div style="font-size:0.8rem; color:#6b7280;">Sıcaklık: ${h.temperature_max}°C, Yağış: ${h.precipitation}mm</div>
                        </div>
                        <div style="display:flex; align-items:center; gap:0.5rem; font-weight:600; color:${isIrrigate ? '#10B981':'#6b7280'};">
                            ${icon} ${isIrrigate ? 'Sulandı' : 'Sulanmadı'}
                        </div>
                    `;
                    historyList.appendChild(li);
                });
            });
    }

    // Check Irrigation
    btnCheck.addEventListener('click', () => {
        if(!currentParcelId) return;
        
        const btnOriginalText = btnCheck.innerHTML;
        btnCheck.innerHTML = '<i class="ph ph-spinner ph-spin"></i> İşleniyor...';
        btnCheck.disabled = true;

        fetch(`/api/parcels/${currentParcelId}/check_irrigation`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                btnCheck.innerHTML = btnOriginalText;
                btnCheck.disabled = false;

                if(data.success) {
                    // Update UI
                    document.getElementById('val-temp').textContent = data.weather.temp_max + ' °C';
                    document.getElementById('val-rain').textContent = data.weather.precipitation + ' mm';
                    document.getElementById('val-budget').textContent = data.new_budget.toFixed(1) + ' mm';

                    const decisionBox = document.getElementById('decision-box');
                    const isIrrigate = data.decision.includes('ÖNERİLİR');
                    
                    if(isIrrigate) {
                        decisionBox.className = 'decision-box mt-2 irrigate';
                        document.getElementById('decision-icon').className = 'ph ph-plant';
                    } else {
                        decisionBox.className = 'decision-box mt-2 no-irrigate';
                        document.getElementById('decision-icon').className = 'ph ph-cloud-slash';
                    }
                    document.getElementById('decision-text').textContent = data.decision;

                    loadHistory(currentParcelId);
                    loadParcels(); // To update the budget in the sidebar
                } else {
                    alert("Hata: " + data.error);
                }
            })
            .catch(err => {
                btnCheck.innerHTML = btnOriginalText;
                btnCheck.disabled = false;
                alert("Bağlantı hatası!");
            });
    });

    // Init
    loadParcels();
});
