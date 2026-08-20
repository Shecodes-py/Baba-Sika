from django.urls import path

from .views import MyBankAccountView

app_name = "account_provisioning"

urlpatterns = [
    path("account/", MyBankAccountView.as_view(), name="my-account"),
]
