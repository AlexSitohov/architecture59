import os
import sys
import time
from datetime import datetime, timedelta
from functools import wraps

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException

sys.path.insert(0, (os.path.dirname(__file__)))

from src.config import DagConfig
from src.upload import UploadProvider
from src.logger import setup_logger

logger = setup_logger(__name__)

try:
    dag_folder = os.path.dirname(os.path.abspath(__file__))
    dag_name = os.path.basename(dag_folder)
    logger.info(f"Инициализация DAG: {dag_name} из папки: {dag_folder}")

    dag_config = DagConfig(dag_folder=dag_folder)
    global_config = dag_config.global_config

    logger.info(f"Конфигурация DAG успешно загружена: {dag_name}")
except Exception as e:
    logger.critical(f"Критическая ошибка при инициализации DAG: {str(e)}")
    raise


def task_decorator(func):
    @wraps(func)
    def wrapper(**context):
        task_id = context.get("task_instance").task_id
        run_id = context.get("run_id", "unknown")
        logger.info(f"Начало выполнения задачи: {task_id}, run_id: {run_id}")

        start_time = time.time()
        try:
            result = func(**context)
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Задача {task_id} успешно выполнена за {duration:.2f} секунд")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(
                f"Ошибка в задаче {task_id} после {duration:.2f} секунд выполнения: {str(e)}"
            )
            logger.exception("Подробная информация об ошибке:")
            raise AirflowException(f"Ошибка в задаче {task_id}: {str(e)}")

    return wrapper


@task_decorator
def prepare(**context):
    pass


@task_decorator
def upload(**context):
    logger.info("Начало процесса загрузки данных")

    uploader = UploadProvider(global_config)

    rows_processed = uploader.execute()

    logger.info(
        f"Загрузка данных успешно завершена: обработано {rows_processed} записей"
    )

    context["ti"].xcom_push(key="rows_processed", value=rows_processed)

    return rows_processed


@task_decorator
def actualize(**context):
    pass


with DAG(
    dag_name,
    schedule_interval="*/3 * * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(hours=2),
        "on_failure_callback": lambda context: logger.error(
            f"Задача {context['task_instance'].task_id} завершилась с ошибкой"
        ),
    },
    doc_md=__doc__,
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

logger.info(f"DAG {dag_name} успешно инициализирован и готов к выполнению")
