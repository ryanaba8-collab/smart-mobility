import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


STORAGE_ACCOUNT_NAME = "stsmartmobilityryan"
FILE_SYSTEM_NAME = "processed"

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "processed"


def get_credential():

    storage_account_key = os.getenv(
        "AZURE_STORAGE_ACCOUNT_KEY"
    )

    if storage_account_key:
        print("Authentification Azure : Storage Account Key")
        return storage_account_key

    print("Authentification Azure : DefaultAzureCredential")
    return DefaultAzureCredential()


def upload_processed_to_datalake():

    credential = get_credential()

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

    parquet_files = list(
        PROCESSED_DIR.glob("*.parquet")
    )

    if not parquet_files:
        raise FileNotFoundError(
            f"Aucun fichier Parquet trouvé dans {PROCESSED_DIR}"
        )

    print(
        f"{len(parquet_files)} fichiers Parquet à envoyer."
    )

    for local_file in parquet_files:

        remote_path = f"sncf/{local_file.name}"

        print(
            f"Upload : {local_file.name}"
            f" -> {remote_path}"
        )

        file_client = (
            file_system_client.get_file_client(
                remote_path
            )
        )

        with open(local_file, "rb") as data:

            file_client.upload_data(
                data,
                overwrite=True,
            )

    print(
        "Upload des données PROCESSED terminé avec succès."
    )


if __name__ == "__main__":
    upload_processed_to_datalake()