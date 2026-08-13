import os
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from sklearn.base import clone
import joblib

def main():
    print("5. Bölge Bazlı (Region) Holdout Testi Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    model_path = os.path.join(base_dir, 'data', 'water_need_model.pkl')

    df = pd.read_csv(data_path)
    model = joblib.load(model_path)
    new_model = clone(model)

    regions = df['Region'].unique()
    train_regions = regions[:len(regions)//2]
    test_regions = regions[len(regions)//2:]

    print(f"Eğitim Bölgeleri: {train_regions}")
    print(f"Test Bölgeleri: {test_regions}")

    df_train = df[df['Region'].isin(train_regions)]
    df_test = df[df['Region'].isin(test_regions)]

    y_train = df_train['Irrigation_Need']
    y_test = df_test['Irrigation_Need']

    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X_train = df_train[num_cols + cat_cols]
    X_test = df_test[num_cols + cat_cols]

    print("Model daha önce hiç görmediği bir bölge (iklim/toprak) üzerinde test ediliyor...")
    new_model.fit(X_train, y_train)

    y_pred = new_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')

    print("\n--- REGION HOLDOUT SONUÇLARI ---")
    print(f"Test Accuracy: %{acc*100:.2f}")
    print(f"Test Macro F1: %{f1*100:.2f}")
    print("Not: Bu testte başarı çok yüksekse (%90+), modelin öğrenimi spesifik bir bölgeye bağımlı değildir.")

if __name__ == "__main__":
    main()
