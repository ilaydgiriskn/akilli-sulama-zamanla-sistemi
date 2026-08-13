import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def main():
    print("8. Baseline Model Karşılaştırması Başlıyor...")
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'irrigation_prediction.csv')

    df = pd.read_csv(data_path)
    y = df['Irrigation_Need']
    num_cols = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh', 'Soil_Moisture', 'Soil_pH']
    cat_cols = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used', 'Soil_Type']
    X = df[num_cols + cat_cols]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # SMOTENC kullanmadan sadece standart Scaler ve OHE kullanacağız
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), num_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
        ])
    
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    models = {
        "Dummy (Çoğunluk Sınıfı)": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree (Basit Ağaç)": DecisionTreeClassifier(random_state=42),
        "Random Forest (Mevcut Model)": RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    }

    print("\n--- BASELINE KARŞILAŞTIRMA SONUÇLARI ---")
    for name, model in models.items():
        model.fit(X_train_processed, y_train)
        y_pred = model.predict(X_test_processed)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='macro')
        print(f"{name:<30}: Accuracy = %{acc*100:.2f} | Macro F1 = %{f1*100:.2f}")

if __name__ == "__main__":
    main()
