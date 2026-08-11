import requests
import json

def test_open_meteo_api():
    print("Open-Meteo API Testi Başlıyor...")
    # Eskişehir koordinatları (Örnek)
    lat = 39.77
    lon = 30.52
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
        "forecast_days": 3,
        "timezone": "auto"
    }
    
    print(f"İstek atılıyor: {url} | Parametreler: {params}")
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print("\n[BAŞARILI] API Yanıtı:")
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"\n[HATA] API çağrısı başarısız oldu. Durum kodu: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n[İSTİSNA] İstek sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    test_open_meteo_api()
