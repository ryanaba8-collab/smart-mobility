from pathlib import Path

import joblib
import pandas as pd


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "delay_random_forest.joblib"
)


# ============================================================
# 2. CHARGEMENT DU MODELE
# ============================================================

print("Chargement du modèle...")

model = joblib.load(
    MODEL_FILE
)

print("Modèle chargé.")


# ============================================================
# 3. DONNEE A PREDIRE
# ============================================================

sample = pd.DataFrame(
    [
        {
            "annee": 2026,
            "mois": 7,
            "duree_moyenne": 125,
            "nb_train_prevu": 300,
            "retard_mois_precedent": 6.5,
            "retard_moyen_3_mois": 7.1,
            "retard_moyen_6_mois": 6.8,
            "service": "National",
            "gare_depart": "BORDEAUX ST JEAN",
            "gare_arrivee": "PARIS MONTPARNASSE",
        }
    ]
)


# ============================================================
# 4. PREDICTION
# ============================================================

prediction = model.predict(
    sample
)

retard_predit = prediction[0]


# ============================================================
# 5. RESULTAT
# ============================================================

print("\n=== PREDICTION ===")

print(
    f"Retard moyen prédit : "
    f"{retard_predit:.2f} minutes"
)