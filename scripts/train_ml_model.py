import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    print("Veriseti yükleniyor...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    df = pd.read_csv(data_path)
    
    print("Sınıflandırma (Classification) Hedefi oluşturuluyor...")
    # 'Low' olanlar -> 0 (Sulama)
    # 'Medium' ve 'High' olanlar -> 1 (Sula)
    df['Irrigation_Decision'] = df['Irrigation_Need'].apply(lambda x: 0 if x == 'Low' else 1)
    
    # Modele Girecek Özellikler
    X = df[['Temperature_C', 'Humidity', 'Crop_Type']]
    y = df['Irrigation_Decision']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Pipeline (Önişleme + Random Forest Classifier)
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['Temperature_C', 'Humidity']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['Crop_Type'])
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])
    
    print("\nModel eğitiliyor (RandomForestClassifier)...")
    model.fit(X_train, y_train)
    
    print("\n--- ML MODEL BAŞARISI ---")
    y_pred = model.predict(X_test)
    print(f"Doğruluk (Accuracy): %{accuracy_score(y_test, y_pred)*100:.2f}")
    print("\nSınıflandırma Raporu:")
    print(classification_report(y_test, y_pred, target_names=['Sulama (0)', 'Sula (1)']))
    
    # Feature Importance
    rf = model.named_steps['classifier']
    importances = rf.feature_importances_
    print("\n--- FEATURE IMPORTANCE ---")
    crop_importance = sum(importances[2:])
    display_importances = {
        'Sıcaklık (Temperature_C)': importances[0],
        'Nem (Humidity)': importances[1],
        'Ürün Tipi (Crop_Type)': crop_importance
    }
    
    for k, v in sorted(display_importances.items(), key=lambda item: item[1], reverse=True):
        bar = '#' * int(v * 40)
        print(f"{k.ljust(25)} {bar} ({v:.2f})")
    
    model_out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')
    joblib.dump(model, model_out_path)
    print(f"\nModel başarıyla kaydedildi: {model_out_path}")

if __name__ == "__main__":
    main()
