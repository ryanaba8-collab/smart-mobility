from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "stops.txt"
CLEAN_DIR = BASE_DIR / "clean"
CLEAN_FILE = CLEAN_DIR / "stations.csv"


def transform_stations():
    import pandas as pd
    print("Lecture des données RAW...")

    stops = pd.read_csv(RAW_FILE)

    print(f"Lignes RAW : {len(stops)}")

    # 1. Garder uniquement les stations
    stations = stops[
        stops["location_type"] == 1
    ].copy()

    # 2. Garder uniquement les colonnes utiles
    stations = stations[
        [
            "stop_id",
            "stop_name",
            "stop_lat",
            "stop_lon",
        ]
    ]

    # 3. Renommer pour notre modèle Smart Mobility
    stations = stations.rename(
        columns={
            "stop_id": "external_id",
            "stop_name": "name",
            "stop_lat": "latitude",
            "stop_lon": "longitude",
        }
    )

    # 4. Nettoyer les noms
    stations["name"] = stations["name"].str.strip()

    # 5. Contrôles qualité
    stations = stations.dropna(
        subset=[
            "external_id",
            "name",
            "latitude",
            "longitude",
        ]
    )

    stations = stations.drop_duplicates(
        subset=["external_id"]
    )

    # 6. Créer le dossier CLEAN
    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # 7. Sauvegarder
    stations.to_csv(
        CLEAN_FILE,
        index=False,
    )

    print(f"Stations CLEAN : {len(stations)}")
    print(f"Fichier créé : {CLEAN_FILE}")


if __name__ == "__main__":
    transform_stations()