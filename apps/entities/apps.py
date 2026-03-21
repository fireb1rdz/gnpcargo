from django.apps import AppConfig


class EntitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.entities'
    verbose_name = 'Entities'
    
    def ready(self):
        from domain.registry.module_registry import ModuleRegistry
        from apps.entities.module import EntitiesModule
        ModuleRegistry.register(namespace='entities', service_instance=EntitiesModule)