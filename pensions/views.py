from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Contribution
from .serializers import ContributionSerializer, ProgressSummarySerializer


class ProgressSummaryView(APIView):
    """
    GET /api/pensions/progress/ - read-only, no AI. Same data the WhatsApp
    "balance/progress" flow surfaces, exposed for the dashboard.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        summary = services.get_progress_summary(request.user)
        serializer = ProgressSummarySerializer(summary)
        return Response(serializer.data)


class ContributionHistoryView(ListAPIView):
    """
    GET /api/pensions/contributions/ - the dashboard's "recent activity" feed.
    Every executed contribution, both buckets, newest first. Read-only.
    """

    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Contribution.objects.filter(plan__user=self.request.user).order_by("-created_at")[:50]
