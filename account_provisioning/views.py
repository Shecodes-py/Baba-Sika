from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import BankAccountLink
from .serializers import BankAccountLinkSerializer


class MyBankAccountView(RetrieveAPIView):
    """GET /api/account-provisioning/account/ - cached balance for the dashboard/API consumers."""

    serializer_class = BankAccountLinkSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return BankAccountLink.objects.get(user=self.request.user)
