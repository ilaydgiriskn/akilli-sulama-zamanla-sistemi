import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
import joblib

def main():
    print("10. ROC Eğrisi (ROC Curve) Çizimi Başlıyor...")
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

    # Sınıfları binarize ediyoruz (One-vs-Rest için gerekli)
    classes = model.classes_
    y_bin = label_binarize(y, classes=classes)
    n_classes = y_bin.shape[1]

    X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42, stratify=y)

    print("Tahmin olasılıkları (predict_proba) alınıyor...")
    y_score = model.predict_proba(X_test)

    # Her sınıf için ROC eğrisi ve AUC hesaplama
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    colors = ['blue', 'green', 'red']
    
    plt.figure(figsize=(10, 8))
    
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        
        plt.plot(fpr[i], tpr[i], color=colors[i], lw=2,
                 label=f'ROC eğrisi: {classes[i]} (AUC = %0.3f)' % roc_auc[i])

    # Şans çizgisi
    plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Şans (%50)')
    
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Yanlış Pozitif Oranı (False Positive Rate)')
    plt.ylabel('Gerçek Pozitif Oranı (True Positive Rate)')
    plt.title('Çok Sınıflı ROC Eğrisi (One-vs-Rest)')
    plt.legend(loc="lower right")
    
    roc_path = os.path.join(out_dir, "10_roc_curve.png")
    plt.savefig(roc_path, bbox_inches='tight')
    plt.close()
    
    print(f"ROC Eğrisi {roc_path} olarak başarıyla kaydedildi.")

if __name__ == "__main__":
    main()
