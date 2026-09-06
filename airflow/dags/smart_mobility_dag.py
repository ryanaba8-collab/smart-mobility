from datetime import datetime, timedelta
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


# ============================================================
# ACCÈS AU DATA PIPELINE DEPUIS AIRFLOW
# ============================================================

sys.path.append("/opt/airflow/data_pipeline")


# ============================================================
# FONCTIONS EXÉCUTÉES PAR AIRFLOW
# ============================================================

def run_download_gtfs():
    from ingestion.download_gtfs import download_gtfs

    download_gtfs()


def run_upload_gtfs_to_datalake():
    from ingestion.upload_to_datalake import upload_gtfs_to_datalake

    upload_gtfs_to_datalake()


def run_extract_gtfs():
    from ingestion.download_gtfs import extract_gtfs

    extract_gtfs()


def run_transform_stations():
    from transformation.transform_stations import transform_stations

    transform_stations()


def run_load_stations():
    from loading.load_stations import load_stations

    load_stations()


def run_transform_stop_points():
    from transformation.transform_stop_points import transform_stop_points

    transform_stop_points()


def run_load_stop_points():
    from loading.load_stop_points import load_stop_points

    load_stop_points()


def run_transform_routes():
    from transformation.transform_routes import transform_routes

    transform_routes()


def run_load_routes():
    from loading.load_routes import load_routes

    load_routes()


def run_transform_trips():
    from transformation.transform_trips import transform_trips

    transform_trips()


def run_load_trips():
    from loading.load_trips import load_trips

    load_trips()


def run_transform_stop_times():
    from transformation.transform_stop_times import transform_stop_times

    transform_stop_times()


def run_load_stop_times():
    from loading.load_stop_times import load_stop_times

    load_stop_times()


def run_transform_calendar_dates():
    from transformation.transform_calendar_dates import (
        transform_calendar_dates,
    )

    transform_calendar_dates()


def run_load_calendar_dates():
    from loading.load_calendar_dates import load_calendar_dates

    load_calendar_dates()

def run_export_parquet():
    from transformation.export_parquet import export_clean_to_parquet

    export_clean_to_parquet()


def run_upload_processed_to_datalake():
    from ingestion.upload_processed_to_datalake import (
        upload_processed_to_datalake,
    )

    upload_processed_to_datalake()
default_args = {
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}
def run_check_data_quality():
    from quality.check_data_quality import check_data_quality

    check_data_quality()

def run_collect_pipeline_metrics():
    from monitoring.pipeline_metrics import collect_pipeline_metrics

    collect_pipeline_metrics()
# ============================================================
# DAG SMART MOBILITY
# ============================================================

with DAG(
    dag_id="smart_mobility_etl",
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    tags=["smart-mobility"],
    max_active_runs=1,
    max_active_tasks=2,
    default_args=default_args,
) as dag:

    # --------------------------------------------------------
    # INGESTION
    # --------------------------------------------------------

    download = PythonOperator(
        task_id="download_gtfs",
        python_callable=run_download_gtfs,
    )

    upload_raw_to_azure = PythonOperator(
        task_id="upload_raw_to_azure",
        python_callable=run_upload_gtfs_to_datalake,
    )

    extract = PythonOperator(
        task_id="extract_gtfs",
        python_callable=run_extract_gtfs,
    )

    # --------------------------------------------------------
    # STATIONS
    # --------------------------------------------------------

    transform_stations_task = PythonOperator(
        task_id="transform_stations",
        python_callable=run_transform_stations,
    )

    load_stations_task = PythonOperator(
        task_id="load_stations",
        python_callable=run_load_stations,
    )

    # --------------------------------------------------------
    # STOP POINTS
    # --------------------------------------------------------

    transform_stop_points_task = PythonOperator(
        task_id="transform_stop_points",
        python_callable=run_transform_stop_points,
    )

    load_stop_points_task = PythonOperator(
        task_id="load_stop_points",
        python_callable=run_load_stop_points,
    )

    # --------------------------------------------------------
    # ROUTES
    # --------------------------------------------------------

    transform_routes_task = PythonOperator(
        task_id="transform_routes",
        python_callable=run_transform_routes,
    )

    load_routes_task = PythonOperator(
        task_id="load_routes",
        python_callable=run_load_routes,
    )

    # --------------------------------------------------------
    # TRIPS
    # --------------------------------------------------------

    transform_trips_task = PythonOperator(
        task_id="transform_trips",
        python_callable=run_transform_trips,
    )

    load_trips_task = PythonOperator(
        task_id="load_trips",
        python_callable=run_load_trips,
    )

    # --------------------------------------------------------
    # STOP TIMES
    # --------------------------------------------------------

    transform_stop_times_task = PythonOperator(
        task_id="transform_stop_times",
        python_callable=run_transform_stop_times,
    )

    load_stop_times_task = PythonOperator(
        task_id="load_stop_times",
        python_callable=run_load_stop_times,
    )

    # --------------------------------------------------------
    # CALENDAR DATES
    # --------------------------------------------------------

    transform_calendar_dates_task = PythonOperator(
        task_id="transform_calendar_dates",
        python_callable=run_transform_calendar_dates,
    )

    load_calendar_dates_task = PythonOperator(
        task_id="load_calendar_dates",
        python_callable=run_load_calendar_dates,
    )
    check_data_quality_task = PythonOperator(
        task_id="check_data_quality",
        python_callable=run_check_data_quality,
    )
    export_parquet_task = PythonOperator(
            task_id="export_parquet",
            python_callable=run_export_parquet,
    )

    upload_processed_to_azure_task = PythonOperator(
        task_id="upload_processed_to_azure",
        python_callable=run_upload_processed_to_datalake,
    )
    
    collect_pipeline_metrics_task = PythonOperator(
    task_id="collect_pipeline_metrics",
    python_callable=run_collect_pipeline_metrics,
    )
    # ========================================================
    # ORDRE D'EXÉCUTION DU PIPELINE
    # ========================================================

    (
        download
        >> upload_raw_to_azure
        >> extract
        >> transform_stations_task
        >> load_stations_task
        >> transform_stop_points_task
        >> load_stop_points_task
        >> transform_routes_task
        >> load_routes_task
        >> transform_trips_task
        >> load_trips_task
        >> transform_stop_times_task
        >> load_stop_times_task
        >> transform_calendar_dates_task
        >> load_calendar_dates_task
        >>check_data_quality_task
        >>collect_pipeline_metrics_task
        >> export_parquet_task
        >> upload_processed_to_azure_task
    )