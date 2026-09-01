from pathlib import Path
import pandas as pd



BASE_DIR = Path(__file__).resolve().parent.parent

STOP_TIMES_FILE = BASE_DIR / "raw" / "sncf_gtfs" / "stop_times.txt"
OUTPUT_FILE = BASE_DIR / "clean" / "stop_times.csv"


def time_to_seconds(value):
   
    if pd.isna(value):
        return None

    hours, minutes, seconds = map(int, str(value).split(":"))

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


def transform_stop_times():
    print("Lecture des stop_times RAW...")

    stop_times = pd.read_csv(STOP_TIMES_FILE)

    print(f"Stop times RAW : {len(stop_times)}")

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
        stop_times["stop_sequence"].astype(int)
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

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    stop_times.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"Stop times transformés : {len(stop_times)}"
    )
    print(
        f"Fichier créé : {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    transform_stop_times()