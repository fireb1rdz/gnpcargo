from django.urls import path
from apps.entities.views import EntityCreateView, EntityListView, EntityUpdateView, EntityDeleteView

app_name = 'entities'
urlpatterns = [
    path("entidades/criar/", EntityCreateView.as_view(), name="entity_create"),
    path("entidades/listar/", EntityListView.as_view(), name="entity_list"),
    path("entidades/editar/<int:pk>/", EntityUpdateView.as_view(), name="entity_update"),
    path("entidades/excluir/<int:pk>/", EntityDeleteView.as_view(), name="entity_delete"),
]