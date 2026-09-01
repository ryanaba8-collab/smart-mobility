from pathlib import Path
import uuid
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent
STOP_POINTS_FILE = BASE_DIR / "clean" / "stop_points.csv"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_stop_points():
    import pandas as pd
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    print("Lecture des stop_points CLEAN...")

    stop_points = pd.read_csv(STOP_POINTS_FILE)

    print(f"Stop points à charger : {len(stop_points)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    try:
        for _, stop_point in stop_points.iterrows():

            # Retrouver l'UUID de la gare par son external_id
            cursor.execute(
                """
                SELECT id
                FROM station
                WHERE external_id = %s;
                """,
                (stop_point["station_external_id"],),
            )

            station_row = cursor.fetchone()

            if station_row is None:
                skipped += 1
                continue

            station_id = station_row[0]
            stop_point_id = str(uuid.uuid4())

            cursor.execute(
                """
                INSERT INTO stop_point (
                    id,
                    external_id,
                    station_id,
                    name,
                    created_at,
                    updated_at
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT (external_id)
                DO UPDATE SET
                    station_id = EXCLUDED.station_id,
                    name = EXCLUDED.name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING (xmax = 0) AS inserted;
                """,
                (
                    stop_point_id,
                    stop_point["external_id"],
                    station_id,
                    stop_point["name"],
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
    load_stop_points()