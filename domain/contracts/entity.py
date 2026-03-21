from abc import ABC, abstractmethod
from apps.entities.models import Entity

class EntityServiceInterface(ABC):
    @abstractmethod
    def create_entity(self, tenant, entity_data):
        pass
    
    @abstractmethod
    def get_or_create(self, tenant, entity_data):
        pass

    @abstractmethod
    def update_entity(self, tenant, entity_id, entity_data):
        pass

    @abstractmethod
    def delete_entity(self, tenant, entity_id):
        pass

    @abstractmethod
    def list_entities(self, tenant):
        pass

    @abstractmethod
    def get_entity(self, tenant, entity_id):
        pass

class EntityAddressServiceInterface(ABC):
    @abstractmethod
    def create_entity_address(self, tenant, entity_id, entity_address_data):
        pass
    
    @abstractmethod
    def get_or_create_entity_address(self, tenant, entity_id, entity_address_data):
        pass

    @abstractmethod
    def update_entity_address(self, tenant, entity_id, entity_address_id, entity_address_data):
        pass

    @abstractmethod
    def delete_entity_address(self, tenant, entity_id, entity_address_id):
        pass

    @abstractmethod
    def list_entity_addresses(self, tenant, entity_id):
        pass

    @abstractmethod
    def get_entity_address(self, tenant, entity_id, entity_address_id):
        pass

class PartyServiceInterface(ABC):
    @abstractmethod
    def create_party(self, tenant, party_data):
        pass

    @abstractmethod
    def can_be(self, entity: Entity, role: str):
        """
        Verifica se a entity pode ser um party.
        """
        pass

    @abstractmethod
    def sync_entity_roles(self, entity, selected_roles):
        """
        Sincroniza papéis de uma entidade com base nos selecionados no formulário.
        """
        pass

    @abstractmethod
    def get_roles_for_entity(self, entity):
        """
        Retorna os papéis da entity.
        """
        pass