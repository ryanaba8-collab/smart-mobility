from pathlib import Path
import requests

DATASET_URL = (
    "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/"
    "regularite-mensuelle-tgv-aqst/exports/csv"
)

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "regularite_tgv.csv"


def download_dataset():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Téléchargement des données de régularité TGV...")

    response = requests.get(DATASET_URL, timeout=120)
    response.raise_for_status()

    OUTPUT_FILE.write_bytes(response.content)

    print(f"Fichier téléchargé : {OUTPUT_FILE}")
    print(f"Taille : {OUTPUT_FILE.stat().st_size / 1024 / 1024:.2f} Mo")


if __name__ == "__main__":
    download_dataset()