import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_target(df):
    """
    Veri setinde sayısal bir 'Günlük Su İhtiyacı (mm)' hedefi olmadığı için, 
    Kaggle'daki Irrigation_Need (Low/Medium/High) kategorilerine 
    ve agronomik gerçeklere dayanarak sürekli bir hedef (continuous target) üretiyoruz.
    'Sentetik veri, model geliştirme ve yazılım test amacıyla kullanılmıştır.'
    """
    need_map = {'Low': 3.0, 'Medium': 5.5, 'High': 8.5}
    base = df['Irrigation_Need'].map(need_map)
    
    # Sıcaklık, nem ve yağış etkisini ekleyelim
    temp_effect = (df['Temperature_C'] - 25) * 0.15
    humidity_effect = (df['Humidity'] - 50) * -0.05
    
    target = base + temp_effect + humidity_effect
    return target.clip(lower=0.5, upper=15.0)

def main():
    print("Veriseti yükleniyor...")
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    df = pd.read_csv(data_path)
    
    print("Hedef değişken oluşturuluyor...")
    df['Water_Need_mm'] = create_synthetic_target(df)
    
    # Modele Girecek Özellikler (API ve Arayüzden kolayca alabileceğimiz özellikler)
    X = df[['Temperature_C', 'Humidity', 'Rainfall_mm', 'Crop_Type']]
    y = df['Water_Need_mm']
    
    # Baseline comparison (Sadece ürün tipinin ortalamasına göre kaba tahmin)
    baseline_pred = np.full_like(y, y.mean())
    print("\n--- BASELINE (Sade Ortalama) BAŞARISI ---")
    print(f"MAE: {mean_absolute_error(y, baseline_pred):.2f} mm")
    print(f"RMSE: {np.sqrt(mean_squared_error(y, baseline_pred)):.2f} mm")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Pipeline (Önişleme + Random Forest)
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['Temperature_C', 'Humidity', 'Rainfall_mm']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['Crop_Type'])
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    print("\nModel eğitiliyor (RandomForestRegressor)...")
    model.fit(X_train, y_train)
    
    print("\n--- ML MODEL BAŞARISI ---")
    y_pred = model.predict(X_test)
    print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f} mm")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f} mm")
    print(f"R²: {r2_score(y_test, y_pred):.2f}")
    
    # Feature Importance (Hangi veri kararı ne kadar etkiledi?)
    rf = model.named_steps['regressor']
    cat_features = model.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(['Crop_Type'])
    
    importances = rf.feature_importances_
    print("\n--- FEATURE IMPORTANCE ---")
    crop_importance = sum(importances[3:])
    display_importances = {
        'Sıcaklık (Temperature_C)': importances[0],
        'Nem (Humidity)': importances[1],
        'Yağış (Rainfall_mm)': importances[2],
        'Ürün Tipi (Crop_Type)': crop_importance
    }
    
    for k, v in sorted(display_importances.items(), key=lambda item: item[1], reverse=True):
        bar = '█' * int(v * 40)
        print(f"{k.ljust(25)} {bar} ({v:.2f})")
    
    model_out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')
    joblib.dump(model, model_out_path)
    print(f"\nModel başarıyla kaydedildi: {model_out_path}")

if __name__ == "__main__":
    main()
