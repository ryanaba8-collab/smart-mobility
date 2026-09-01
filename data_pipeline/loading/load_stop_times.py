from pathlib import Path
import uuid
import os

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
STOP_TIMES_FILE = BASE_DIR / "clean" / "stop_times.csv"

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_stop_times():
    print("Lecture des stop_times CLEAN...")

    stop_times = pd.read_csv(STOP_TIMES_FILE)

    print(f"Stop times à charger : {len(stop_times)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        # --------------------------------------------------
        # 1. Charger les correspondances des trips
        # --------------------------------------------------

        print("Chargement des correspondances trips...")

        cursor.execute(
            """
            SELECT external_id, id
            FROM gtfs_trip;
            """
        )

        trip_mapping = dict(cursor.fetchall())

        print(f"Trips disponibles : {len(trip_mapping)}")

        # --------------------------------------------------
        # 2. Charger les correspondances des stop points
        # --------------------------------------------------

        print("Chargement des correspondances stop points...")

        cursor.execute(
            """
            SELECT external_id, id
            FROM stop_point;
            """
        )

        stop_point_mapping = dict(cursor.fetchall())

        print(
            f"Stop points disponibles : "
            f"{len(stop_point_mapping)}"
        )

        # --------------------------------------------------
        # 3. Conversion external_id -> UUID
        # --------------------------------------------------

        stop_times["trip_id"] = (
            stop_times["trip_external_id"]
            .map(trip_mapping)
        )

        stop_times["stop_point_id"] = (
            stop_times["stop_point_external_id"]
            .map(stop_point_mapping)
        )

        # Vérifier les correspondances manquantes
        missing_trip = stop_times["trip_id"].isna().sum()
        missing_stop = stop_times["stop_point_id"].isna().sum()

        print(f"Trips non trouvés : {missing_trip}")
        print(f"Stop points non trouvés : {missing_stop}")

        # On ne charge que les lignes correctement reliées
        stop_times = stop_times.dropna(
            subset=["trip_id", "stop_point_id"]
        )

        # --------------------------------------------------
        # 4. Préparer les données
        # --------------------------------------------------

        rows = []

        for row in stop_times.itertuples(index=False):

            rows.append(
                (
                    str(uuid.uuid4()),
                    row.trip_id,
                    row.stop_point_id,
                    int(row.stop_sequence),
                    int(row.arrival_seconds)
                    if pd.notna(row.arrival_seconds)
                    else None,
                    int(row.departure_seconds)
                    if pd.notna(row.departure_seconds)
                    else None,
                    int(row.pickup_type)
                    if pd.notna(row.pickup_type)
                    else None,
                    int(row.drop_off_type)
                    if pd.notna(row.drop_off_type)
                    else None,
                )
            )

        print(f"Lignes préparées : {len(rows)}")

        # --------------------------------------------------
        # 5. INSERT par lots
        # --------------------------------------------------

        print("Insertion dans PostgreSQL...")

        query = """
            INSERT INTO gtfs_stop_time (
                id,
                trip_id,
                stop_point_id,
                stop_sequence,
                arrival_seconds,
                departure_seconds,
                pickup_type,
                drop_off_type
            )
            VALUES %s

            ON CONFLICT (trip_id, stop_sequence)
            DO UPDATE SET
                stop_point_id = EXCLUDED.stop_point_id,
                arrival_seconds = EXCLUDED.arrival_seconds,
                departure_seconds = EXCLUDED.departure_seconds,
                pickup_type = EXCLUDED.pickup_type,
                drop_off_type = EXCLUDED.drop_off_type,
                updated_at = CURRENT_TIMESTAMP;
        """

        execute_values(
            cursor,
            query,
            rows,
            page_size=5000,
        )

        connection.commit()

        print("Chargement terminé.")
        print(f"Lignes traitées : {len(rows)}")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    load_stop_times()