import os
import pandas as pd
from sklearn.model_selection import train_test_split

def main():
    print("6. Duplicate (Kopya Veri) ve Sızıntı Kontrolü Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')

    df = pd.read_csv(data_path)

    # Bütün kolonları kapsayan tam kopyalar
    exact_duplicates = df.duplicated().sum()
    print(f"Tam Kopya (Exact Duplicates) Sayısı: {exact_duplicates} (Tüm kolonlar %100 aynı)")

    # Sadece Features (Özellikler) aynı olanlar
    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    feature_duplicates = X.duplicated().sum()
    print(f"Özellik Kopyası (Feature Duplicates) Sayısı: {feature_duplicates} (Sadece 11 özellik aynı)")

    # Test ve Train arası sızıntı var mı?
    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train ve Test'te ortak olan feature seti var mı?
    train_merged = X_train.apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    test_merged = X_test.apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    
    overlap = set(train_merged).intersection(set(test_merged))
    print(f"Eğitim ve Test setlerinde birebir aynı olan veri (Satır) sayısı: {len(overlap)}")
    
    if len(overlap) > 0:
        print("❌ UYARI: Eğitim setindeki bazı satırlar test setinde de var. Bu durum 'Data Leakage' sebebidir ve model başarısını sahte (şişirilmiş) gösterebilir.")
    else:
        print("✅ BAŞARILI: Eğitim ve Test setleri arasında %100 ortak olan hiçbir satır bulunamadı. Sızıntı (Leakage) yok!")

if __name__ == "__main__":
    main()
