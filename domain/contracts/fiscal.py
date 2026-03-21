from abc import ABC, abstractmethod
from domain.dto.fiscal import DocumentDTO

class FiscalServiceInterface(ABC):
    @abstractmethod
    def import_document(self, xml):
        """
        Importa um XML de documento fiscal e retorna um objeto com os dados.
        """
        pass

    @abstractmethod
    def create_model_from_dto(self, dto: DocumentDTO):
        """
        Cria um modelo a partir de um DTO.
        """
        pass
