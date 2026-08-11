import json
import os

REFERENCE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference_table.json')

def load_reference_data():
    """Ürün su ihtiyacı referans tablosunu yükler."""
    if not os.path.exists(REFERENCE_FILE):
        return {}
    with open(REFERENCE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_water_balance(previous_balance, precipitation, crop_type, temp_max):
    """
    Güncel su bütçesini hesaplar.
    Formül: Güncel Su = Önceki Su + Yağış - Günlük Tüketim
    """
    reference_data = load_reference_data()
    # Eğer ürün bulunamazsa varsayılan olarak 4.0 mm al
    crop_info = reference_data.get(crop_type, {})
    daily_need = crop_info.get("gunluk_su_ihtiyaci_mm", 4.0)
    
    # Sıcak hava düzeltmesi (Sıcaklık 30°C üzerindeyse %15 daha fazla su tüketir)
    if temp_max > 30:
        daily_need *= 1.15
        
    new_balance = previous_balance + precipitation - daily_need
    return round(new_balance, 2)

def decide_irrigation(new_balance, humidity, precipitation, threshold=-15.0):
    """
    Su bütçesi ve hava koşullarına göre sulama kararını verir.
    """
    # Nem %70'in üzerindeyse ve 5 mm'den fazla yağış bekleniyorsa ertele
    if humidity > 70 and precipitation > 5:
        return "SULAMA GEREKMİYOR (Yağış ve yüksek nem bekleniyor)"
    
    if new_balance < threshold:
        return "SULAMA ÖNERİLİR"
    else:
        return "SULAMA GEREKMİYOR"
