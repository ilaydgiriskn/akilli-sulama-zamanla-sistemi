import json
import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')

# Modelin tam olarak beklediği sütun sırası
FEATURE_COLUMNS = [
    'Temperature_C',
    'Humidity',
    'Rainfall_mm',
    'Wind_Speed_kmh',
    'Soil_Moisture',
    'Soil_pH',
    'Crop_Type',
    'Crop_Growth_Stage',
    'Season',
    'Mulching_Used',
    'Soil_Type'
]

MESSAGES = {
    "Low": "Mevcut toprak ve çevresel koşullar sulama ihtiyacının düşük olduğunu göstermektedir. Sulama gerekmiyor.",
    "Medium": "Toprak ve hava koşulları sulama ihtiyacının arttığını göstermektedir. Toprak nemini yakından takip etmeniz önerilir.",
    "High": "Mevcut çevresel ve toprak koşulları bitkinin yüksek düzeyde su stresi yaşadığını göstermektedir. Acil sulama planlaması yapılması önerilir."
}

def load_ml_model():
    """Eğitilmiş Makine Öğrenmesi (ML) modelini yükler."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

def predict_irrigation_decision(input_data_dict):
    """
    ML modelini doğrudan çağırarak sonucu oluşturur.
    input_data_dict içinde 11 feature eksiksiz bulunmalıdır.
    """
    # 1. Eksik veri kontrolü
    for col in FEATURE_COLUMNS:
        if col not in input_data_dict:
            return {"error": f"{col} bilgisi gerekli."}
            
    # 2. DataFrame oluştur ve sadece FEATURE_COLUMNS sırasına göre diz
    input_df = pd.DataFrame([input_data_dict])
    input_df = input_df[FEATURE_COLUMNS]
    
    # 3. Model yükle ve tahmin yap
    model = load_ml_model()
    if model is None:
        return {"error": "ML Modeli (.pkl) bulunamadı veya yüklenemedi."}
        
    try:
        prediction = model.predict(input_df)[0]
        probabilities = model.predict_proba(input_df)[0]
        class_index = list(model.classes_).index(prediction)
        confidence = round(probabilities[class_index] * 100, 1)
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "message": MESSAGES.get(prediction, "Bilinmeyen durum tespit edildi.")
        }
    except Exception as e:
        return {"error": f"Model tahmin sırasında bir hata oluşturdu: {str(e)}"}
