import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib, os, json

def train_risk_model(filepath="data/geocoded_accidents.csv"):
    df = pd.read_csv(filepath)

    feature_cols = [
        "hour", "month", "day_enc", "road_type_enc",
        "weather_enc", "road_cond_enc", "lighting_enc",
        "alcohol", "num_vehicles", "num_casualties"
    ]

    df = df.dropna(subset=feature_cols)
    X  = df[feature_cols]
    y  = df["severity"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(
        n_estimators=200, max_depth=12,
        random_state=42, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    print("="*50)
    print(f"✅ Accuracy: {round(acc*100,2)}%")
    print("="*50)
    print(classification_report(y_test, y_pred, target_names=["Minor","Serious","Fatal"]))

    importances = pd.Series(model.feature_importances_, index=feature_cols)
    print("Feature Importances:")
    for feat, imp in importances.sort_values(ascending=False).items():
        print(f"  {feat:<30} {'█'*int(imp*50)} {round(imp,4)}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(model,        "models/risk_model.pkl")
    joblib.dump(feature_cols, "models/feature_cols.pkl")
    print("\n✅ Model saved.")

if __name__ == "__main__":
    train_risk_model()