from django.urls import path

from .views import VerifyMagicLinkView

app_name = "dashboard_bridge"

urlpatterns = [
    path("verify/", VerifyMagicLinkView.as_view(), name="verify"),
]
