from domain.contracts.entity import EntityAddressServiceInterface

class EntityAddressService(EntityAddressServiceInterface):
    def create_entity_address(self, tenant, entity_id, entity_address_data):
        pass
    
    def get_or_create_entity_address(self, tenant, entity_id, entity_address_data):
        pass

    def update_entity_address(self, tenant, entity_id, entity_address_id, entity_address_data):
        pass

    def delete_entity_address(self, tenant, entity_id, entity_address_id):
        pass

    def list_entity_addresses(self, tenant, entity_id):
        pass

    def get_entity_address(self, tenant, entity_id, entity_address_id):
        pass
