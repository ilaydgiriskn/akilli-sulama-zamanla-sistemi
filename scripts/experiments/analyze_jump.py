import pandas as pd
import joblib
import os

print("--- 1. FEATURE IMPORTANCE (Özellik Önem Dereceleri) ---")
model_path = r'c:\Users\İlayda Serpil\Desktop\tarım\sulama_sistemi\data\water_need_model.pkl'
if os.path.exists(model_path):
    model = joblib.load(model_path)
    # The pipeline is: preprocessor -> smote -> classifier
    rf = model.named_steps['classifier']
    importances = rf.feature_importances_
    
    # Feature names need to be extracted from preprocessor
    # Number of numerical features: 6
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    
    print("\nSayisal ve Ohe sonrasi Kategorik featurelarin ham onem degerleri (Ilk 6 = Sayisal):\n")
    for i, col in enumerate(num_cols):
        print(f"{col:20}: %{importances[i]*100:.2f}")
    
    print(f"\nKategorik özelliklerin (OHE) toplam önemi: %{sum(importances[6:])*100:.2f}")

print("\n\n--- 2. VERİ SETİ KURAL ANALİZİ (Soil_Moisture vs Irrigation_Need) ---")
data_path = r'c:\Users\İlayda Serpil\Desktop\tarım\sulama_sistemi\data\irrigation_prediction.csv'
df = pd.read_csv(data_path)

print(df.groupby('Irrigation_Need')['Soil_Moisture'].describe())
