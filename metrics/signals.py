from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from metrics.models import Metric
from metrics.tasks import update_metric_records_name


@receiver(pre_save, sender=Metric)
def cache_old_metric_name(sender, instance, **kwargs):
    """Времено кешируем старое значение поля name"""
    if instance.pk:
        instance._old_name = (
            sender.objects.filter(pk=instance.pk).values_list("name", flat=True).first()
        )


@receiver(post_save, sender=Metric)
def update_metric_name_metric_records(sender, instance, created, **kwargs):
    """Обновляет metric_name у связанных MetricRecord"""
    if created:
        return

    old_name = getattr(instance, "_old_name", None)
    if old_name and old_name != instance.name:
        update_metric_records_name.delay(
            metric_id=instance.pk,
            new_name=instance.name,
        )
