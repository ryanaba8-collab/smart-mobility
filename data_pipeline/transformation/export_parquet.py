from pathlib import Path
import gc

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


BASE_DIR = Path(__file__).resolve().parent.parent

CLEAN_DIR = BASE_DIR / "clean"
PROCESSED_DIR = BASE_DIR / "processed"

PROCESSED_DIR.mkdir(exist_ok=True)


FILES_TO_CONVERT = {
    "stations.csv": "stations.parquet",
    "stop_points.csv": "stop_points.parquet",
    "routes.csv": "routes.parquet",
    "trips.csv": "trips.parquet",
    "stop_times.csv": "stop_times.parquet",
    "calendar_dates.csv": "calendar_dates.parquet",
}


CHUNK_SIZE = 50_000


def csv_to_parquet(csv_path, parquet_path):

    print(f"Lecture par morceaux : {csv_path.name}")

    # Supprimer un éventuel fichier partiellement créé
    if parquet_path.exists():
        parquet_path.unlink()

    writer = None
    total_rows = 0

    try:
        for chunk_number, chunk in enumerate(
            pd.read_csv(
                csv_path,
                chunksize=CHUNK_SIZE,
            ),
            start=1,
        ):
            total_rows += len(chunk)

            print(
                f"Chunk {chunk_number} : "
                f"{len(chunk)} lignes"
            )

            table = pa.Table.from_pandas(
                chunk,
                preserve_index=False,
            )

            if writer is None:
                writer = pq.ParquetWriter(
                    parquet_path,
                    table.schema,
                    compression="snappy",
                )
            else:
                # Garantir le même schéma pour tous les chunks
                if table.schema != writer.schema:
                    table = table.cast(writer.schema)

            writer.write_table(table)

            # Libération explicite de la mémoire
            del table
            del chunk
            gc.collect()

    finally:
        if writer is not None:
            writer.close()

    print(
        f"Créé : {parquet_path} "
        f"({total_rows} lignes)"
    )


def export_clean_to_parquet():

    print("Début conversion CSV -> Parquet")

    for csv_name, parquet_name in FILES_TO_CONVERT.items():

        csv_path = CLEAN_DIR / csv_name
        parquet_path = PROCESSED_DIR / parquet_name

        if not csv_path.exists():
            print(
                f"Fichier absent, ignoré : {csv_path}"
            )
            continue

        csv_to_parquet(
            csv_path,
            parquet_path,
        )

        gc.collect()

    print("Conversion terminée.")


if __name__ == "__main__":
    export_clean_to_parquet()