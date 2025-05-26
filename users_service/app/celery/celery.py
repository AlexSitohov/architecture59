from celery import Celery
import os


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND")

celery.autodiscover_tasks(["app.celery"], related_name="send_email", force=True)
