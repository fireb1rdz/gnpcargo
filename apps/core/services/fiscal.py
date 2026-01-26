from abc import ABC, abstractmethod

class FiscalServiceInterface(ABC):
    @abstractmethod
    def import_cte(self, xml):
        """
        Importa um XML de CT-e e retorna um objeto com os dados.
        """
        pass

    @abstractmethod
    def import_nfe(self, xml):
        """
        Importa um XML de NFe e retorna um objeto com os dados.
        """
        pass