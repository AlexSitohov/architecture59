import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import logging

sys.path.insert(0, (os.path.dirname(__file__)))

from src.source_to_target import DagConfig
from src.prepare import PrepareProvider
from src.upload import UploadProvider

dag_folder = os.path.dirname(os.path.abspath(__file__))

dag_name = os.path.basename(dag_folder)

dag_config = DagConfig(dag_folder=dag_folder)
global_config = dag_config.global_config

logger = logging.getLogger(__name__)


def prepare(**context):
    PrepareProvider(global_config).execute()


def upload(**context):
    UploadProvider(global_config).execute()


def actualize(**context): ...


with DAG(
    dag_name,
    schedule_interval="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(hours=2),
    },
) as dag:

    prepare_task = PythonOperator(
        task_id="prepare",
        python_callable=prepare,
        provide_context=True,
    )
    upload_task = PythonOperator(
        task_id="upload",
        python_callable=upload,
        provide_context=True,
    )

    actualization_task = PythonOperator(
        task_id="actualize",
        python_callable=actualize,
        provide_context=True,
    )

    prepare_task >> upload_task >> actualization_task
