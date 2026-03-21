import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ModuleRegistry:
    """
    A central registry where modules can register their public services/interfaces.
    This allows 'sales' to call 'finance' without importing it directly.
    """
    _services = {}

    @classmethod
    def register(cls, namespace: str, service_instance):
        """
        Register a service implementation under a namespace (e.g., 'finance').
        """
        cls._services[namespace] = service_instance
        logger.info(f"Service registered: {namespace}")

    @classmethod
    def get(cls, namespace: str):
        """
        Get a service. Returns a NullService if not found to prevent crashes.
        """
        service = cls._services.get(namespace)
        if not service:
            return NullService(namespace)
        return service

class NullService:
    """
    A dummy service that absorbs calls safely when a module is missing.
    """
    def __init__(self, namespace):
        self.namespace = namespace

    def __getattr__(self, name):
        def method(*args, **kwargs):
            logger.warning(
                f"Attempted to call '{name}' on missing module '{self.namespace}'. "
                f"Call ignored."
            )
            return None
        return method
