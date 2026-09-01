from pathlib import Path
import uuid
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent
TRIPS_FILE = BASE_DIR / "clean" / "trips.csv"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_trips():
    
    print("Lecture des trips CLEAN...")

    trips = pd.read_csv(
    TRIPS_FILE,
    dtype={"service_id": str},
   )

    print(f"Trips à charger : {len(trips)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    try:
        for _, trip in trips.iterrows():

            # Retrouver l'UUID interne de la route
            cursor.execute(
                """
                SELECT id
                FROM route
                WHERE external_id = %s;
                """,
                (trip["route_external_id"],),
            )

            route_row = cursor.fetchone()

            if route_row is None:
                skipped += 1
                continue

            route_id = route_row[0]
            trip_id = str(uuid.uuid4())

            direction_id = (
                int(trip["direction_id"])
                if pd.notna(trip["direction_id"])
                else None
            )

            headsign = (
                str(trip["headsign"])
                if pd.notna(trip["headsign"])
                else None
            )

            cursor.execute(
                """
                INSERT INTO gtfs_trip (
                    id,
                    external_id,
                    route_id,
                    service_id,
                    headsign,
                    direction_id,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
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
                    route_id = EXCLUDED.route_id,
                    service_id = EXCLUDED.service_id,
                    headsign = EXCLUDED.headsign,
                    direction_id = EXCLUDED.direction_id,
                    updated_at = CURRENT_TIMESTAMP

                RETURNING (xmax = 0) AS inserted;
                """,
                (
                    trip_id,
                    trip["external_id"],
                    route_id,
                    str(trip["service_id"]),
                    headsign,
                    direction_id,
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
    print(f"Insérés : {inserted}")
    print(f"Mis à jour : {updated}")
    print(f"Ignorés : {skipped}")


if __name__ == "__main__":
    load_trips()