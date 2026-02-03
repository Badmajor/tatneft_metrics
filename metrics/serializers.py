from django.db import IntegrityError
from rest_framework import serializers

from metrics.models import Metric, MetricRecord, Tag


class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = (
            "id",
            "name",
            "description",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class MetricRecordSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = MetricRecord
        fields = (
            "id",
            "metric",
            "metric_name",
            "value",
            "timestamp",
            "tags",
        )
        read_only_fields = (
            "id",
            "metric",
            "metric_name",
        )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"timestamp": "Запись на этот момент времени уже существует"}
            )
