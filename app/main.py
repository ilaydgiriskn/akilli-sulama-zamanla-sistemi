from flask import Flask, render_template, request, jsonify
import sys
import os
from datetime import datetime

# app modüllerine erişim için
sys.path.append(os.path.dirname(__file__))

import database
from weather_client import get_forecast
from decision_engine import predict_irrigation_decision

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
    
    # Frontend henüz güncellenmediği için şimdilik varsayılan değerler ekleyelim
    soil_type = data.get('soil_type', 'Loamy')
    soil_ph = float(data.get('soil_ph', 6.5))
    field_area = float(data.get('field_area', 2.0))
    region = data.get('region', 'Central')
    
    parcel_id = database.add_parcel(name, lat, lon, crop, soil_type, soil_ph, field_area, region)
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
    
    # 2. Makine Öğrenmesi (Classification) ile Karar
    ai_result = predict_irrigation_decision(
        temp_max=weather['temperature_max'],
        humidity=weather['humidity'],
        rainfall=weather['precipitation'],
        wind_speed=weather['wind_speed_kmh'],
        soil_moisture=weather['soil_moisture'],
        soil_ph=parcel['soil_ph'],
        field_area=parcel['field_area'],
        crop_type=parcel['crop_type'],
        soil_type=parcel['soil_type'],
        region=parcel['region']
    )
    
    decision = ai_result['decision']
    confidence = ai_result['confidence']
    
    # 3. Veritabanını Güncelle (Sadece bugün için daha önce kayıt girilmediyse güncelle!)
    today_prefix = datetime.now().strftime('%Y-%m-%d')
    history = database.get_irrigation_history(parcel_id)
    already_checked_today = any(record['date'].startswith(today_prefix) for record in history)
    
    if not already_checked_today:
        database.add_irrigation_record(
            parcel_id=parcel_id,
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            decision=decision,
            temp_max=weather['temperature_max'],
            precipitation=weather['precipitation']
        )
    
    return jsonify({
        "success": True,
        "decision": decision,
        "confidence": confidence,
        "raw_prediction": ai_result.get('raw_prediction'),
        "weather": {
            "temp_max": weather['temperature_max'],
            "precipitation": weather['precipitation'],
            "humidity": weather['humidity'],
            "wind_speed_kmh": weather['wind_speed_kmh'],
            "soil_moisture": weather['soil_moisture']
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
