from domain.contracts.entity import PartyServiceInterface
from apps.entities.services.party_service import PartyService
from apps.logistics.services.conference_application_service import ConferenceApplicationService
from domain.contracts.logistics import ConferenceServiceInterface
from domain.contracts.stock import PackageServiceInterface
from apps.stock.services.package_service import PackageService
from apps.fiscal.services.process_transport_document_service import ProcessTransportDocumentService
from apps.fiscal.module import FiscalModule

def get_party_service() -> PartyServiceInterface:
    return PartyService()

def get_conference_application_service() -> ConferenceServiceInterface:
    return ConferenceApplicationService(get_package_service(), get_party_service())

def get_package_service() -> PackageServiceInterface:
    return PackageService()

def get_process_transport_document_service() -> ProcessTransportDocumentService:
    return ProcessTransportDocumentService(
        conference_application_service=get_conference_application_service()
    )

def get_fiscal_module():
    return FiscalModule(
        process_transport_document_service=get_process_transport_document_service()
    )