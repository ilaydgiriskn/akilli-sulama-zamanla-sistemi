import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTENC
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings
warnings.filterwarnings('ignore')

data_path = r'c:\Users\İlayda Serpil\Desktop\tarım\sulama_sistemi\data\irrigation_prediction.csv'
df = pd.read_csv(data_path)
y = df['Irrigation_Need']

num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
X = df[num_cols + cat_cols]

cat_indices = [X.columns.get_loc(col) for col in cat_cols]

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])

model = ImbPipeline([
    ('smotenc', SMOTENC(categorical_features=cat_indices, random_state=42)),
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
])

print("--- 5-FOLD CROSS VALIDATION (ÇAPRAZ DOĞRULAMA) BAŞLIYOR ---")
print("Her bir fold (katman) için eğitim ve test yapılıyor. Lütfen bekleyin...")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', n_jobs=-1)

for i, score in enumerate(scores):
    print(f"Fold {i+1} -> %{score*100:.2f}")

print(f"\nOrtalama Accuracy -> %{np.mean(scores)*100:.2f} ± %{np.std(scores)*100:.2f}")
if np.std(scores) < 0.02:
    print("Sonuç: Düşük standart sapma! Model başarısı şans değil, istikrarlı ve güvenilir.")
else:
    print("Sonuç: Yüksek standart sapma. Model bazı veri kümelerinde zorlanıyor.")
