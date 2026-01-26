from django.urls import path, include
from .views import ConferenceCreateView

urlpatterns = [
    path('conferencia/criar', ConferenceCreateView.as_view(), name='conference_create'),
]
