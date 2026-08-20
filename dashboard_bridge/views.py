from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import VerifyMagicLinkRequestSerializer, VerifyMagicLinkResponseSerializer


class VerifyMagicLinkView(APIView):
    """
    POST /api/dashboard-bridge/verify/ - called by the dashboard, not by
    WhatsApp. Body: {"token": "<jwt from the magic link>"}. Returns a normal
    session access token the dashboard then sends as a Bearer token on
    every subsequent API call.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        request_serializer = VerifyMagicLinkRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            access_token = services.verify_and_exchange(request_serializer.validated_data["token"])
        except services.MagicLinkExpiredError:
            return Response({"detail": "This link has expired."}, status=410)
        except services.MagicLinkAlreadyUsedError:
            return Response({"detail": "This link has already been used."}, status=409)
        except services.MagicLinkInvalidError:
            return Response({"detail": "This link is invalid."}, status=400)

        response_serializer = VerifyMagicLinkResponseSerializer({"access": access_token})
        return Response(response_serializer.data)
