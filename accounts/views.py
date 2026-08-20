from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer


class MeView(RetrieveAPIView):
    """
    GET /api/accounts/me/ - used by the dashboard after it has exchanged the
    WhatsApp magic link for a session access token (see dashboard_bridge).
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
