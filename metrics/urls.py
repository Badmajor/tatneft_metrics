from django.urls import path

from metrics.views import (
    MetricListCreateAPIView,
    MetricRecordDetailAPIView,
    MetricRecordListCreateAPIView,
    TagListAPIView,
)

urlpatterns = [
    path(
        "metrics/",
        MetricListCreateAPIView.as_view(),
    ),
    path(
        "tags/",
        TagListAPIView.as_view(),
    ),
    path(
        "metrics/<int:metric_id>/records/<int:record_id>/",
        MetricRecordDetailAPIView.as_view(),
    ),
    path(
        "metrics/<int:metric_id>/records/",
        MetricRecordListCreateAPIView.as_view(),
        name="metric-record-list-create",
    ),
]
