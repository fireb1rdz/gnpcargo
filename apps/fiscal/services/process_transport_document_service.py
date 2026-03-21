from apps.fiscal.services.cte_importer import CTEImporter
from apps.entities.services.party_service import PartyService
from apps.entities.models import PartyRole
# from apps.fiscal.services.nfe_importer import NFEImporter

class ProcessTransportDocumentService:
    def __init__(self, conference_application_service):
        self.cte_importer = CTEImporter()
        # self.nfe_importer = NFEImporter()
        self.conference_application_service = conference_application_service

    def import_and_create_models(self, tenant, user, client, carrier, supplier, files):
        client = PartyService.create_party(tenant=tenant, entity=client, role=PartyRole.CLIENT)
        carrier = PartyService.create_party(tenant=tenant, entity=carrier, role=PartyRole.CARRIER)
        supplier = PartyService.create_party(tenant=tenant, entity=supplier, role=PartyRole.SUPPLIER)
        for file in files:
            if self.cte_importer.can_import(file):
                ctedto = self.cte_importer.import_document(file)
                self.conference_application_service.create_from_dto(tenant, user, client, carrier, supplier, ctedto)
                self.cte_service.create_models_from_dto(ctedto)
            else:
                raise ValueError("Arquivo não é um XML válido")
            # elif self.nfe_importer.can_import(file):
            #     self.nfe_importer.import_document(tenant, user, carrier, file)
    # def create_from_nfe(self, tenant, user, carrier, nfe_files):
    #     self.nfe_importer.import_document(tenant, user, carrier, nfe_files)