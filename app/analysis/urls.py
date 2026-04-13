from django.urls import path

from .views import AnalysisCreateView, AnalysisListView

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis_list"),
    path("create/", AnalysisCreateView.as_view(), name="analysis_create"),
]
