from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Analysis
from .serializers import AnalysisSerializer


class AnalysisListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        analysis = Analysis.objects.filter(user=self.request.user).select_related("user")

        analysis_type = self.request.query_params.get("analysis_type")
        if analysis_type:
            analysis = analysis.filter(analysis_type=analysis_type)

        return analysis
