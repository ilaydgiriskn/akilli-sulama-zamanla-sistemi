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
    print("10. Çok Sınıflı (Multiclass) ROC Eğrisi Çizdiriliyor...")
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

    # Sınıflarımız: Low, Medium, High
    classes = ['Low', 'Medium', 'High']
    # ROC çizimi için hedefleri binarize ediyoruz (One-vs-Rest mantığı)
    y_bin = label_binarize(y, classes=classes)
    n_classes = y_bin.shape[1]

    X_train, X_test, y_train, y_test = train_test_split(X, y_bin, test_size=0.2, random_state=42)

    # Modeli çok sınıflı olasılıklar (predict_proba) verecek şekilde eğitelim
    # Zaten model Pipeline içinde. Pipeline'ın içinden y_train'i normal formata geri çevirip vermeliyiz.
    # Ancak elimizdeki model halihazırda eğitilmiş. 
    # Yeniden eğitmeden direkt test seti üzerinden olasılık (predict_proba) alalım:
    
    # y'yi orijinal haliyle ayırıp test edelim (Predict Proba için orijinal etiket lazım)
    _, X_test_orig, _, y_test_orig = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Modelden olasılık tahminleri al
    y_score = model.predict_proba(X_test_orig)
    
    # Binarize edilmiş test setini kullanarak her sınıf için FPR ve TPR hesapla
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Plotting ROC Curve
    plt.figure(figsize=(10, 8))
    colors = ['green', 'orange', 'red']
    
    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=2,
                 label=f'ROC curve of class {classes[i]} (area = {roc_auc[i]:.4f})')

    plt.plot([0, 1], [0, 1], 'k--', lw=2) # Diagonal çizgi (rastgele tahmin)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (Yanlış Pozitif Oranı)')
    plt.ylabel('True Positive Rate (Gerçek Pozitif Oranı)')
    plt.title('Çok Sınıflı (Multiclass) ROC Eğrisi (One-vs-Rest)')
    plt.legend(loc="lower right")
    
    save_path = os.path.join(out_dir, "10_roc_curve.png")
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

    print(f"ROC Eğrisi başarıyla kaydedildi: {save_path}")

if __name__ == "__main__":
    main()
