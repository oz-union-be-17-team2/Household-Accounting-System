from datetime import date, timedelta

from celery import shared_task
from django.contrib.auth import get_user_model

from .analyzer import SpendingAnalyzer
from .models import Analysis

User = get_user_model()


@shared_task
def analyze_weekly_task():
    users = User.objects.filter(is_active=True, is_delete=False)

    today = date.today()
    period_end = today - timedelta(days=1)
    period_start = today - timedelta(days=7)

    for user in users:
        try:
            if Analysis.objects.filter(
                user=user,
                analysis_type=Analysis.AnalysisType.WEEKLY,
                period_start=period_start,
                period_end=period_end,
            ).exists():
                continue

            analyzer = SpendingAnalyzer(
                user=user,
                period_start=period_start,
                period_end=period_end,
                analysis_type=Analysis.AnalysisType.WEEKLY,
            )
            analyzer.run()
        except ValueError:
            continue


@shared_task
def analyze_monthly_task():
    users = User.objects.filter(is_active=True, is_delete=False)

    today = date.today()
    period_end = date(today.year, today.month, 1) - timedelta(days=1)
    period_start = date(period_end.year, period_end.month, 1)

    for user in users:
        try:
            if Analysis.objects.filter(
                user=user,
                analysis_type=Analysis.AnalysisType.MONTHLY,
                period_start=period_start,
                period_end=period_end,
            ).exists():
                continue

            analyzer = SpendingAnalyzer(
                user=user,
                period_start=period_start,
                period_end=period_end,
                analysis_type=Analysis.AnalysisType.WEEKLY,
            )
            analyzer.run()
        except ValueError:
            continue
