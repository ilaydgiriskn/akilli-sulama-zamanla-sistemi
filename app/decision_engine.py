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

def predict_irrigation_decision(temp_max, humidity, rainfall, wind_speed, soil_moisture, soil_ph, field_area, crop_type, soil_type, region):
    """
    ML Sınıflandırma modelini kullanarak, 
    doğrudan 'Low', 'Medium', veya 'High' kararı verir.
    Ayrıca karar olasılığını (%) döndürür.
    """
    model = load_ml_model()
    
    if model is None:
        return {"decision": "SİSTEM HATASI", "confidence": 0}
        
    input_data = pd.DataFrame([{
        'Temperature_C': temp_max,
        'Humidity': humidity,
        'Rainfall_mm': rainfall,
        'Wind_Speed_kmh': wind_speed,
        'Soil_Moisture': soil_moisture,
        'Soil_pH': soil_ph,
        'Field_Area_hectare': field_area,
        'Crop_Type': crop_type,
        'Soil_Type': soil_type,
        'Region': region
    }])
    
    # SınıflandırmaTahmini (Low, Medium, High)
    prediction = model.predict(input_data)[0]
    
    # Olasılık değerleri (Low, Medium, High)
    # model.classes_ dizisi olasılıkların sırasını verir
    probabilities = model.predict_proba(input_data)[0]
    class_index = list(model.classes_).index(prediction)
    confidence = round(probabilities[class_index] * 100, 1)
    
    # Uygulama Dili Çevirisi
    if prediction == 'High':
        decision_text = "SULAMA ÖNERİLİR"
    elif prediction == 'Medium':
        decision_text = "SULAMA İHTİYACI ORTA"
    else:
        decision_text = "SULAMA GEREKMİYOR"
        
    return {"decision": decision_text, "confidence": confidence, "raw_prediction": prediction}
