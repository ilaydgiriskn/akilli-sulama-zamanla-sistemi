import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("7. Feature Distribution Analizi Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')
    out_dir = os.path.join(base_dir, 'scripts', 'advanced_tests')

    df = pd.read_csv(data_path)

    # 1. Boxplot: Soil_Moisture vs Irrigation_Need
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Irrigation_Need', y='Soil_Moisture', data=df, order=['Low', 'Medium', 'High'])
    plt.title('Toprak Nemi Dağılımı (Sınıflara Göre)')
    plt.xlabel('Sulama İhtiyacı')
    plt.ylabel('Toprak Nemi (%)')
    plt.savefig(os.path.join(out_dir, "7_dist_soil_moisture.png"))
    plt.close()

    # 2. Boxplot: Rainfall_mm vs Irrigation_Need
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Irrigation_Need', y='Rainfall_mm', data=df, order=['Low', 'Medium', 'High'])
    plt.title('Yağış Miktarı Dağılımı (Sınıflara Göre)')
    plt.xlabel('Sulama İhtiyacı')
    plt.ylabel('Yağış (mm)')
    plt.savefig(os.path.join(out_dir, "7_dist_rainfall.png"))
    plt.close()

    # 3. Countplot: Crop_Growth_Stage vs Irrigation_Need
    plt.figure(figsize=(10, 6))
    sns.countplot(x='Crop_Growth_Stage', hue='Irrigation_Need', data=df, hue_order=['Low', 'Medium', 'High'])
    plt.title('Büyüme Evresi Dağılımı (Sınıflara Göre)')
    plt.xlabel('Büyüme Evresi')
    plt.ylabel('Kayıt Sayısı')
    plt.legend(title='Sulama İhtiyacı')
    plt.savefig(os.path.join(out_dir, "7_dist_growth_stage.png"))
    plt.close()
    
    print("Grafikler (7_dist_*.png) başarıyla kaydedildi.")

if __name__ == "__main__":
    main()
