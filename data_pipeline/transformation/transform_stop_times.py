from pathlib import Path
import gc

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

STOP_TIMES_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "stop_times.txt"
OUTPUT_FILE = BASE_DIR / "clean" / "stop_times.csv"

CHUNK_SIZE = 50_000


def time_to_seconds(value):
    if pd.isna(value):
        return None

    hours, minutes, seconds = map(int, str(value).split(":"))

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


def transform_chunk(stop_times):
    stop_times = stop_times[
        [
            "trip_id",
            "stop_id",
            "arrival_time",
            "departure_time",
            "stop_sequence",
            "pickup_type",
            "drop_off_type",
        ]
    ].copy()

    stop_times = stop_times.rename(
        columns={
            "trip_id": "trip_external_id",
            "stop_id": "stop_point_external_id",
        }
    )

    stop_times = stop_times.dropna(
        subset=[
            "trip_external_id",
            "stop_point_external_id",
            "stop_sequence",
        ]
    )

    stop_times["arrival_seconds"] = (
        stop_times["arrival_time"]
        .apply(time_to_seconds)
    )

    stop_times["departure_seconds"] = (
        stop_times["departure_time"]
        .apply(time_to_seconds)
    )

    stop_times = stop_times.drop(
        columns=[
            "arrival_time",
            "departure_time",
        ]
    )

    stop_times["stop_sequence"] = (
        stop_times["stop_sequence"]
        .astype(int)
    )

    stop_times["pickup_type"] = (
        stop_times["pickup_type"]
        .fillna(0)
        .astype(int)
    )

    stop_times["drop_off_type"] = (
        stop_times["drop_off_type"]
        .fillna(0)
        .astype(int)
    )

    return stop_times


def transform_stop_times():
    print("Lecture des stop_times RAW par chunks...")

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    total_raw = 0
    total_transformed = 0
    first_chunk = True

    reader = pd.read_csv(
        STOP_TIMES_FILE,
        chunksize=CHUNK_SIZE,
    )

    for chunk_number, chunk in enumerate(reader, start=1):
        raw_count = len(chunk)
        total_raw += raw_count

        print(
            f"Chunk {chunk_number} : "
            f"{raw_count} lignes RAW"
        )

        transformed = transform_chunk(chunk)

        transformed_count = len(transformed)
        total_transformed += transformed_count

        transformed.to_csv(
            OUTPUT_FILE,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False,
        )

        first_chunk = False

        print(
            f"Chunk {chunk_number} : "
            f"{transformed_count} lignes transformées"
        )

        del transformed
        del chunk
        gc.collect()

    print(f"Stop times RAW : {total_raw}")
    print(f"Stop times transformés : {total_transformed}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    transform_stop_times()