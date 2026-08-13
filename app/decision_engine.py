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

def predict_irrigation_decision(temp_max, humidity, crop_type):
    """
    ML Sınıflandırma modelini kullanarak, 
    doğrudan 'Sulama (0)' veya 'Sula (1)' kararı verir.
    Ayrıca karar olasılığını (%) döndürür.
    """
    model = load_ml_model()
    
    if model is None:
        return {"decision": "SİSTEM HATASI", "confidence": 0}
        
    input_data = pd.DataFrame([{
        'Temperature_C': temp_max,
        'Humidity': humidity,
        'Crop_Type': crop_type
    }])
    
    # SınıflandırmaTahmini (0 veya 1)
    prediction = model.predict(input_data)[0]
    
    # Olasılık değerleri (0 olma ihtimali, 1 olma ihtimali)
    probabilities = model.predict_proba(input_data)[0]
    
    if prediction == 1:
        confidence = round(probabilities[1] * 100, 1)
        return {"decision": "SULAMA ÖNERİLİR", "confidence": confidence}
    else:
        confidence = round(probabilities[0] * 100, 1)
        return {"decision": "SULAMA GEREKMİYOR", "confidence": confidence}
