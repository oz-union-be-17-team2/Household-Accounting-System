from django.conf import settings
from django.db import models

from core.models import TimeStampModel


class Analysis(TimeStampModel):
    class AnalysisType(models.TextChoices):
        WEEKLY = "WEEKLY", "주간"
        MONTHLY = "MONTHLY", "월간"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    about = models.CharField(max_length=50)
    analysis_type = models.CharField(max_length=10, choices=AnalysisType.choices)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField(blank=True)
    result_image = models.ImageField(upload_to="analysis/", blank=True, null=True)

    class Meta:
        verbose_name = "소비 분석"
        verbose_name_plural = f"{verbose_name} 목록"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} | {self.analysis_type} | {self.period_start} ~ {self.period_end}"
