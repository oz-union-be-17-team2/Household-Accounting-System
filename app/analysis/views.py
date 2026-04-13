from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .analyzer import SpendingAnalyzer
from .models import Analysis
from .serializers import AnalysisCreateSerializer, AnalysisSerializer


class AnalysisListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisSerializer

    def get_queryset(self):
        analysis = Analysis.objects.filter(user=self.request.user).select_related("user")

        analysis_type = self.request.query_params.get("analysis_type")
        if analysis_type:
            analysis = analysis.filter(analysis_type=analysis_type)

        return analysis


class AnalysisCreateView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AnalysisCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        period_start = serializer.validated_data["period_start"]
        period_end = serializer.validated_data["period_end"]
        analysis_type = serializer.validated_data["analysis_type"]

        try:
            analyzer = SpendingAnalyzer(
                user=request.user,
                period_start=period_start,
                period_end=period_end,
                analysis_type=analysis_type,
            )
            analyzer.run()
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        analysis = Analysis.objects.filter(
            user=request.user,
            period_start=period_start,
            period_end=period_end,
            analysis_type=analysis_type,
        ).last()

        return Response(AnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)
