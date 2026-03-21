from typing import Protocol, Iterable
from domain.dto.party import PartyDTO
from decimal import Decimal
from abc import ABC, abstractmethod

class ConferenceSource(Protocol):
    id: str
    supplier: PartyDTO
    carrier: PartyDTO
    client: PartyDTO

    def iter_items(self) -> Iterable["ConferenceSourceItem"]:
        ...

class ConferenceSourceItem(Protocol):
    id: str
    description: str
    quantity: int
    unit_price: Decimal

class ConferenceServiceInterface(ABC):
    @abstractmethod
    def create_from_xml(self, tenant, user, carrier_entity, xml_files):
        pass

class ConferenceApplicationServiceInterface(ABC):
    @abstractmethod
    def create_conference(self, tenant, user, carrier_entity, xml_files):
        pass