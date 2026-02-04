from django.contrib import admin

from metrics.models import Metric, MetricRecord, Tag, TagsMetricRecord


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
