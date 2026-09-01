from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

CALENDAR_DATES_FILE = (
    BASE_DIR / "raw" / "sncf_gtfs" / "calendar_dates.txt"
)

OUTPUT_FILE = (
    BASE_DIR / "clean" / "calendar_dates.csv"
)


def transform_calendar_dates():
    print("Lecture des calendar_dates RAW...")

    calendar_dates = pd.read_csv(
        CALENDAR_DATES_FILE,
        dtype={"service_id": str},
    )

    print(
        f"Calendar dates RAW : {len(calendar_dates)}"
    )

    calendar_dates = calendar_dates[
        [
            "service_id",
            "date",
            "exception_type",
        ]
    ].copy()

    calendar_dates = calendar_dates.dropna(
        subset=[
            "service_id",
            "date",
            "exception_type",
        ]
    )

    # Conversion YYYYMMDD -> vraie date
    calendar_dates["date"] = pd.to_datetime(
        calendar_dates["date"].astype(str),
        format="%Y%m%d",
    ).dt.date

    calendar_dates["exception_type"] = (
        calendar_dates["exception_type"].astype(int)
    )

    calendar_dates = calendar_dates.drop_duplicates(
        subset=[
            "service_id",
            "date",
        ]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    calendar_dates.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"Calendar dates transformées : "
        f"{len(calendar_dates)}"
    )

    print(
        f"Fichier créé : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    transform_calendar_dates()