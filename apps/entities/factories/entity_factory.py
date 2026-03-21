from apps.entities.models import Entity

class EntityFactory:
    @staticmethod
    def create(tenant, entity_data):
        entity = Entity.objects.create(
            tenant=tenant,
            **entity_data
        )
        return entity