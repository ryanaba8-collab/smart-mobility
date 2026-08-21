import logging
import time

from ingestion.download_gtfs import download_gtfs, extract_gtfs
from transformation.transform_stations import transform_stations
from loading.load_stations import load_stations


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_step(step_name, function):
    logger.info("Début : %s", step_name)

    start_time = time.time()

    try:
        function()

        duration = time.time() - start_time

        logger.info(
            "Succès : %s (%.2f secondes)",
            step_name,
            duration,
        )

    except Exception:
        duration = time.time() - start_time

        logger.exception(
            "Échec : %s après %.2f secondes",
            step_name,
            duration,
        )

        raise


def run_pipeline():
    logger.info("Démarrage du pipeline Smart Mobility")

    pipeline_start = time.time()

    try:
        run_step("Téléchargement GTFS", download_gtfs)
        run_step("Extraction GTFS", extract_gtfs)
        run_step("Transformation stations", transform_stations)
        run_step("Chargement PostgreSQL", load_stations)

    except Exception:
        logger.error("Pipeline interrompu")
        raise

    duration = time.time() - pipeline_start

    logger.info(
        "Pipeline terminé avec succès en %.2f secondes",
        duration,
    )


if __name__ == "__main__":
    run_pipeline()