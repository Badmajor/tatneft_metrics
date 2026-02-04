from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from metrics.models import Metric, MetricRecord
from metrics.views import MetricRecordQSMixin

User = get_user_model()


class MetricRecordCreateAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            password="password123",
        )

        self.metric = Metric.objects.create(
            name="Test Metric",
            author=self.user,
        )

        self.url = reverse(
            "metric-record-list-create",
            kwargs={"metric_id": self.metric.id},
        )

        self.payload = {
            "value": "123.45",
            "timestamp": 1700000000,
        }

    def test_create_metric_record_success(self):
        """Упсешное создание метрики"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MetricRecord.objects.count(), 1)

        record = MetricRecord.objects.first()
        self.assertEqual(record.metric, self.metric, "Не верно указана метрика")
        self.assertEqual(
            record.metric_name, self.metric.name, "Не верно указано название метрики"
        )
        self.assertEqual(
            float(record.value),
            float(self.payload.get("value")),
            "Значение метрики не верное",
        )
        self.assertEqual(
            record.timestamp, self.payload.get("timestamp"), "Временая метка не верна"
        )

    def test_create_metric_record_unauthorized(self):
        """Не авторизованным пользователям отказано в доступе"""
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Статус код должен быть 401",
        )
        self.assertEqual(
            MetricRecord.objects.count(), 0, "Запись метрики не должна создаваться"
        )

    def test_create_metric_record_for_other_user_metric(self):
        """Можно добавлят записи только для своих метрик"""
        self.metric.author = self.other_user
        self.metric.save()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Пользователь не должен получать доступ к чужим метрикам",
        )
        self.assertEqual(
            MetricRecord.objects.count(),
            0,
            "Не должны создаваться записи для чужих метрик",
        )

    def test_cache_invalidated_on_create(self):
        self.client.force_authenticate(user=self.user)

        cache_key = MetricRecordQSMixin.metric_records_cache_key(self.metric.id)
        cache.set(cache_key, [{"fake": "data"}], timeout=300)

        self.assertIsNotNone(cache.get(cache_key), "Кеш не созраняется")

        self.client.post(self.url, self.payload, format="json")

        self.assertIsNone(cache.get(cache_key), "Инвалидация кеша не сработала")
