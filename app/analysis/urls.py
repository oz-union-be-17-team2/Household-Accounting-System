from django.urls import path

from .views import AnalysisListView

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis_list"),
]
