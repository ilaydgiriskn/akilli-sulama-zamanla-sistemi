import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg') # Force Tkinter backend to avoid Qt errors
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

def main():
    print("Veri ve model yükleniyor...")
    # Dinamik dosya yolları (scripts klasöründen bir üst dizine çıkıp data'ya ulaşıyoruz)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    model_path = os.path.join(base_dir, 'data', 'water_need_model.pkl')

    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    # Veriyi hazırlama
    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Tahminler alınıyor...")
    y_pred = model.predict(X_test)
    classes = model.classes_

    # 1. Confusion Matrix (Karmaşıklık Matrisi)
    print("Karmaşıklık Matrisi çiziliyor...")
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(cm, cmap=plt.cm.Blues)
    fig.colorbar(cax)

    ax.set_xticks(np.arange(len(classes)))
    ax.set_yticks(np.arange(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    ax.xaxis.set_ticks_position('bottom')
    plt.xlabel('Tahmin Edilen Sınıf')
    plt.ylabel('Gerçek Sınıf')
    plt.title('Karmaşıklık Matrisi (Confusion Matrix)')

    # Kutuların içine sayıları yazma
    for i in range(len(classes)):
        for j in range(len(classes)):
            ax.text(j, i, str(cm[i, j]), va='center', ha='center', color='red' if cm[i,j] == 0 else 'black', fontweight='bold')
            
    # Ekranda Göster
    plt.show()

    # 2. Feature Importance (Özellik Önemleri)
    print("Özellik Önemleri çiziliyor...")
    preprocessor = model.named_steps['preprocessor']
    cat_features = preprocessor.transformers_[1][1].get_feature_names_out(cat_cols)
    feature_names = num_cols + list(cat_features)

    rf_model = model.named_steps['classifier']
    importances = rf_model.feature_importances_

    indices = np.argsort(importances)
    top_n = min(15, len(feature_names))
    top_indices = indices[-top_n:]
    top_features = [feature_names[i] for i in top_indices]
    top_importances = importances[top_indices]

    plt.figure(figsize=(10, 8))
    plt.barh(top_features, top_importances, color='skyblue')
    plt.title('Makine Öğrenmesinde En Önemli Faktörler (Feature Importance)')
    plt.xlabel('Önem Derecesi (Göreceli)')
    plt.ylabel('Özellik')
    
    # Ekranda Göster
    plt.show()
    
    print("İşlem tamamlandı!")

if __name__ == "__main__":
    main()
