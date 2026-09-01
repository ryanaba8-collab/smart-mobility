from datetime import datetime
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator


sys.path.append("/opt/airflow/data_pipeline")


def run_download_gtfs():
    from ingestion.download_gtfs import download_gtfs
    download_gtfs()


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
    from transformation.transform_calendar_dates import transform_calendar_dates
    transform_calendar_dates()


def run_load_calendar_dates():
    from loading.load_calendar_dates import load_calendar_dates
    load_calendar_dates()


with DAG(
    dag_id="smart_mobility_etl",
    start_date=datetime(2026, 8, 1),
    schedule="@daily",
    catchup=False,
    tags=["smart-mobility"],
) as dag:

    download = PythonOperator(
        task_id="download_gtfs",
        python_callable=run_download_gtfs,
    )

    extract = PythonOperator(
        task_id="extract_gtfs",
        python_callable=run_extract_gtfs,
    )

    transform_stations_task = PythonOperator(
        task_id="transform_stations",
        python_callable=run_transform_stations,
    )

    load_stations_task = PythonOperator(
        task_id="load_stations",
        python_callable=run_load_stations,
    )

    transform_stop_points_task = PythonOperator(
        task_id="transform_stop_points",
        python_callable=run_transform_stop_points,
    )

    load_stop_points_task = PythonOperator(
        task_id="load_stop_points",
        python_callable=run_load_stop_points,
    )

    transform_routes_task = PythonOperator(
        task_id="transform_routes",
        python_callable=run_transform_routes,
    )

    load_routes_task = PythonOperator(
        task_id="load_routes",
        python_callable=run_load_routes,
    )

    transform_trips_task = PythonOperator(
        task_id="transform_trips",
        python_callable=run_transform_trips,
    )

    load_trips_task = PythonOperator(
        task_id="load_trips",
        python_callable=run_load_trips,
    )

    transform_stop_times_task = PythonOperator(
        task_id="transform_stop_times",
        python_callable=run_transform_stop_times,
    )

    load_stop_times_task = PythonOperator(
        task_id="load_stop_times",
        python_callable=run_load_stop_times,
    )

    transform_calendar_dates_task = PythonOperator(
    task_id="transform_calendar_dates",
    python_callable=run_transform_calendar_dates,
    )

    load_calendar_dates_task = PythonOperator(
    task_id="load_calendar_dates",
    python_callable=run_load_calendar_dates,
   )

        

    (
        download
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
    )