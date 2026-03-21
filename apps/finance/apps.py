from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.finance'
    verbose_name = 'Finance'
    
    def ready(self):
        from domain.registry.module_registry import ModuleRegistry
        from domain.bootstrap.service_container import get_finance_module
        ModuleRegistry.register(
            namespace="finance",
            service_instance=get_finance_module()    
        )
