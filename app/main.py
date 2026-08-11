from flask import Flask, render_template, request, jsonify
import sys
import os
from datetime import datetime

# app modüllerine erişim için
sys.path.append(os.path.dirname(__file__))

import database
from weather_client import get_forecast
from decision_engine import predict_water_need, calculate_water_balance, decide_irrigation

app = Flask(__name__)

# Veritabanını başlat
database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/parcels', methods=['GET'])
def get_parcels():
    parcels = database.get_all_parcels()
    return jsonify(parcels)

@app.route('/api/parcels', methods=['POST'])
def add_parcel():
    data = request.json
    name = data.get('name')
    lat = float(data.get('latitude'))
    lon = float(data.get('longitude'))
    crop = data.get('crop_type')
    
    parcel_id = database.add_parcel(name, lat, lon, crop)
    return jsonify({"success": True, "parcel_id": parcel_id})

@app.route('/api/parcels/<int:parcel_id>/history', methods=['GET'])
def get_history(parcel_id):
    history = database.get_irrigation_history(parcel_id)
    return jsonify(history)

@app.route('/api/parcels/<int:parcel_id>/check_irrigation', methods=['POST'])
def check_irrigation(parcel_id):
    parcel = database.get_parcel(parcel_id)
    if not parcel:
        return jsonify({"success": False, "error": "Parsel bulunamadı."})
    
    # 1. Hava Durumu Verisi Çek
    weather = get_forecast(parcel['latitude'], parcel['longitude'])
    if not weather['success']:
        return jsonify({"success": False, "error": "Hava durumu alınamadı."})
    
    # 2. Makine Öğrenmesi ile Su İhtiyacı Tahmini (Prediction)
    predicted_need = predict_water_need(
        temp_max=weather['temperature_max'],
        humidity=weather['humidity'],
        precipitation=weather['precipitation'],
        crop_type=parcel['crop_type']
    )

    # 3. Su Bütçesi Hesapla
    prev_balance = parcel['water_budget']
    new_balance = calculate_water_balance(
        previous_balance=prev_balance,
        precipitation=weather['precipitation'],
        predicted_need=predicted_need
    )
    
    # 4. Kural Motoru ile Nihai Karar
    decision = decide_irrigation(new_balance=new_balance)
    
    # 5. Veritabanını Güncelle (Sadece bugün için daha önce kayıt girilmediyse güncelle!)
    today_prefix = datetime.now().strftime('%Y-%m-%d')
    history = database.get_irrigation_history(parcel_id)
    already_checked_today = any(record['date'].startswith(today_prefix) for record in history)
    
    if not already_checked_today:
        database.update_water_budget(parcel_id, new_balance)
        database.add_irrigation_record(
            parcel_id=parcel_id,
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            decision=decision,
            temp_max=weather['temperature_max'],
            precipitation=weather['precipitation']
        )
    else:
        # Zaten bugün kayıt girilmişse, mevcut bütçeyi bozma, sadece güncel bakiyeyi döndür
        # (Yeniden tıklandığında bütçenin sonsuza kadar düşmesini engeller)
        new_balance = prev_balance
    
    # Yeni arayüz talebi için tahmin edilen miktarı da döndürüyoruz
    return jsonify({
        "success": True,
        "decision": decision,
        "new_budget": new_balance,
        "predicted_need": predicted_need,
        "weather": {
            "temp_max": weather['temperature_max'],
            "precipitation": weather['precipitation'],
            "humidity": weather['humidity']
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
