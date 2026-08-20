from ingestion.download_gtfs import download_gtfs, extract_gtfs
from transformation.transform_stations import transform_stations
from loading.load_stations import load_stations


def run_pipeline():
    print("=" * 50)
    print("SMART MOBILITY — DATA PIPELINE")
    print("=" * 50)

    print("\n[1/3] EXTRACT")
    download_gtfs()
    extract_gtfs()

    print("\n[2/3] TRANSFORM")
    transform_stations()

    print("\n[3/3] LOAD")
    load_stations()

    print("\n" + "=" * 50)
    print("PIPELINE TERMINÉ AVEC SUCCÈS")
    print("=" * 50)


if __name__ == "__main__":
    run_pipeline()