from pathlib import Path
import pandas as pd


# ============================================================
# 1. CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "regularite_tgv.csv"
)

PROCESSED_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

OUTPUT_FILE = (
    PROCESSED_DIR
    / "delay_ml.csv"
)


# ============================================================
# 2. CHARGEMENT
# ============================================================

print("Chargement des données...")

df = pd.read_csv(
    RAW_FILE,
    sep=";"
)

print("Nombre de lignes initial :", len(df))


# ============================================================
# 3. CONVERSION DE LA DATE
# ============================================================

df["date"] = pd.to_datetime(
    df["date"],
    format="%Y-%m"
)

df["annee"] = df["date"].dt.year
df["mois"] = df["date"].dt.month


# ============================================================
# 4. CREATION DE LA LIAISON
# ============================================================

df["liaison"] = (
    df["gare_depart"]
    + " → "
    + df["gare_arrivee"]
)


# ============================================================
# 5. DEFINITION DE LA CIBLE
# ============================================================

TARGET = "retard_moyen_tous_trains_arrivee"


# ============================================================
# 6. NETTOYAGE DES ANOMALIES EXTREMES
# ============================================================

df = df[
    df[TARGET] >= -60
].copy()

print(
    "Nombre de lignes après nettoyage :",
    len(df)
)


# ============================================================
# 7. SELECTION DES VARIABLES
# ============================================================

columns = [
    "date",
    "annee",
    "mois",
    "service",
    "gare_depart",
    "gare_arrivee",
    "liaison",
    "duree_moyenne",
    "nb_train_prevu",
    TARGET,
]

df_ml = df[columns].copy()


# ============================================================
# 8. TRI CHRONOLOGIQUE
# ============================================================

df_ml = df_ml.sort_values(
    by=["date", "liaison"]
)


# ============================================================
# 9. SAUVEGARDE
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

df_ml.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 10. CONTROLE
# ============================================================

print("\nDataset ML créé.")
print("Dimensions :", df_ml.shape)
print("Période :", df_ml["date"].min(), "→", df_ml["date"].max())

print("\nColonnes :")
print(df_ml.columns.tolist())

print("\nAperçu :")
print(df_ml.head())

print(
    "\nFichier créé :",
    OUTPUT_FILE
)