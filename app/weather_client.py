import requests
import logging

def get_forecast(lat, lon, days=3):
    """
    Open-Meteo API'sine bağlanarak hava durumu tahminlerini çeker.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,wind_speed_10m_max",
        "hourly": "relative_humidity_2m,soil_moisture_0_to_7cm",
        "forecast_days": days,
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})
        
        precipitation = daily.get("precipitation_sum", [0.0])[0]
        temp_max = daily.get("temperature_2m_max", [20.0])[0]
        wind_speed = daily.get("wind_speed_10m_max", [10.0])[0]
        
        # Günlük ortalama nem ve toprak nemi değerini saatlik verilerden hesaplayalım
        humidity_list = hourly.get("relative_humidity_2m", [])
        if humidity_list:
            humidity = sum(humidity_list[:24]) / 24.0
        else:
            humidity = 50.0
            
        soil_moisture_list = hourly.get("soil_moisture_0_to_7cm", [])
        if soil_moisture_list:
            # Open-Meteo topraktaki nem oranını m³/m³ olarak döndürür (örneğin 0.35).
            # Veri setimiz (irrigation_prediction) % bazlı olabilir veya farklı ölçektir, bu yüzden basit bir çarpım yapabiliriz.
            # Veri setindeki Soil_Moisture değerleri genellikle 10-60 arası % gibi görünüyor.
            soil_moisture = (sum(soil_moisture_list[:24]) / 24.0) * 100
        else:
            soil_moisture = 30.0
        
        return {
            "success": True,
            "precipitation": precipitation,
            "temperature_max": temp_max,
            "humidity": humidity,
            "wind_speed_kmh": wind_speed,
            "soil_moisture": soil_moisture,
            "raw_data": data
        }
    except Exception as e:
        logging.error(f"API Hatası: {e}")
        return {
            "success": False,
            "error": str(e)
        }
