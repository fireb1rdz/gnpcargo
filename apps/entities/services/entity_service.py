from domain.contracts.entity import EntityServiceInterface
from apps.entities.factories.entity_factory import EntityFactory

class EntityService(EntityServiceInterface):
    def create_entity(self, tenant, entity_data):
        entity = EntityFactory.create(tenant, entity_data)
        return entity