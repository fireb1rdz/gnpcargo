from django.apps import AppConfig


class FiscalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fiscal'
    verbose_name = 'Fiscal'
    
    def ready(self):
        from domain.registry.module_registry import ModuleRegistry
        from domain.bootstrap.service_container import get_fiscal_module
        ModuleRegistry.register(
            namespace="fiscal",
            service_instance=get_fiscal_module()    
        )
