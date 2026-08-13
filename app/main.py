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
    
    # 7 Statik Girdi
    crop_type = data.get('crop_type', 'Wheat')
    crop_growth_stage = data.get('crop_growth_stage', 'Vegetative')
    season = data.get('season', 'Spring')
    mulching_used = data.get('mulching_used', 'No')
    soil_moisture = float(data.get('soil_moisture', 30.0))
    soil_ph = float(data.get('soil_ph', 6.5))
    soil_type = data.get('soil_type', 'Loamy')
    
    parcel_id = database.add_parcel(
        name, lat, lon, crop_type, crop_growth_stage, season, 
        mulching_used, soil_moisture, soil_ph, soil_type
    )
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
    
    # 1. Hava Durumu Verisi Çek (4 Dinamik Veri)
    weather = get_forecast(parcel['latitude'], parcel['longitude'])
    if not weather['success']:
        return jsonify({"success": False, "error": "Hava durumu alınamadı."})
    
    # 2. 11 Özellikli ML Karar Motoruna Veri Hazırla
    input_data = {
        "Temperature_C": weather['temperature_max'],
        "Humidity": weather['humidity'],
        "Rainfall_mm": weather['precipitation'],
        "Wind_Speed_kmh": weather['wind_speed_kmh'],
        "Soil_Moisture": parcel['soil_moisture'],
        "Soil_pH": parcel['soil_ph'],
        "Crop_Type": parcel['crop_type'],
        "Crop_Growth_Stage": parcel['crop_growth_stage'],
        "Season": parcel['season'],
        "Mulching_Used": parcel['mulching_used'],
        "Soil_Type": parcel['soil_type']
    }
    
    ai_result = predict_irrigation_decision(input_data)
    
    if "error" in ai_result:
        return jsonify({"success": False, "error": ai_result["error"]})
        
    decision = ai_result['prediction']
    confidence = ai_result['confidence']
    message = ai_result['message']
    
    # 3. Veritabanını Güncelle
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
        "message": message,
        "confidence": confidence,
        "weather": {
            "temp_max": weather['temperature_max'],
            "precipitation": weather['precipitation'],
            "humidity": weather['humidity'],
            "wind_speed_kmh": weather['wind_speed_kmh']
        }
    })

@app.route('/api/predict', methods=['POST'])
def direct_predict_test():
    """ML modelini doğrudan terminalden/Postman'den test etmek için uç nokta."""
    data = request.json
    ai_result = predict_irrigation_decision(data)
    
    if "error" in ai_result:
        return jsonify({"success": False, "error": ai_result["error"]}), 400
        
    return jsonify({
        "success": True,
        "prediction": ai_result["prediction"],
        "confidence": ai_result["confidence"],
        "message": ai_result["message"]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
