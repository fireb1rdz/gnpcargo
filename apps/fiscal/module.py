# apps/fiscal/module.py

from apps.fiscal.services.cte_service import CTEService
from apps.fiscal.services.cte_importer import CTEImporter

class FiscalModule:
    def __init__(self, process_transport_document_service):
        self.cte = CTEService()
        self.cte_importer = CTEImporter()
        self.process_transport_document_service = process_transport_document_service