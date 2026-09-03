from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "delay_ml_features.csv"
)

MODEL_DIR = BASE_DIR / "models"

MODEL_FILE = (
    MODEL_DIR
    / "delay_random_forest.joblib"
)

METRICS_FILE = (
    MODEL_DIR
    / "delay_random_forest_metrics.json"
)


# ============================================================
# 2. CHARGEMENT
# ============================================================

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["date"]
)

print("Dataset chargé :", df.shape)


# ============================================================
# 3. VARIABLES
# ============================================================

TARGET = "retard_moyen_tous_trains_arrivee"

NUMERIC_FEATURES = [
    "annee",
    "mois",
    "duree_moyenne",
    "nb_train_prevu",
    "retard_mois_precedent",
    "retard_moyen_3_mois",
    "retard_moyen_6_mois",
]

CATEGORICAL_FEATURES = [
    "service",
    "gare_depart",
    "gare_arrivee",
]

FEATURES = (
    NUMERIC_FEATURES
    + CATEGORICAL_FEATURES
)

X = df[FEATURES]
y = df[TARGET]


# ============================================================
# 4. SPLIT TEMPOREL
# ============================================================

cutoff_date = pd.Timestamp("2025-01-01")

train_mask = df["date"] < cutoff_date
test_mask = df["date"] >= cutoff_date

X_train = X[train_mask]
X_test = X[test_mask]

y_train = y[train_mask]
y_test = y[test_mask]

print("Train :", X_train.shape)
print("Test  :", X_test.shape)


# ============================================================
# 5. PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            "passthrough",
            NUMERIC_FEATURES,
        ),
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            CATEGORICAL_FEATURES,
        ),
    ]
)


# ============================================================
# 6. MODELE FINAL
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
            )
        ),
    ]
)


# ============================================================
# 7. ENTRAINEMENT
# ============================================================

print("\nEntraînement du modèle final...")

model.fit(
    X_train,
    y_train
)


# ============================================================
# 8. EVALUATION
# ============================================================

y_pred = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\n=== PERFORMANCE MODELE FINAL ===")

print(f"MAE  : {mae:.2f} minutes")
print(f"RMSE : {rmse:.2f} minutes")
print(f"R²   : {r2:.3f}")


# ============================================================
# 9. CREATION DU DOSSIER MODELS
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 10. SAUVEGARDE DU MODELE
# ============================================================

joblib.dump(
    model,
    MODEL_FILE
)


# ============================================================
# 11. SAUVEGARDE DES METRIQUES
# ============================================================

metrics = {
    "model": "RandomForestRegressor",
    "target": TARGET,
    "cutoff_date": str(cutoff_date.date()),
    "train_observations": len(X_train),
    "test_observations": len(X_test),
    "mae_minutes": round(mae, 4),
    "rmse_minutes": round(rmse, 4),
    "r2": round(r2, 4),
    "features": FEATURES,
}

with open(
    METRICS_FILE,
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        metrics,
        file,
        indent=4,
        ensure_ascii=False,
    )


# ============================================================
# 12. CONTROLE
# ============================================================

print("\nModèle sauvegardé :")
print(MODEL_FILE)

print("\nMétriques sauvegardées :")
print(METRICS_FILE)