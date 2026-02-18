import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tatneft_metrics.settings")
app = Celery("tatneft_metrics")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "generate-report": {
        "task": "metrics.tasks.generate_report",
        "schedule": 2 * 60,
    },
}
