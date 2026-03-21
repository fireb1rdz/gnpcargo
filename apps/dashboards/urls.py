from django.urls import path, include
from apps.dashboards.views import DashboardsView

app_name = 'dashboards'
urlpatterns = [
    path('dashboards/', DashboardsView.as_view(), name='dashboards'),
]
