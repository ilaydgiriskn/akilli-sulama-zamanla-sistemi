import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize


def main():

    print("Çok Sınıflı ROC Eğrisi Çizdiriliyor...")

    # Proje ana klasörü
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )
    )

    data_path = os.path.join(
        base_dir,
        'data',
        'irrigation_prediction.csv'
    )

    model_path = os.path.join(
        base_dir,
        'data',
        'water_need_model.pkl'
    )

    out_dir = os.path.join(
        base_dir,
        'scripts',
        'advanced_tests'
    )

    # Veri ve model
    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    y = df['Irrigation_Need']

    num_cols = [
        'Temperature_C',
        'Humidity',
        'Rainfall_mm',
        'Wind_Speed_kmh',
        'Soil_Moisture',
        'Soil_pH'
    ]

    cat_cols = [
        'Crop_Type',
        'Crop_Growth_Stage',
        'Season',
        'Mulching_Used',
        'Soil_Type'
    ]

    X = df[num_cols + cat_cols]

    # MODELİN GERÇEK SINIF SIRALAMASI
    classes = model.classes_

    print("\nModel sınıf sırası:")
    print(classes)

    # Eğitimdekiyle aynı mantıkla split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # Gerçek sınıfları binary hale getir
    y_test_bin = label_binarize(
        y_test,
        classes=classes
    )

    # Model olasılıkları
    y_score = model.predict_proba(X_test)

    # ROC değerleri
    fpr = {}
    tpr = {}
    roc_auc = {}

    for i, class_name in enumerate(classes):

        fpr[i], tpr[i], _ = roc_curve(
            y_test_bin[:, i],
            y_score[:, i]
        )

        roc_auc[i] = auc(
            fpr[i],
            tpr[i]
        )

        print(
            f"{class_name} AUC: "
            f"{roc_auc[i]:.4f}"
        )

    # Grafik
    plt.figure(figsize=(10, 8))

    colors = ['red', 'green', 'orange']

    for i, color in zip(range(len(classes)), colors):

        plt.plot(
            fpr[i],
            tpr[i],
            lw=2,
            color=color,
            label=(
                f'{classes[i]} '
                f'(AUC = {roc_auc[i]:.4f})'
            )
        )

    # Rastgele tahmin çizgisi
    plt.plot(
        [0, 1],
        [0, 1],
        'k--',
        lw=2,
        label='Rastgele Tahmin'
    )

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])

    plt.xlabel(
        'False Positive Rate (Yanlış Pozitif Oranı)'
    )

    plt.ylabel(
        'True Positive Rate (Doğru Pozitif Oranı)'
    )

    plt.title(
        'Çok Sınıflı ROC Eğrisi (One-vs-Rest)'
    )

    plt.legend(loc='lower right')

    save_path = os.path.join(
        out_dir,
        '10_roc_curve_corrected.png'
    )

    plt.savefig(
        save_path,
        bbox_inches='tight',
        dpi=300
    )

    plt.close()

    print(
        f"\nROC eğrisi kaydedildi:\n{save_path}"
    )


if __name__ == "__main__":
    main()