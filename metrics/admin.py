from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse

from metrics.models import Metric, MetricRecord, Tag, TagsMetricRecord

REPORT_FILE = Path(settings.BASE_DIR) / "reports" / "metrics_report.txt"


class MetricRecordInline(admin.TabularInline):
    """
    Встраиваем записи метрик прямо в карточку метрики
    """

    model = MetricRecord
    extra = 0
    fields = (
        "value",
        "timestamp",
        "metric_name",
    )
    readonly_fields = ("metric_name",)
    ordering = ("-timestamp",)


class TagsMetricRecordInline(admin.TabularInline):
    model = TagsMetricRecord
    extra = 0


@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    change_list_template = "admin/metrics/change_list.html"
    list_display = (
        "id",
        "name",
        "author",
        "created_at",
    )
    list_filter = (
        "author",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "author__username",
        "author__email",
    )
    ordering = ("-created_at",)

    inlines = [MetricRecordInline]

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "description", "author"),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download-report/",
                self.admin_site.admin_view(self.download_report_view),
                name="metrics_metric_download_report",
            )
        ]
        return custom_urls + urls

    def download_report_view(self, request: HttpRequest) -> HttpResponse:
        if not REPORT_FILE.exists():
            self.message_user(
                request,
                "Отчет еще не сгенерирован или недоступен.",
                level=messages.ERROR,
            )
            return redirect(reverse("admin:metrics_metric_changelist"))

        return FileResponse(
            REPORT_FILE.open("rb"),
            as_attachment=True,
            filename=REPORT_FILE.name,
        )


@admin.register(MetricRecord)
class MetricRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "metric_name",
        "metric",
        "value",
        "timestamp",
    )
    inlines = [TagsMetricRecordInline]
    list_filter = (
        "metric",
        "timestamp",
    )
    search_fields = ("metric_name",)
    ordering = ("-timestamp",)
    readonly_fields = ("metric_name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "metric",
                    "metric_name",
                    "value",
                    "timestamp",
                )
            },
        ),
    )

    autocomplete_fields = ("metric",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)
    ordering = ("name",)
