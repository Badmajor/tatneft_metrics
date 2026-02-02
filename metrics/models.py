from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=64, unique=True,)
        

class Metric(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=256,)
    description = models.TextField(verbose_name='Описание', blank=True, null=True,)
    create_at = models.DateTimeField(verbose_name='Создано', auto_now_add=True,)
    author = models.ForeignKey(User, verbode_name='Автор', on_delete=models.DO_NOTHING, related_name='metrics')

class MetricRecord(models.Model):
    mertic = models.ForeignKey(Metric, verbose_name='Метрика', on_delete=models.CASCADE,)
    value = models.DecimalField(max_digits=16, decimal_places=4,)
    timestamp = models.IntegerField(verbose_name='Временая метка', )
    tags = models.ManyToManyField(Tag, related_name='metric_records', through='TagsMetricRecord')


class TagsMetricRecord(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    record = models.ForeignKey(MetricRecord, on_delete=models.CASCADE)