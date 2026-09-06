import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


# ============================================================
# CONFIGURATION
# ============================================================

STORAGE_ACCOUNT_NAME = "stsmartmobilityryan"
FILE_SYSTEM_NAME = "raw"

LOCAL_FILE = (
    Path(__file__).resolve().parents[1]
    / "raw"
    / "sncf_gtfs.zip"
)

REMOTE_PATH = "sncf/sncf_gtfs.zip"


# ============================================================
# UPLOAD VERS AZURE DATA LAKE
# ============================================================

def upload_gtfs_to_datalake():

    print(f"Fichier local : {LOCAL_FILE}")

    if not LOCAL_FILE.exists():
        raise FileNotFoundError(
            f"Fichier GTFS introuvable : {LOCAL_FILE}"
        )

    # --------------------------------------------------------
    # AUTHENTIFICATION
    # --------------------------------------------------------

    storage_account_key = os.getenv(
        "AZURE_STORAGE_ACCOUNT_KEY"
    )

    if storage_account_key:
        credential = storage_account_key
        print(
            "Authentification Azure : "
            "Storage Account Key"
        )
    else:
        credential = DefaultAzureCredential()
        print(
            "Authentification Azure : "
            "DefaultAzureCredential"
        )

    # --------------------------------------------------------
    # CONNEXION AU DATA LAKE
    # --------------------------------------------------------

    account_url = (
        f"https://{STORAGE_ACCOUNT_NAME}"
        ".dfs.core.windows.net"
    )

    service_client = DataLakeServiceClient(
        account_url=account_url,
        credential=credential,
    )

    file_system_client = (
        service_client.get_file_system_client(
            file_system=FILE_SYSTEM_NAME
        )
    )

    file_client = file_system_client.get_file_client(
        REMOTE_PATH
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    print(f"Upload de : {LOCAL_FILE}")
    print(f"Vers Azure : {REMOTE_PATH}")

    with open(LOCAL_FILE, "rb") as data:
        file_client.upload_data(
            data,
            overwrite=True,
        )

    print("Upload Azure terminé avec succès.")


# ============================================================
# EXÉCUTION MANUELLE
# ============================================================

if __name__ == "__main__":
    upload_gtfs_to_datalake()