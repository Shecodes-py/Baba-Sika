from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import ProgressSummarySerializer


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
