from pathlib import Path
import zipfile

import requests


GTFS_URL = (
    "https://eu.ftp.opendatasoft.com/sncf/plandata/"
    "Export_OpenData_SNCF_GTFS_NewTripId.zip"
)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "raw"

ZIP_PATH = RAW_DIR / "sncf_gtfs.zip"
EXTRACT_DIR = RAW_DIR / "sncf_gtfs"


def download_gtfs():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Téléchargement du GTFS SNCF...")

    response = requests.get(
        GTFS_URL,
        timeout=120,
    )

    response.raise_for_status()

    with open(ZIP_PATH, "wb") as file:
        file.write(response.content)

    print(f"Fichier téléchargé : {ZIP_PATH}")


def extract_gtfs():
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    print("Extraction du GTFS...")

    with zipfile.ZipFile(ZIP_PATH, "r") as zip_file:
        zip_file.extractall(EXTRACT_DIR)

    print(f"Fichiers extraits : {EXTRACT_DIR}")


if __name__ == "__main__":
    download_gtfs()
    extract_gtfs()

    print("Ingestion terminée.")