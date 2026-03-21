from abc import ABC, abstractmethod
from domain.contracts.logistics import ConferenceSource
from decimal import Decimal

class DocumentImporter(ABC):
    NS: dict

    @classmethod
    @abstractmethod
    def can_import(cls, root) -> bool:
        pass

    @classmethod
    @abstractmethod
    def import_document(cls, xml) -> ConferenceSource:
        pass

    @classmethod
    def _get_text(cls, node, path, default=None):
        el = node.find(path, cls.NS)
        return el.text.strip() if el is not None and el.text else default

    @classmethod
    def _get_decimal(cls, node, path, default=Decimal("0.00")):
        value = cls._get_text(node, path)
        return Decimal(value) if value else default

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "NS") or not cls.NS:
            raise TypeError(
                f"{cls.__name__} deve definir o atributo de classe NS"
            )