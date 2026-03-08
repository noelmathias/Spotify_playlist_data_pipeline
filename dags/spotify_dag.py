from airflow import DAG                           #Libraries for DAG , operators and datetime for scheduling
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


#Task retries and failure handling are defined in default_args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1)
}


# Defining the DAG 
with DAG(
    dag_id="spotify_playlist_pipeline",
    start_date=datetime(2026, 3, 1),
    schedule=None,
    catchup=False,
    tags=["spotify"],
) as dag:


# Task definitions
    fetch_data = BashOperator(
        task_id="Fetch_Data",
        bash_command="python /opt/airflow/scripts/main.py fetch"
    )

    validate_data = BashOperator(
        task_id="Validate_Data",
        bash_command="python /opt/airflow/scripts/main.py validate"
    )

    transform_data = BashOperator(
        task_id="Transform_Data",
        bash_command="python /opt/airflow/scripts/main.py transform"
    )


    generate_report = BashOperator(
        task_id="Generate_Report",
        bash_command="python /opt/airflow/scripts/main.py report"
    )

    notify_completion = BashOperator(
        task_id="Notify_Completion",
        bash_command="python /opt/airflow/scripts/main.py notify"
    )

# Task dependencies
    fetch_data >> validate_data >> transform_data >> generate_report >> notify_completion