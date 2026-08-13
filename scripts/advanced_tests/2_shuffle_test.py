import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.base import clone
import joblib

def main():
    print("2. Y-Shuffle (Hedef Karıştırma) Testi Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    model_path = os.path.join(base_dir, 'data', 'water_need_model.pkl')

    df = pd.read_csv(data_path)
    model = joblib.load(model_path)
    # Clone ile boş, aynı ayarlarda yepyeni bir model oluşturuyoruz.
    shuffled_model = clone(model)

    y = df['Irrigation_Need']
    # HEDEFİ TAMAMEN RASTGELE KARIŞTIR (SHUFFLE)
    y_shuffled = np.random.permutation(y)

    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    X_train, X_test, y_train_shuf, y_test_shuf = train_test_split(X, y_shuffled, test_size=0.2, random_state=42)

    print("Model shuffle edilmiş anlamsız veriyle eğitiliyor...")
    shuffled_model.fit(X_train, y_train_shuf)

    y_pred = shuffled_model.predict(X_test)
    
    acc = accuracy_score(y_test_shuf, y_pred)
    f1 = f1_score(y_test_shuf, y_pred, average='macro')
    
    print("\n--- SHUFFLE TEST SONUÇLARI ---")
    print(f"Accuracy (Doğruluk): %{acc*100:.2f}")
    print(f"Macro F1 Score:      %{f1*100:.2f}")
    print("---------------------------------")
    if acc < 0.50:
        print("✅ BAŞARILI: Hedef karıştırıldığında başarı düştü! Model ezber yapmıyor, gerçekten özelliklerle sonuç arasında mantıklı bir bağ kuruyordu.")
    else:
        print("❌ UYARI: Hedef tamamen anlamsızken bile başarı çok yüksek. Sızıntı (Leakage) olabilir!")

if __name__ == "__main__":
    main()
