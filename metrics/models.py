from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models

from metrics.validators import validate_unix_timestamp

User = get_user_model()


class Tag(models.Model):
    """
    Простая модель для тэгов.
    При добвалениии бизнес логики вынести в отдельное приложение.
    """

    name = models.CharField(
        verbose_name="Имя",
        max_length=64,
        unique=True,
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self) -> str:
        return self.name


class Metric(models.Model):
    name = models.CharField(
        verbose_name="Имя",
        max_length=256,
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(
        verbose_name="Создано",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.DO_NOTHING, related_name="metrics"
    )

    class Meta:
        verbose_name = "Метрика"
        verbose_name_plural = "Метрики"
        unique_together = ("author", "name")

    def __str__(self) -> str:
        return f"{self.name}"

    def save(self, *args, **kwargs):
        """
        Подключены сигналы:
         - ./signals.py
        """
        super().save(*args, **kwargs)


class MetricRecord(models.Model):
    metric = models.ForeignKey(
        Metric,
        verbose_name="Метрика",
        on_delete=models.CASCADE,
    )
    value = models.DecimalField(
        max_digits=16,
        decimal_places=4,
    )
    timestamp = models.BigIntegerField(
        verbose_name="Временая метка",
        validators=[validate_unix_timestamp],
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="metric_records",
        through="TagsMetricRecord",
        blank=True,
    )
    metric_name = models.CharField(
        verbose_name="Имя метрики",
        max_length=256,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Запись метрики"
        verbose_name_plural = "Записи метрик"
        ordering = ["-timestamp"]
        unique_together = ("metric", "timestamp")

    def __str__(self) -> str:
        return f"{self.metric_name}: {self.value} @ {self.timestamp}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.metric_name = self.metric.name
        super().save(*args, **kwargs)


class TagsMetricRecord(models.Model):
    """
    Связь Tag и MetricRecord.
    """

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    record = models.ForeignKey(MetricRecord, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("record", "tag")
