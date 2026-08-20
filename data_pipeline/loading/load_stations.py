from pathlib import Path
import uuid

import pandas as pd
import psycopg2
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
STATIONS_FILE = BASE_DIR / "clean" / "stations.csv"


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def load_stations():
    print("Lecture des stations CLEAN...")

    stations = pd.read_csv(STATIONS_FILE)

    print(f"Stations à charger : {len(stations)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    inserted = 0
    updated = 0

    try:
        for _, station in stations.iterrows():

            station_id = str(uuid.uuid4())

            cursor.execute(
                """
                INSERT INTO station (
                    id,
                    external_id,
                    name,
                    latitude,
                    longitude,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (external_id)
                DO UPDATE SET
                    name = EXCLUDED.name,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    updated_at = CURRENT_TIMESTAMP

                RETURNING (xmax = 0) AS inserted;
                """,
                (
                    station_id,
                    station["external_id"],
                    station["name"],
                    float(station["latitude"]),
                    float(station["longitude"]),
                ),
            )

            was_inserted = cursor.fetchone()[0]

            if was_inserted:
                inserted += 1
            else:
                updated += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    print("Chargement terminé.")
    print(f"Insérées : {inserted}")
    print(f"Mises à jour : {updated}")


if __name__ == "__main__":
    load_stations()