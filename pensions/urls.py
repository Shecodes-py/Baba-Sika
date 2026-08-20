from django.urls import path

from .views import ContributionHistoryView, ProgressSummaryView

app_name = "pensions"

urlpatterns = [
    path("progress/", ProgressSummaryView.as_view(), name="progress"),
    path("contributions/", ContributionHistoryView.as_view(), name="contributions"),
]
