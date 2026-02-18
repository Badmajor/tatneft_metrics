from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from metrics.models import Metric, MetricRecord, Tag
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

        cache_key = MetricRecordQSMixin.metric_records_cache_key(
            self.metric.id, self.user.id
        )
        cache.set(cache_key, [{"fake": "data"}], timeout=300)

        self.assertIsNotNone(cache.get(cache_key), "Кеш не созраняется")

        self.client.post(self.url, self.payload, format="json")

        self.assertIsNone(cache.get(cache_key), "Инвалидация кеша не сработала")

    def test_create_metric_record_with_tags_success(self):
        """Создание записи метрики с тегами"""
        self.client.force_authenticate(user=self.user)

        tag_1 = Tag.objects.create(name="critical")
        tag_2 = Tag.objects.create(name="daily")
        payload = {
            **self.payload,
            "tags": [tag_1.id, tag_2.id],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MetricRecord.objects.count(), 1)

        record = MetricRecord.objects.get()
        self.assertSetEqual(
            set(record.tags.values_list("id", flat=True)),
            {tag_1.id, tag_2.id},
            "Теги не сохранились в записи метрики",
        )
        self.assertSetEqual(
            set(response.data["tags"]),
            {tag_1.id, tag_2.id},
            "В ответе API возвращаются некорректные теги",
        )

    def test_create_metric_record_with_invalid_tag_returns_400(self):
        """Нельзя создать запись с несуществующим тегом"""
        self.client.force_authenticate(user=self.user)

        payload = {
            **self.payload,
            "tags": [999999],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(MetricRecord.objects.count(), 0)
        self.assertIn("tags", response.data)


class MetricNameSyncSignalsTestCase(TestCase):
    def test_sync_fallback_used_if_celery_enqueue_failed(self):
        user = User.objects.create_user(username="sync-user", password="password123")
        metric = Metric.objects.create(name="Old Name", author=user)
        record = MetricRecord.objects.create(
            metric=metric,
            value="10.0000",
            timestamp=1700000000,
        )

        with patch(
            "metrics.signals.update_metric_records_name.delay",
            side_effect=RuntimeError("broker down"),
        ):
            with self.captureOnCommitCallbacks(execute=True) as callbacks :
                metric.name = "New Name"
                metric.save()

        record.refresh_from_db()
        assert len(callbacks) == 1
        self.assertEqual(
            record.metric_name,
            "New Name",
            "Fallback обновление metric_name не сработало при сбое Celery",
        )
