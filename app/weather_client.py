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
        "daily": "precipitation_sum,temperature_2m_max",
        "hourly": "relative_humidity_2m",
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
        
        # Günlük ortalama nem değerini saatlik verilerden hesaplayalım
        humidity_list = hourly.get("relative_humidity_2m", [])
        if humidity_list:
            # İlk 24 saatin ortalaması
            humidity = sum(humidity_list[:24]) / 24.0
        else:
            humidity = 50.0
        
        return {
            "success": True,
            "precipitation": precipitation,
            "temperature_max": temp_max,
            "humidity": humidity,
            "raw_data": data
        }
    except Exception as e:
        logging.error(f"API Hatası: {e}")
        return {
            "success": False,
            "error": str(e)
        }
