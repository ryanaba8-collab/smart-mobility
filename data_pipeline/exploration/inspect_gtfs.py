from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
GTFS_DIR = BASE_DIR / "raw" / "sncf_gtfs"


stops = pd.read_csv(GTFS_DIR / "stops.txt")

print("=== STOPS ===")
print()

print("Dimensions :")
print(stops.shape)

print("\nColonnes :")
print(stops.columns.tolist())

print("\nPremières lignes :")
print(stops.head())

print("\nTypes :")
print(stops.dtypes)

print("\nValeurs manquantes :")
print(stops.isnull().sum())

stations = stops[stops["location_type"] == 1]

print("\n=== STATIONS UNIQUEMENT ===")

print("\nNombre de stations :")
print(len(stations))

print("\nPremières stations :")
print(
    stations[
        ["stop_id", "stop_name", "stop_lat", "stop_lon"]
    ].head(10)
)
print("\nDoublons sur stop_id :")
print(stations["stop_id"].duplicated().sum())

print("\nDoublons sur stop_name :")
print(stations["stop_name"].duplicated().sum())