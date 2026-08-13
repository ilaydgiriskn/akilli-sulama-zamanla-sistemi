import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings
warnings.filterwarnings('ignore')

def main():
    print("Veriseti yükleniyor...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    df = pd.read_csv(data_path)
    
    # Hedef Değişken (Orijinal 3 Sınıf: Low, Medium, High)
    y = df['Irrigation_Need']
    
    # 1. Dinamik ve Statik Özellikler (Features)
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH', 'Field_Area_hectare']
    cat_cols = ['Crop_Type', 'Soil_Type', 'Region']
    
    X = df[num_cols + cat_cols]
    
    # 2. Veri Ön İşleme (Preprocessing)
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ])
    
    # 3. SMOTE + Random Forest Pipeline
    print("Makine Öğrenmesi Pipeline (SMOTE + RF) kuruluyor...")
    model = ImbPipeline([
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Model eğitiliyor (Bu işlem SMOTE nedeniyle birkaç saniye sürebilir)...")
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    print("\n--- ML MODEL BAŞARISI (Test Seti) ---")
    print(f"Doğruluk (Accuracy): %{accuracy_score(y_test, y_pred)*100:.2f}\n")
    print("Sınıflandırma Raporu:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Modeli Kaydetme
    model_save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')
    joblib.dump(model, model_save_path)
    print(f"\nModel başarıyla kaydedildi: {model_save_path}")

if __name__ == "__main__":
    main()
