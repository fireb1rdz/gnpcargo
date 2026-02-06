from django.urls import path, include
from .views import ConferenceCreateView, ConferenceListView, ConferenceActionView, ConferenceAddPackageView, ConferenceRemovePackageView, GetConferenceItemsView, FinishConferenceView, ConferenceReadPackageView

app_name = "logistics"
urlpatterns = [
    path('logistica/conferencia/criar', ConferenceCreateView.as_view(), name='conference_create'),
    path('logistica/conferencia/listar', ConferenceListView.as_view(), name='conference_list'),
    path('logistica/conferencia/acao/<int:conference_id>/', ConferenceActionView.as_view(), name='conference_action'),
    path('logistica/conferencia/adicionar_volume/<int:conference_id>/', ConferenceAddPackageView.as_view(), name='conference_add_package'),
    path('logistica/conferencia/remover_volume/<int:conference_id>/', ConferenceRemovePackageView.as_view(), name='conference_remove_package'),
    path('logistica/conferencia/items/<int:conference_id>/', GetConferenceItemsView.as_view(), name='conference_items'),
    path('logistica/conferencia/terminar/<int:conference_id>/', FinishConferenceView.as_view(), name='finish_conference'),
    path('logistica/conferencia/ler_volume/<int:conference_id>/', ConferenceReadPackageView.as_view(), name='conference_read_package'),
]
