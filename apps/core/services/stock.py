from django.db import transaction
from abc import ABC, abstractmethod
from apps.stock.models import Package, TrackingSequence


class PackageServiceInterface(ABC):
    @abstractmethod
    def generate_tracking_code(self, tenant):
        pass
    @abstractmethod
    def create_generated_package(self, tenant, **data):
        pass

