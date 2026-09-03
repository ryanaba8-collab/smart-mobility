from pathlib import Path
import pandas as pd


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "delay_ml.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "delay_ml_features.csv"
)


# ============================================================
# 2. CHARGEMENT
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["date"]
)

print("Dataset chargé :", df.shape)


# ============================================================
# 3. TRI CHRONOLOGIQUE PAR LIAISON
# ============================================================

df = df.sort_values(
    ["liaison", "date"]
).copy()


# ============================================================
# 4. CIBLE
# ============================================================

TARGET = "retard_moyen_tous_trains_arrivee"


# ============================================================
# 5. RETARD DU MOIS PRECEDENT
# ============================================================

df["retard_mois_precedent"] = (
    df.groupby("liaison")[TARGET]
    .shift(1)
)


# ============================================================
# 6. MOYENNE DES 3 MOIS PRECEDENTS
# ============================================================

df["retard_moyen_3_mois"] = (
    df.groupby("liaison")[TARGET]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=3,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# 7. MOYENNE DES 6 MOIS PRECEDENTS
# ============================================================

df["retard_moyen_6_mois"] = (
    df.groupby("liaison")[TARGET]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(
            window=6,
            min_periods=1
        )
        .mean()
    )
)


# ============================================================
# 8. SUPPRESSION DES LIGNES SANS HISTORIQUE
# ============================================================

print(
    "\nValeurs manquantes avant nettoyage :"
)

print(
    df[
        [
            "retard_mois_precedent",
            "retard_moyen_3_mois",
            "retard_moyen_6_mois",
        ]
    ].isna().sum()
)

df = df.dropna(
    subset=["retard_mois_precedent"]
).copy()


# ============================================================
# 9. SAUVEGARDE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 10. CONTROLE
# ============================================================

print(
    "\nDataset après feature engineering :",
    df.shape
)

print("\nNouvelles features :")

print(
    df[
        [
            "date",
            "liaison",
            TARGET,
            "retard_mois_precedent",
            "retard_moyen_3_mois",
            "retard_moyen_6_mois",
        ]
    ].head(10).to_string(index=False)
)

print(
    "\nFichier créé :",
    OUTPUT_FILE
)