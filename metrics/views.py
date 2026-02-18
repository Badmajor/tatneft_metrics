import logging

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.models import Metric, MetricRecord, Tag
from metrics.serializers import MetricRecordSerializer, MetricSerializer, TagSerializer

logger = logging.getLogger("metrics.views")


class MetricListCreateAPIView(APIView):
    def get(self, request):
        metrics = Metric.objects.filter(author=request.user)
        serializer = MetricSerializer(metrics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MetricSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        metric = serializer.save(author=request.user)

        return Response(
            MetricSerializer(metric).data,
            status=status.HTTP_201_CREATED,
        )


class TagListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by("name")


class MetricRecordQSMixin:
    serializer_class = MetricRecordSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Возвращает qs записей метрики с фильлтрацией по metric_id и author."""
        return MetricRecord.objects.filter(
            metric_id=self.kwargs["metric_id"],
            metric__author=self.request.user,
        ).order_by("-timestamp")

    @staticmethod
    def metric_records_cache_key(metric_id: int, user_id: int) -> str:
        return f"metric:{metric_id}:{user_id}:records"


class MetricRecordListCreateAPIView(MetricRecordQSMixin, generics.GenericAPIView):
    def get(self, request, metric_id: int):
        user_id = request.user.id
        cache_key = self.metric_records_cache_key(metric_id, user_id)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug(f"Отдаю записи метрики ID {metric_id} из кеша.")
            return Response(cached_data)

        records = self.get_queryset()
        serializer = self.get_serializer(records, many=True)

        cache.set(cache_key, serializer.data, timeout=60 * 5)

        return Response(serializer.data)

    def post(self, request, metric_id: int):
        user_id = request.user.id
        metric = get_object_or_404(
            Metric,
            id=metric_id,
            author=request.user,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = serializer.save(
            metric=metric,
            metric_name=metric.name,
        )
        logger.debug(f"Сбрасываю кеш записей метрики ID {metric_id}.")
        cache.delete(self.metric_records_cache_key(metric_id, user_id))

        return Response(
            self.get_serializer(record).data,
            status=status.HTTP_201_CREATED,
        )


class MetricRecordDetailAPIView(MetricRecordQSMixin, generics.RetrieveAPIView):
    lookup_url_kwarg = "record_id"
