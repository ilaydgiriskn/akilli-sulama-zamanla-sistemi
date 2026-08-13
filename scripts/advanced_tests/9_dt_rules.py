import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

def main():
    print("9. Decision Tree Karar Kuralları (Rule Extraction) Çıkarılıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    out_dir = os.path.join(base_dir, 'scripts', 'advanced_tests')

    df = pd.read_csv(data_path)
    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    # Kuralları okuyabilmek için veriyi ölçeklendirmeden (StandardScaler kullanmadan) OHE uygulayacağız
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ], remainder='passthrough'
    )
    
    X_processed = preprocessor.fit_transform(X)
    
    # Yeni feature isimlerini oluşturma
    cat_features = preprocessor.transformers_[0][1].get_feature_names_out(cat_cols)
    feature_names = list(cat_features) + num_cols

    # Sığ bir ağaç (max_depth=3) eğitiyoruz ki kurallar kolayca okunabilsin
    dt = DecisionTreeClassifier(max_depth=3, random_state=42)
    dt.fit(X_processed, y)

    # Kuralları Metin Olarak Dışa Aktar
    tree_rules = export_text(dt, feature_names=feature_names)
    
    rule_file_path = os.path.join(out_dir, "9_dt_rules.txt")
    with open(rule_file_path, "w", encoding="utf-8") as f:
        f.write("Sığ Karar Ağacı (Max Depth=3) ile Öğrenilen Temel Kurallar:\n")
        f.write("="*60 + "\n")
        f.write(tree_rules)
    
    print("\n--- ÇIKARILAN BAZI KURALLAR ---")
    print(tree_rules)
    print(f"\nKurallar {rule_file_path} dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
