import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_target(df):
    need_map = {'Low': 3.0, 'Medium': 5.5, 'High': 8.5}
    base = df['Irrigation_Need'].map(need_map)
    temp_effect = (df['Temperature_C'] - 25) * 0.15
    humidity_effect = (df['Humidity'] - 50) * -0.05
    return (base + temp_effect + humidity_effect).clip(lower=0.5, upper=15.0)

def main():
    print("="*60)
    print("   MAKİNE ÖĞRENMESİ MODEL KARŞILAŞTIRMASI")
    print("="*60)
    
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'irrigation_prediction.csv')
    df = pd.read_csv(data_path)
    
    df['Water_Need_mm'] = create_synthetic_target(df)
    
    X = df[['Temperature_C', 'Humidity', 'Rainfall_mm', 'Crop_Type']]
    y = df['Water_Need_mm']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), ['Temperature_C', 'Humidity', 'Rainfall_mm']),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['Crop_Type'])
        ])
        
    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
    }
    
    results = {}
    
    for name, model_algo in models.items():
        print(f"{name} modeli eğitiliyor...")
        model = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model_algo)
        ])
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {'MAE': mae, 'RMSE': rmse, 'R2': r2}
        
    print("\n" + "="*60)
    print(f"{'Model':<20} | {'MAE':<10} | {'RMSE':<10} | {'R² Skor':<10}")
    print("-" * 60)
    
    for name, metrics in results.items():
        print(f"{name:<20} | {metrics['MAE']:.4f} mm | {metrics['RMSE']:.4f} mm | {metrics['R2']:.4f}")
        
    print("="*60)

if __name__ == "__main__":
    main()
