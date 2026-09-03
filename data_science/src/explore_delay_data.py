from pathlib import Path
import pandas as pd


# ============================================================
# 1. CHEMIN VERS LE DATASET
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = BASE_DIR / "data" / "raw" / "regularite_tgv.csv"


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

print("Lecture du dataset...\n")

df = pd.read_csv(DATA_FILE, sep=";")


# ============================================================
# 3. DIMENSIONS DU DATASET
# ============================================================

print("=== DIMENSIONS ===")
print(df.shape)


# ============================================================
# 4. LISTE DES COLONNES
# ============================================================

print("\n=== COLONNES ===")

for i, column in enumerate(df.columns, start=1):
    print(f"{i}. {column}")


# ============================================================
# 5. APERCU DES DONNEES
# ============================================================

print("\n=== APERÇU ===")
print(df.head())


# ============================================================
# 6. TYPES DES VARIABLES
# ============================================================

print("\n=== TYPES ===")
print(df.dtypes)


# ============================================================
# 7. VALEURS MANQUANTES
# ============================================================

print("\n=== VALEURS MANQUANTES ===")
print(df.isna().sum())


# ============================================================
# 8. PERIODE COUVERTE
# ============================================================

print("\n=== PERIODE ===")

print("Date min :", df["date"].min())
print("Date max :", df["date"].max())


# ============================================================
# 9. SERVICES
# ============================================================

print("\n=== SERVICES ===")
print(df["service"].value_counts())


# ============================================================
# 10. CARDINALITE
# ============================================================

print("\n=== CARDINALITE ===")

print(
    "Gares de départ :",
    df["gare_depart"].nunique()
)

print(
    "Gares d'arrivée :",
    df["gare_arrivee"].nunique()
)

print(
    "Liaisons différentes :",
    df[
        ["gare_depart", "gare_arrivee"]
    ]
    .drop_duplicates()
    .shape[0]
)


# ============================================================
# 11. RETARD MOYEN DES TRAINS EN RETARD
# ============================================================

print("\n=== RETARD MOYEN DES TRAINS EN RETARD ===")

print(
    df["retard_moyen_arrivee"]
    .describe()
)


# ============================================================
# 12. CIBLE POTENTIELLE :
#     RETARD MOYEN DE TOUS LES TRAINS
# ============================================================

print("\n=== CIBLE : RETARD MOYEN TOUS TRAINS ===")

print(
    df["retard_moyen_tous_trains_arrivee"]
    .describe()
)


# ============================================================
# 13. COMPARAISON DES DEUX VARIABLES DE RETARD
# ============================================================

print("\n=== EXEMPLES ===")

colonnes_exemple = [
    "date",
    "gare_depart",
    "gare_arrivee",
    "nb_train_prevu",
    "retard_moyen_arrivee",
    "retard_moyen_tous_trains_arrivee",
]

print(
    df[colonnes_exemple]
    .head(10)
)
# ============================================================
# 14. CONTROLE DES VALEURS EXTREMES DE LA CIBLE
# ============================================================

print("\n=== VALEURS EXTREMES DE LA CIBLE ===")

colonnes_extremes = [
    "date",
    "gare_depart",
    "gare_arrivee",
    "nb_train_prevu",
    "retard_moyen_tous_trains_arrivee",
]

print("\n5 plus petites valeurs :")

print(
    df[colonnes_extremes]
    .sort_values("retard_moyen_tous_trains_arrivee")
    .head(5)
)

print("\n5 plus grandes valeurs :")

print(
    df[colonnes_extremes]
    .sort_values(
        "retard_moyen_tous_trains_arrivee",
        ascending=False
    )
    .head(5)
)
target = "retard_moyen_tous_trains_arrivee"

print("\n=== REPARTITION DES VALEURS NEGATIVES ===")

print("Valeurs < 0 min :", (df[target] < 0).sum())
print("Valeurs < -5 min :", (df[target] < -5).sum())
print("Valeurs < -15 min :", (df[target] < -15).sum())
print("Valeurs < -60 min :", (df[target] < -60).sum())

print("\n=== REPARTITION DES FORTS RETARDS ===")

print("Valeurs > 15 min :", (df[target] > 15).sum())
print("Valeurs > 30 min :", (df[target] > 30).sum())
print("Valeurs > 60 min :", (df[target] > 60).sum())