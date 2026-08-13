import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import warnings
warnings.filterwarnings('ignore')

data_path = r'c:\Users\İlayda Serpil\Desktop\tarım\sulama_sistemi\data\irrigation_prediction.csv'
df = pd.read_csv(data_path)
y = df['Irrigation_Need']

# Feature grupları
env_num = ['Temperature_C', 'Humidity', 'Rainfall_mm', 'Wind_Speed_kmh']
agr_cat = ['Crop_Type', 'Crop_Growth_Stage', 'Season', 'Mulching_Used']
soil_num = ['Soil_Moisture', 'Soil_pH']
soil_cat = ['Soil_Type']

experiments = [
    {"name": "Çevresel", "num": env_num, "cat": []},
    {"name": "Çevresel + Tarımsal", "num": env_num, "cat": agr_cat},
    {"name": "Çevresel + Toprak", "num": env_num + soil_num, "cat": soil_cat},
    {"name": "Tüm 11 Feature", "num": env_num + soil_num, "cat": agr_cat + soil_cat},
    {"name": "Tüm 11 (Soil_Moisture HARİÇ)", "num": env_num + ['Soil_pH'], "cat": agr_cat + soil_cat}
]

def evaluate_ablation(name, num_cols, cat_cols):
    X = df[num_cols + cat_cols]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    transformers = []
    if num_cols:
        transformers.append(('num', StandardScaler(), num_cols))
    if cat_cols:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols))
        
    preprocessor = ColumnTransformer(transformers=transformers)
    
    model = ImbPipeline([
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'))
    ])
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    acc = report['accuracy'] * 100
    macro_f1 = report['macro avg']['f1-score'] * 100
    high_recall = report['High']['recall'] * 100
    
    return acc, macro_f1, high_recall

print(f"{'Model':<30} | {'Accuracy':<10} | {'Macro F1':<10} | {'High Recall'}")
print("-" * 65)

for exp in experiments:
    acc, macro_f1, high_recall = evaluate_ablation(exp['name'], exp['num'], exp['cat'])
    print(f"{exp['name']:<30} | %{acc:<9.2f} | %{macro_f1:<9.2f} | %{high_recall:.2f}")

