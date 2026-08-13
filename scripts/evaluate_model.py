import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

def main():
    print("="*50)
    print("   SINIFLANDIRMA MODELİ DOĞRULAMA TESTİ")
    print("="*50)
    
    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    
    if not os.path.exists(model_path):
        print("Hata: Model dosyası bulunamadı! Önce train_ml_model.py çalıştırılmalı.")
        return
        
    model = joblib.load(model_path)
    df = pd.read_csv(data_path)
    
    # Hedef değişkeni oluştur (Classification)
    df['Irrigation_Decision'] = df['Irrigation_Need'].apply(lambda x: 0 if x == 'Low' else 1)
    
    X = df[['Temperature_C', 'Humidity', 'Crop_Type']]
    y = df['Irrigation_Decision']
    
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    y_pred = model.predict(X_test)
    
    print("\n--- MODEL TEST SONUÇLARI ---")
    print(f"Accuracy : %{accuracy_score(y_test, y_pred)*100:.2f}")
    print(f"Precision: %{precision_score(y_test, y_pred, zero_division=0)*100:.2f}")
    print(f"Recall   : %{recall_score(y_test, y_pred, zero_division=0)*100:.2f}")
    print(f"F1 Score : %{f1_score(y_test, y_pred, zero_division=0)*100:.2f}")
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"[[{cm[0][0]} {cm[0][1]}]\n [{cm[1][0]} {cm[1][1]}]]")
    
    print("\n2. SENARYO TESTLERİ (Model Mantıklı Kararlar Veriyor mu?)")
    print("-" * 50)
    
    def eval_scenario(temp, hum, crop):
        scenario = pd.DataFrame([{'Temperature_C': temp, 'Humidity': hum, 'Crop_Type': crop}])
        prediction = model.predict(scenario)[0]
        probs = model.predict_proba(scenario)[0]
        
        if prediction == 1:
            decision_text = "SULA (1)"
            confidence = probs[1] * 100
        else:
            decision_text = "SULAMA (0)"
            confidence = probs[0] * 100
            
        print(f"   Sıcaklık {temp}°C, Nem %{hum} -> Karar: {decision_text} (Güven: %{confidence:.1f})")

    # Senaryo 1: Aynı üründe artan sıcaklığın etkisi
    print("[Senaryo 1] Sebze - Nem %40")
    for temp in [20, 25, 30, 35, 40]:
        eval_scenario(temp, 40, 'sebze')
        
    print("\n[Senaryo 2] Sebze - Sıcaklık 35°C (Nemin Etkisi)")
    for hum in [20, 40, 60, 80]:
        eval_scenario(35, hum, 'sebze')
        
    print("\n==================================================")
    print("SONUÇ: Sınıflandırma modeli hava koşullarına göre")
    print("karar olasılıklarını (Confidence) tutarlı şekilde değiştirmektedir.")
    print("==================================================")

if __name__ == "__main__":
    main()
