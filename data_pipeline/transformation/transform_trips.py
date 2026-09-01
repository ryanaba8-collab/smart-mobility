from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent

TRIPS_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "trips.txt"
OUTPUT_FILE = BASE_DIR / "clean" / "trips.csv"


def transform_trips():
    import pandas as pd
    print("Lecture des trips RAW...")

    trips = pd.read_csv(
    TRIPS_FILE,
    dtype={"service_id": str},
)

    print(f"Trips RAW : {len(trips)}")

    trips = trips[
        [
            "trip_id",
            "route_id",
            "service_id",
            "trip_headsign",
            "direction_id",
        ]
    ].copy()

    trips = trips.rename(
        columns={
            "trip_id": "external_id",
            "route_id": "route_external_id",
            "trip_headsign": "headsign",
        }
    )

    # Un trajet doit obligatoirement avoir ces informations
    trips = trips.dropna(
        subset=[
            "external_id",
            "route_external_id",
            "service_id",
        ]
    )

    # trip_id est l'identifiant unique GTFS du trajet
    trips = trips.drop_duplicates(
        subset=["external_id"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    trips.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Trips transformés : {len(trips)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_trips()