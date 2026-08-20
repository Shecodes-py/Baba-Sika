"""
URL configuration for babasika project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/account-provisioning/', include('account_provisioning.urls')),
    path('api/conversations/', include('conversations.urls')),
    path('api/pensions/', include('pensions.urls')),
    path('api/dashboard-bridge/', include('dashboard_bridge.urls')),
]
