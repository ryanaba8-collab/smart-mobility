from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "clean"


# Nombre minimum de lignes attendu pour chaque dataset.
# Ces seuils sont volontairement inférieurs aux volumes habituels SNCF
# afin de détecter une chute anormale sans être trop stricts.
QUALITY_RULES = {
    "stations.csv": 3000,
    "stop_points.csv": 5000,
    "routes.csv": 500,
    "trips.csv": 30000,
    "stop_times.csv": 300000,
    "calendar_dates.csv": 100000,
}


def check_data_quality():

    print("=== CONTRÔLE DE QUALITÉ DES DONNÉES ===")

    errors = []

    for filename, minimum_rows in QUALITY_RULES.items():

        file_path = CLEAN_DIR / filename

        # Vérifie que le fichier existe
        if not file_path.exists():
            errors.append(f"{filename} : fichier introuvable")
            continue

        # Compte les lignes sans charger tout le CSV en mémoire
        with open(file_path, "r", encoding="utf-8") as file:
            row_count = sum(1 for _ in file) - 1

        print(
            f"{filename} : {row_count} lignes "
            f"(minimum attendu : {minimum_rows})"
        )

        if row_count < minimum_rows:
            errors.append(
                f"{filename} : seulement {row_count} lignes "
                f"(minimum : {minimum_rows})"
            )

    if errors:
        print("\n❌ DATA QUALITY FAILED")

        for error in errors:
            print(f"- {error}")

        raise ValueError(
            "Les contrôles de qualité des données ont échoué."
        )

    print("\n✅ DATA QUALITY PASSED")