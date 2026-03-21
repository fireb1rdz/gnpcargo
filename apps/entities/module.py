from apps.entities.services.entity_service import EntityService
from apps.entities.services.party_service import PartyService


class EntitiesModule:
    def __init__(self):
        self.entity_service = EntityService()
        self.party_service = PartyService()
    
    def get_name(self):
        return "entities"