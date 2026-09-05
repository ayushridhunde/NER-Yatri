import os
import json
import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
import joblib

from ai.datasets.synthetic_generator import generate_northeast_landslide_dataset

FEATURE_COLUMNS = [
    "slope",
    "elevation",
    "rainfall_24h",
    "rainfall_12h",
    "rainfall_6h",
    "rainfall_1h",
    "soil_moisture",
    "soil_type",
    "geology",
    "vegetation_ndvi",
    "land_use",
    "historical_landslide_density"
]

def train_and_export_model():
    os.makedirs("ai/models", exist_ok=True)
    os.makedirs("ai/datasets", exist_ok=True)

    print("Generating Northeast India Landslide Dataset...")
    df = generate_northeast_landslide_dataset(n_samples=6000)
    dataset_csv = "ai/datasets/northeast_landslide_training_data.csv"
    df.to_csv(dataset_csv, index=False)

    # Prepare features and target
    X = df[FEATURE_COLUMNS]
    # Binary threshold for high risk/critical vs manageable, plus multi-class mapping
    # Classes: 0: LOW, 1: MEDIUM, 2: HIGH, 3: VERY HIGH
    class_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "VERY HIGH": 3}
    y = df["risk_level"].map(class_map)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Random Forest Landslide Susceptibility Classifier...")
    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"Model Accuracy on Test Set: {acc:.4f}")
    report = classification_report(y_test, y_pred, target_names=["LOW", "MEDIUM", "HIGH", "VERY HIGH"], output_dict=True)

    # Compute Feature Importances
    importances = dict(zip(FEATURE_COLUMNS, [round(float(v), 4) for v in model.feature_importances_]))
    sorted_importances = dict(sorted(importances.items(), key=lambda item: item[1], reverse=True))

    model_path = "ai/models/landslide_model.joblib"
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

    metadata = {
        "model_name": "NER-YATRI Random Forest Landslide Risk Estimator",
        "version": "1.0-demo",
        "type": "RandomForestClassifier",
        "features": FEATURE_COLUMNS,
        "feature_importances": sorted_importances,
        "training_date": datetime.datetime.utcnow().isoformat() + "Z",
        "dataset_source": "Demonstration Dataset (Calibrated for Northeast Terrain)",
        "source_type": "DEMO",
        "accuracy": round(float(acc), 4),
        "f1_macro": round(float(report["macro avg"]["f1-score"]), 4),
        "prediction_window": "6–24 hours",
        "risk_thresholds": {
            "LOW": "0 - 25%",
            "MEDIUM": "25 - 50%",
            "HIGH": "50 - 75%",
            "VERY HIGH": "75 - 100%"
        },
        "disclaimer": "Predicted risk for 6–24 hours. Demonstration model calibrated on terrain physics."
    }

    meta_path = "ai/models/model_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {meta_path}")

    return model, metadata

if __name__ == "__main__":
    train_and_export_model()
