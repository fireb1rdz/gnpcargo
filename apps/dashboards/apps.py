from django.apps import AppConfig


class DashboardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboards'
    verbose_name = 'Dashboards'
    
    def ready(self):
        from domain.registry.module_registry import ModuleRegistry
        from domain.bootstrap.service_container import get_dashboards_module
        ModuleRegistry.register(
            namespace="dashboards",
            service_instance=get_dashboards_module()    
        )
