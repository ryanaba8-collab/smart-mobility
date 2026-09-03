from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


# ============================================================
# 1. CHARGEMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "delay_ml_features.csv"
)

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["date"]
)

print("Dataset chargé :", df.shape)


# ============================================================
# 2. CIBLE
# ============================================================

TARGET = "retard_moyen_tous_trains_arrivee"


# ============================================================
# 3. FEATURES
# ============================================================

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

print("\nTrain :", X_train.shape)
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
# 6. MODELE
# ============================================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "regressor",
            LinearRegression()
        ),
    ]
)


# ============================================================
# 7. ENTRAINEMENT
# ============================================================

print("\nEntraînement du modèle...")

model.fit(
    X_train,
    y_train
)

print("Entraînement terminé.")


# ============================================================
# 8. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)


# ============================================================
# 9. EVALUATION
# ============================================================

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


print("\n=== PERFORMANCE BASELINE ===")

print(
    f"MAE  : {mae:.2f} minutes"
)

print(
    f"RMSE : {rmse:.2f} minutes"
)

print(
    f"R²   : {r2:.3f}"
)


# ============================================================
# 10. EXEMPLES DE PREDICTIONS
# ============================================================

results = df.loc[
    test_mask,
    [
        "date",
        "gare_depart",
        "gare_arrivee",
    ],
].copy()

results["retard_reel"] = y_test.values
results["retard_predit"] = y_pred

results["erreur_absolue"] = (
    results["retard_reel"]
    - results["retard_predit"]
).abs()


print("\n=== EXEMPLES DE PREDICTIONS ===")

print(
    results.head(10).to_string(
        index=False
    )
)
# ============================================================
# 11. RANDOM FOREST
# ============================================================

random_forest = Pipeline(
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
                n_jobs=-1
            )
        ),
    ]
)


# ============================================================
# 12. ENTRAINEMENT RANDOM FOREST
# ============================================================

print("\nEntraînement Random Forest...")

random_forest.fit(
    X_train,
    y_train
)

print("Entraînement terminé.")


# ============================================================
# 13. PREDICTIONS RANDOM FOREST
# ============================================================

y_pred_rf = random_forest.predict(
    X_test
)


# ============================================================
# 14. EVALUATION RANDOM FOREST
# ============================================================

mae_rf = mean_absolute_error(
    y_test,
    y_pred_rf
)

rmse_rf = mean_squared_error(
    y_test,
    y_pred_rf
) ** 0.5

r2_rf = r2_score(
    y_test,
    y_pred_rf
)


print("\n=== RANDOM FOREST ===")

print(
    f"MAE  : {mae_rf:.2f} minutes"
)

print(
    f"RMSE : {rmse_rf:.2f} minutes"
)

print(
    f"R²   : {r2_rf:.3f}"
)


# ============================================================
# 15. COMPARAISON
# ============================================================

print("\n=== COMPARAISON DES MODELES ===")

print(
    f"{'Modèle':<22}"
    f"{'MAE':>10}"
    f"{'RMSE':>10}"
    f"{'R²':>10}"
)

print("-" * 52)

print(
    f"{'Régression linéaire':<22}"
    f"{mae:>10.2f}"
    f"{rmse:>10.2f}"
    f"{r2:>10.3f}"
)

print(
    f"{'Random Forest':<22}"
    f"{mae_rf:>10.2f}"
    f"{rmse_rf:>10.2f}"
    f"{r2_rf:>10.3f}"
)
# ============================================================
# 16. IMPORTANCE DES FEATURES
# ============================================================

print("\n=== IMPORTANCE DES FEATURES ===")

importance = permutation_importance(
    random_forest,
    X_test,
    y_test,
    n_repeats=10,
    random_state=42,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
)

feature_importance = pd.DataFrame(
    {
        "feature": X_test.columns,
        "importance": importance.importances_mean,
        "ecart_type": importance.importances_std,
    }
)

feature_importance = feature_importance.sort_values(
    "importance",
    ascending=False,
)

print(
    feature_importance.to_string(
        index=False
    )
)