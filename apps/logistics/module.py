from apps.logistics.services.conference_application_service import ConferenceApplicationService
from apps.stock.services.package_service import PackageService
from apps.fiscal.services.process_transport_document_service import ProcessTransportDocumentService

class LogisticsModule:
    def __init__(self):
        self.conference_application_service = ConferenceApplicationService()
        self.package_service = PackageService()
