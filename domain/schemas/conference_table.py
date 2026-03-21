# domain/schemas/conference_table.py

from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Column:
    label: str
    attr: str


# class ConferenceTableSchema:
#     @staticmethod
#     def for_role(role: str) -> List[Column]:
#         if role == "carrier":
#             return [
#                 Column("Fornecedor", "supplier.entity.name"),
#                 Column("Data", "date"),
#                 Column("Horário", "time"),
#                 Column("Local de Coleta", "location"),
#             ]

#         if role == "client":
#             return [
#                 Column("Transportadora", "carrier.entity.name"),
#                 Column("Data", "date"),
#                 Column("Horário", "time"),
#                 Column("Destino", "destination"),
#             ]

#         raise ValueError(f"Unsupported role: {role}")
