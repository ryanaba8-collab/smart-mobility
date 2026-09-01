from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent

STOPS_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "stops.txt"
OUTPUT_FILE = BASE_DIR / "clean" / "stop_points.csv"


def transform_stop_points():
    import pandas as pd
    print("Lecture des stops RAW...")

    stops = pd.read_csv(STOPS_FILE)

    # On conserve uniquement les points d'arrêt.
    stop_points = stops[
        stops["location_type"] == 0
    ].copy()

    # On ne garde que les informations utiles à notre modèle.
    stop_points = stop_points[
        [
            "stop_id",
            "stop_name",
            "parent_station",
        ]
    ]

    stop_points = stop_points.rename(
        columns={
            "stop_id": "external_id",
            "stop_name": "name",
            "parent_station": "station_external_id",
        }
    )

    # Un StopPoint sans gare parente ne pourra pas être
    # rattaché à notre table station.
    stop_points = stop_points.dropna(
        subset=["external_id", "station_external_id"]
    )

    # Protection contre les doublons.
    stop_points = stop_points.drop_duplicates(
        subset=["external_id"]
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    stop_points.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Stop points transformés : {len(stop_points)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_stop_points()