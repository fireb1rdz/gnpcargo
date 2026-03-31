from django.urls import path, include
from . import views

app_name = "logistics"
urlpatterns = [
    path('logistica/conferencia/criar', views.ConferenceCreateView.as_view(), name='conference_create'),
    path('logistica/conferencia/listar', views.ConferenceListView.as_view(), name='conference_list'),
    path('logistica/conferencia/acao/<int:conference_id>/', views.ConferenceActionView.as_view(), name='conference_action'),
    path('logistica/conferencia/adicionar_volume/<int:conference_id>/', views.ConferenceAddPackageView.as_view(), name='conference_add_package'),
    path('logistica/conferencia/remover_volume/<int:conference_id>/', views.ConferenceRemovePackageView.as_view(), name='conference_remove_package'),
    path('logistica/conferencia/items/<int:conference_id>/', views.GetConferenceItemsView.as_view(), name='conference_items'),
    path('logistica/conferencia/terminar/<int:conference_id>/', views.FinishConferenceView.as_view(), name='finish_conference'),
    path('logistica/conferencia/ler_volume/<int:conference_id>/', views.ConferenceReadPackageView.as_view(), name='conference_read_package'),
    path('api/conferencia/amount_packages_by_day/', views.AmountPackagesByDayView.as_view(), name='amount_packages_by_day'),
    path("api/conferences-in-progress/", views.conferences_in_progress, name="conferences_in_progress"),
    path("api/average-conference-time/", views.average_conference_time, name="average_conference_time"),
    path("api/conferences-with-problem/", views.conferences_with_problem, name="conferences_with_problem"),
    path("api/pending-items-by-conference/", views.pending_items_by_conference, name="pending_items_by_conference"),
    path("api/faulty-items-grouped/", views.faulty_items_grouped, name="faulty_items_grouped"),
    path("api/error-rate-rankings/", views.error_rate_rankings, name="error_rate_rankings"),
    path("api/operator-performance/", views.operator_performance, name="operator_performance"),
    path("api/volume-by-operation-type/", views.volume_by_operation_type, name="volume_by_operation_type"),
    path("api/conferences-by-period/", views.conferences_by_period, name="conferences_by_period"),
    path("api/derived-conferences/", views.derived_conferences, name="derived_conferences"),
    path("api/problematic-suppliers/", views.problematic_suppliers, name="problematic_suppliers"),
    path("api/products-with-divergence/", views.products_with_divergence, name="products_with_divergence"),
    path("api/idle-time-conferences/", views.idle_time_conferences, name="idle_time_conferences"),
    path("api/full-flow-load-unload/", views.full_flow_load_unload, name="full_flow_load_unload"),
    path("api/cancelled-conferences/", views.cancelled_conferences, name="cancelled_conferences"),
    path("api/conference-sla/", views.conference_sla, name="conference_sla"),
    path("api/full-audit/", views.full_audit, name="full_audit"),
    path("api/errors-heatmap/", views.errors_heatmap, name="errors_heatmap"),
]
