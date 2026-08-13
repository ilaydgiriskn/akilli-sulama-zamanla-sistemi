import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
import joblib

def main():
    print("3. Permutation Importance Testi Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    model_path = os.path.join(base_dir, 'data', 'water_need_model.pkl')

    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    features = num_cols + cat_cols
    X = df[features]

    # Test setinde özelliği bozup (karıştırıp) model başarımının ne kadar düştüğünü ölçeceğiz
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Permutasyonlar hesaplanıyor (Bu işlem biraz vakit alabilir)...")
    # n_repeats=5 ile her özelliği 5 kez karıştırıp ortalama etkiye bakıyoruz
    result = permutation_importance(model, X_test, y_test, n_repeats=5, random_state=42, n_jobs=-1)

    print("\n--- PERMUTASYON ÖNEM DERECELERİ ---")
    print("Hangi özelliği tamamen bozduğumuzda Accuracy (Doğruluk) ne kadar DÜŞÜYOR?\n")
    
    # Ortalama etkiye göre sıralama
    sorted_idx = result.importances_mean.argsort()[::-1]
    
    for i in sorted_idx:
        drop_mean = result.importances_mean[i] * 100
        drop_std = result.importances_std[i] * 100
        feature_name = features[i]
        print(f"{feature_name:<20}: Doğruluk %{drop_mean:.2f} düşüyor (± %{drop_std:.2f})")

if __name__ == "__main__":
    main()
