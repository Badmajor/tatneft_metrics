import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tatneft_metrics.settings")
app = Celery("tatneft_metrics")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
