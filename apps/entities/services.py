from .models import Entity, EntityAddress
from apps.core.services.entities import EntityServiceInterface, EntityAddressServiceInterface

class EntityService(EntityServiceInterface):
    def create_entity(self, tenant, data):
        entity = Entity.objects.create(tenant=tenant, **data)
        return entity

    def update_entity(self, entity, data):
        entity.update(**data)
        return entity

    def delete_entity(self, entity):
        entity.delete()
        return entity

    def list_entities(self, tenant):
        return Entity.objects.filter(tenant=tenant)

    def get_entity(self, tenant, entity_id):
        return Entity.objects.get(tenant=tenant, id=entity_id)

    def get_or_create(self, tenant, document, defaults=None):
        defaults = defaults or {}
        entity, created = Entity.objects.get_or_create(
            tenant=tenant,
            document=document,
            defaults=defaults,
        )
        return entity

class EntityAddressService(EntityAddressServiceInterface):
    def create_entity_address(self, entity, data):
        entity_address = EntityAddress.objects.create(entity=entity, **data)
        return entity_address

    def update_entity_address(self, entity_address, data):
        entity_address.update(**data)
        return entity_address

    def delete_entity_address(self, entity_address):
        entity_address.delete()
        return entity_address

    def list_entity_addresses(self, entity):
        return EntityAddress.objects.filter(entity=entity)

    def get_entity_address(self, entity_address_id):
        return EntityAddress.objects.get(id=entity_address_id)