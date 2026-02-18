import logging
from pathlib import Path

from celery import shared_task
from django.utils import timezone

from metrics.models import Metric, MetricRecord

logger = logging.getLogger(__name__)

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_FILE = REPORT_DIR / "metrics_report.txt"


def sync_metric_records_name(metric_id: int, new_name: str) -> int:
    """Обновляет поле metric_name у записей метрики."""
    return MetricRecord.objects.filter(metric_id=metric_id).update(metric_name=new_name)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def update_metric_records_name(metric_id: int, new_name: str):
    """Обновляет metric_name у связанных MetricRecord с ретраями."""
    sync_metric_records_name(metric_id=metric_id, new_name=new_name)
    logger.info("Поле metric_name обновлено")


@shared_task
def generate_report():
    """Генерация отчета по метрикам и записям"""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    metrics_count = Metric.objects.count()
    records_count = MetricRecord.objects.count()
    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    content = (
        f"[{timestamp}] Отчёт по метрикам:\n"
        f"Всего метрик: {metrics_count}\n"
        f"Всего записей: {records_count}\n"
    )

    REPORT_FILE.write_text(content, encoding="utf-8")
