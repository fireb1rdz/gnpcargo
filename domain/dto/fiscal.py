from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
import datetime
from domain.dto.party import PartyDTO

@dataclass
class DocumentVolumeDTO:
    quantity: int
    description: Optional[str]
    weight: Optional[Decimal]
    value: Optional[Decimal]

@dataclass
class DocumentDTO:
    id: str
    model: str
    series: int
    number: int
    issue_datetime: datetime
    environment: str

    supplier: PartyDTO
    carrier: PartyDTO
    client: PartyDTO

    raw_xml: str

@dataclass 
class CTEDTO(DocumentDTO):
    cfop: str
    nature_operation: str
    modal: str
    route: dict
    freight: dict
    icms: dict
    cargo: dict
    related_nfes: list
    road: dict | None
    authorization: dict | None
    observations: list  
    modal: str
    route: dict
    freight: dict
    icms: dict
    cargo: dict
    related_nfes: list
    road: dict | None
    authorization: dict | None
    observations: list

    def iter_items(self):
        return []