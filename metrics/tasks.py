from celery import shared_task

from metrics.models import MetricRecord

@shared_task
def update_metric_records_name(metric_id, new_name):
    MetricRecord.objects.filter(metric_id=metric_id).update(metric_name=new_name)