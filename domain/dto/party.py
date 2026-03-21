from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PartyDTO:
    document: str                 # CPF ou CNPJ
    document_type: str             # CPF | CNPJ
    name: str

    state_registration: Optional[str] = None

    address: Optional["AddressDTO"] = None

@dataclass(frozen=True)
class AddressDTO:
    street: str
    number: str
    complement: Optional[str]
    district: Optional[str]
    city: str
    city_code: Optional[str]
    state: str
    zip_code: str
    country: str
    country_code: str
