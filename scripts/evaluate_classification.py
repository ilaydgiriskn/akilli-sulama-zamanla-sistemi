import pandas as pd
import os
import joblib
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def main():
    print("="*50)
    print("   SINIFLANDIRMA METRİKLERİ TESTİ (KARAR MOTORU)")
    print("="*50)
    
    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'water_need_model.pkl')
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    
    model = joblib.load(model_path)
    df = pd.read_csv(data_path)
    
    # ML Modeli mm cinsinden "Regresyon" (sayısal) tahmini yapıyor.
    # Ancak F1, Accuracy gibi metrikler "Sınıflandırma" (Evet/Hayır) için kullanılır.
    # Bu yüzden modelimizin ürettiği mm değerini ve gerçek verideki durumu "Evet/Hayır" kararına çeviriyoruz:
    
    # 1. Gerçek Durum (True Labels): Verisetinde 'Low' olanlara Sulama Gerekmez (0), Medium/High olanlara Gerekir (1) diyelim.
    y_true = df['Irrigation_Need'].apply(lambda x: 0 if x == 'Low' else 1)
    
    # 2. Modelin Tahmini (Predicted Labels): Modelimizin tahmin ettiği su ihtiyacı belli bir eşiğin üzerindeyse (örn: 4.5 mm) Sula (1), altındaysa Sulama (0) kararı verdirelim.
    X = df[['Temperature_C', 'Humidity', 'Rainfall_mm', 'Crop_Type']]
    y_pred_mm = model.predict(X)
    
    # Karar Motoru Mantığı: İhtiyaç > 4.5 mm ise SULA (1), değilse SULAMA (0)
    y_pred = [1 if val > 4.5 else 0 for val in y_pred_mm]
    
    # Metrikleri Hesapla
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print("\n[HİBRİT SİSTEM NİHAİ KARAR BAŞARISI]")
    print(f"Doğruluk (Accuracy)   : %{acc*100:.2f}")
    print(f"Kesinlik (Precision)  : %{prec*100:.2f}")
    print(f"Duyarlılık (Recall)   : %{rec*100:.2f}")
    print(f"F1 Skoru (F1-Score)   : %{f1*100:.2f}")
    print("\nNot: Bu metrikler, Regression (mm tahmini) modelinin Karar Motoru (Rule Engine) ile birleştirilmiş nihai hibrit karar performansı üzerinden hesaplanmıştır.")

if __name__ == "__main__":
    main()
