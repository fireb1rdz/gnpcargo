from abc import ABC, abstractmethod

class EntityServiceInterface(ABC):
    @abstractmethod
    def create_entity(self, tenant, data):
        pass

    @abstractmethod
    def update_entity(self, entity, data):
        pass

    @abstractmethod
    def delete_entity(self, entity):
        pass

    @abstractmethod
    def list_entities(self, tenant):
        pass

    @abstractmethod
    def get_entity(self, tenant, entity_id):
        pass

class EntityAddressServiceInterface(ABC):
    @abstractmethod
    def create_entity_address(self, entity, data):
        pass

    @abstractmethod
    def update_entity_address(self, entity_address, data):
        pass

    @abstractmethod
    def delete_entity_address(self, entity_address):
        pass

    @abstractmethod
    def list_entity_addresses(self, entity):
        pass

    @abstractmethod
    def get_entity_address(self, entity_address_id):
        pass