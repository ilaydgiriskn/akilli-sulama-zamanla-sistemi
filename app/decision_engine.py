import json
import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')

def load_ml_model():
    """Eğitilmiş Makine Öğrenmesi (ML) modelini yükler."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_water_need(temp_max, humidity, crop_type):
    """
    ML modelini kullanarak, sadece sıcaklık, nem ve ürün tipine göre 
    bitkinin günlük fizyolojik su tüketimini (ETc) tahmin eder.
    Yağış burada kullanılmaz (Double counting olmaması için).
    """
    model = load_ml_model()
    
    # Model bulunamazsa güvenlik önlemi olarak basit bir fallback
    if model is None:
        return 0.0
        
    # Modelin beklediği formatta DataFrame oluştur
    # NOT: 'Rainfall_mm' kolonunu modelin girdilerinden çıkardığımız için burada da siliyoruz.
    input_data = pd.DataFrame([{
        'Temperature_C': temp_max,
        'Humidity': humidity,
        'Crop_Type': crop_type
    }])
    
    # ML modelinden tahmin al (Sadece 1 satır veri verdiğimiz için index 0)
    prediction = model.predict(input_data)[0]
    return round(prediction, 2)

def calculate_water_balance(previous_balance, precipitation, predicted_need):
    """
    Güncel su bütçesini hesaplar.
    Formül: Güncel Su = Önceki Su + Yağış - Tahmini İhtiyaç
    """
    new_balance = previous_balance + precipitation - predicted_need
    return round(new_balance, 2)

def decide_irrigation(new_balance, threshold=-15.0):
    """
    Su bütçesine göre sulama kararını verir (Açıklanabilir kural).
    """
    if new_balance < threshold:
        return "SULAMA ÖNERİLİR"
    else:
        return "SULAMA GEREKMİYOR"
