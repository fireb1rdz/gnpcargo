from django.apps import AppConfig

class LogisticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.logistics'
    verbose_name = 'Logistics'
    
    def ready(self): 
        from apps.logistics.module import LogisticsModule
        from domain.registry.module_registry import ModuleRegistry
        ModuleRegistry.register(
            namespace="logistics",
            service_instance=LogisticsModule,
        )
