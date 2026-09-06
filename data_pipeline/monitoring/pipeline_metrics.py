from pathlib import Path
from datetime import datetime
import json


BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "clean"
MONITORING_DIR = BASE_DIR / "monitoring"
METRICS_FILE = MONITORING_DIR / "latest_metrics.json"


FILES_TO_MONITOR = [
    "stations.csv",
    "stop_points.csv",
    "routes.csv",
    "trips.csv",
    "stop_times.csv",
    "calendar_dates.csv",
]


def count_rows(file_path: Path) -> int:
    if not file_path.exists():
        return 0

    with open(file_path, "r", encoding="utf-8") as file:
        return max(sum(1 for _ in file) - 1, 0)


def collect_pipeline_metrics():
    print("=== PIPELINE METRICS ===")

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "datasets": {},
        "total_rows": 0,
        "status": "HEALTHY",
    }

    for filename in FILES_TO_MONITOR:
        file_path = CLEAN_DIR / filename
        row_count = count_rows(file_path)

        metrics["datasets"][filename] = row_count
        metrics["total_rows"] += row_count

        print(f"{filename} : {row_count} lignes")

    if any(value == 0 for value in metrics["datasets"].values()):
        metrics["status"] = "WARNING"

    MONITORING_DIR.mkdir(parents=True, exist_ok=True)

    with open(METRICS_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4, ensure_ascii=False)

    print(f"\nTotal lignes : {metrics['total_rows']}")
    print(f"Status : {metrics['status']}")
    print(f"Métriques enregistrées dans : {METRICS_FILE}")

    return metrics


if __name__ == "__main__":
    collect_pipeline_metrics()