from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal
import datetime

@dataclass
class CTeVolumeDTO:
    quantity: int
    description: Optional[str]
    weight: Optional[Decimal]
    value: Optional[Decimal]


@dataclass
class CTeDTO:
    id: str
    model: str
    series: int
    number: int
    issue_datetime: datetime.datetime
    environment: str
    cfop: str
    nature_operation: str
    modal: str

    supplier: object
    client: object

    route: dict
    freight: dict
    icms: dict
    cargo: dict
    related_nfes: list
    road: dict | None
    authorization: dict | None
    observations: list

    raw_xml: str
