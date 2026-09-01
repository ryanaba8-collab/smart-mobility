from pathlib import Path
import uuid
import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
load_dotenv()



BASE_DIR = Path(__file__).resolve().parent.parent
ROUTES_FILE = BASE_DIR / "clean" / "routes.csv"

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_routes():
    
    print("Lecture des routes CLEAN...")

    routes = pd.read_csv(ROUTES_FILE)

    print(f"Routes à charger : {len(routes)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    inserted = 0
    updated = 0

    try:
        for _, route in routes.iterrows():

            route_id = str(uuid.uuid4())

            cursor.execute(
                """
                INSERT INTO route (
                    id,
                    external_id,
                    agency_id,
                    short_name,
                    long_name,
                    route_type,
                    color,
                    text_color,
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
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )

                ON CONFLICT (external_id)
                DO UPDATE SET
                    agency_id = EXCLUDED.agency_id,
                    short_name = EXCLUDED.short_name,
                    long_name = EXCLUDED.long_name,
                    route_type = EXCLUDED.route_type,
                    color = EXCLUDED.color,
                    text_color = EXCLUDED.text_color,
                    updated_at = CURRENT_TIMESTAMP

                RETURNING (xmax = 0) AS inserted;
                """,
                (
                    route_id,
                    route["external_id"],
                    str(route["agency_id"]),
                    route["short_name"] if pd.notna(route["short_name"]) else None,
                    route["long_name"] if pd.notna(route["long_name"]) else None,
                    int(route["route_type"]),
                    route["color"] if pd.notna(route["color"]) else None,
                    route["text_color"] if pd.notna(route["text_color"]) else None,
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
    load_routes()