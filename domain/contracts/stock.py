from abc import ABC, abstractmethod

class PackageServiceInterface(ABC):
    @abstractmethod
    def generate_tracking_code(self, tenant):
        pass

    @abstractmethod
    def create_generated_package(self, tenant, **data):
        pass
