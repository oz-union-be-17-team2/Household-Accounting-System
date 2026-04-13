from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analysis
        fields = [
            "id",
            "about",
            "analysis_type",
            "period_end",
            "period_start",
            "description",
            "result_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


class AnalysisCreateSerializer(serializers.Serializer):
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    analysis_type = serializers.ChoiceField(choices=Analysis.AnalysisType.choices)

    def validate(self, data):
        if data["period_start"] > data["period_end"]:
            raise serializers.ValidationError("시작일이 종료일보다 클 수 없습니다.")
        return data
