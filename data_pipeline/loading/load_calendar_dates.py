from pathlib import Path
import uuid
import os

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
CALENDAR_DATES_FILE = BASE_DIR / "clean" / "calendar_dates.csv"

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def load_calendar_dates():
    print("Lecture des calendar_dates CLEAN...")

    calendar_dates = pd.read_csv(
        CALENDAR_DATES_FILE,
        dtype={"service_id": str},
    )

    print(f"Calendar dates à charger : {len(calendar_dates)}")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        rows = []

        for row in calendar_dates.itertuples(index=False):
            rows.append(
                (
                    str(uuid.uuid4()),
                    row.service_id,
                    row.date,
                    int(row.exception_type),
                )
            )

        print(f"Lignes préparées : {len(rows)}")
        print("Insertion dans PostgreSQL...")

        query = """
            INSERT INTO gtfs_service_date (
                id,
                service_id,
                service_date,
                exception_type
            )
            VALUES %s

            ON CONFLICT (service_id, service_date)
            DO UPDATE SET
                exception_type = EXCLUDED.exception_type,
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
    load_calendar_dates()