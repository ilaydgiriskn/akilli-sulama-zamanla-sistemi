import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

def main():
    print("1. Learning Curve Testi Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    model_path = os.path.join(base_dir, 'data', 'water_need_model.pkl')
    out_dir = os.path.join(base_dir, 'scripts', 'advanced_tests')

    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    train_sizes = [0.1, 0.3, 0.5, 0.7, 1.0]
    train_scores = []
    test_scores = []

    for size in train_sizes:
        if size == 1.0:
            X_tr, y_tr = X_train_full, y_train_full
        else:
            X_tr, _, y_tr, _ = train_test_split(X_train_full, y_train_full, train_size=size, random_state=42, stratify=y_train_full)
        
        print(f"Eğitim Seti Boyutu: {len(X_tr)} (Totalin %{int(size*80)})")
        model.fit(X_tr, y_tr)
        
        # Train success
        train_acc = accuracy_score(y_tr, model.predict(X_tr))
        train_scores.append(train_acc)
        
        # Test success (always same test set)
        test_acc = accuracy_score(y_test, model.predict(X_test))
        test_scores.append(test_acc)

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.plot([s * 100 for s in train_sizes], train_scores, 'o-', color="r", label="Eğitim Başarısı")
    plt.plot([s * 100 for s in train_sizes], test_scores, 'o-', color="g", label="Test (Validation) Başarısı")
    plt.title("Learning Curve (Öğrenme Eğrisi)")
    plt.xlabel("Kullanılan Eğitim Verisi Oranı (%)")
    plt.ylabel("Doğruluk (Accuracy)")
    plt.legend(loc="best")
    plt.grid()
    plt.savefig(os.path.join(out_dir, "1_learning_curve.png"))
    plt.close()
    
    print("Sonuçlar:")
    for size, tr, te in zip(train_sizes, train_scores, test_scores):
        print(f"Veri %{int(size*100):3d} -> Train Acc: {tr:.4f} | Test Acc: {te:.4f}")
    
    print("\nSonuç: 1_learning_curve.png olarak kaydedildi.\n")

if __name__ == "__main__":
    main()
