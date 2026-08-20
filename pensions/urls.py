from django.urls import path

from .views import ProgressSummaryView

app_name = "pensions"

urlpatterns = [
    path("progress/", ProgressSummaryView.as_view(), name="progress"),
]
