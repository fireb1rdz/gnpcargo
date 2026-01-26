from abc import ABC, abstractmethod

class LogisticsServiceInterface(ABC):
    pass

class ConferenceServiceInterface(ABC):
    @abstractmethod
    def create_from_xml(self, tenant, user, carrier_entity, xml_files):
        pass