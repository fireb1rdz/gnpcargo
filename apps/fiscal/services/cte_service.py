from domain.dto.fiscal import CTEDTO
from django.db import transaction
from apps.fiscal.models import (
    TransportDocument,
    TransportRoute,
    Issuer,
    TransportParty,
    FreightValue,
    FreightComponent,
    ICMS,
    Cargo,
    CargoMeasurement,
    RelatedNFe,
    RoadTransport,
    TransportAuthorization,
    TransportObservation,
)

import xml.etree.ElementTree as ET
from decimal import Decimal
from django.utils.dateparse import parse_datetime, parse_date


NS = {
    "cte": "http://www.portalfiscal.inf.br/cte",
    "nfe": "http://www.portalfiscal.inf.br/nfe",
}


def _get_text(node, path, default=None):
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else default


def _get_decimal(node, path, default=Decimal("0.00")):
    value = _get_text(node, path)
    return Decimal(value) if value else default

class CTEService:
    @transaction.atomic
    def create_models_from_dto(self, dto: CTEDTO) -> TransportDocument:
        document = TransportDocument.objects.create(
            tenant=dto.tenant,
            internal_code=dto.id,
            fiscal_key=dto.fiscal_key,
            model=dto.model,
            series=dto.series,
            number=dto.number,
            issue_datetime=dto.issue_datetime,
            environment=dto.environment,
            cfop=dto.cfop,
            nature_operation=dto.nature_operation,
            modal=dto.modal,
            status="authorized",
        )

        # ---------- ROUTE ----------
        TransportRoute.objects.create(
            tenant=dto.tenant,
            document=document,
            origin_city_code=dto.route["origin_city_code"],
            origin_city_name=dto.route["origin_city_name"],
            origin_state=dto.route["origin_state"],
            destination_city_code=dto.route["destination_city_code"],
            destination_city_name=dto.route["destination_city_name"],
            destination_state=dto.route["destination_state"],
        )

        # ---------- ISSUER ----------
        Issuer.objects.create(
            tenant=dto.tenant,
            document=document,
            cnpj=dto.supplier.document,
            state_registration=dto.supplier.state_registration,
            legal_name=dto.supplier.legal_name,
            trade_name=dto.supplier.trade_name,
            tax_regime=dto.supplier.tax_regime,
        )

        # ---------- PARTIES ----------
        self._create_party(document, dto.supplier, "sender")
        self._create_party(document, dto.client, "recipient")

        # ---------- FREIGHT ----------
        freight = FreightValue.objects.create(
            tenant=dto.tenant,
            document=document,
            total_service=dto.freight["total_service"],
            total_receivable=dto.freight["total_receivable"],
        )

        for comp in dto.freight.get("components", []):
            FreightComponent.objects.create(
                tenant=dto.tenant,
                freight=freight,
                description=comp["description"],
                amount=comp["amount"],
            )

        # ---------- ICMS ----------
        ICMS.objects.create(
            tenant=dto.tenant,
            document=document,
            cst=dto.icms["cst"],
            base_value=dto.icms["base_value"],
            rate=dto.icms["rate"],
            tax_value=dto.icms["tax_value"],
        )

        # ---------- CARGO ----------
        cargo = Cargo.objects.create(
            document=document,
            declared_value=dto.cargo["declared_value"],
            description=dto.cargo["description"],
            packaging=dto.cargo["packaging"],
        )

        for m in dto.cargo.get("measurements", []):
            CargoMeasurement.objects.create(
                cargo=cargo,
                type=m["type"],
                unit=m["unit"],
                value=m["value"],
            )

        # ---------- RELATED NFEs ----------
        for nfe in dto.related_nfes:
            RelatedNFe.objects.create(
                tenant=dto.tenant,
                document=document,
                access_key=nfe["access_key"],
                expected_delivery_date=nfe.get("expected_delivery_date"),
            )

        # ---------- ROAD ----------
        if dto.road:
            RoadTransport.objects.create(
                tenant=dto.tenant,
                document=document,
                rntrc=dto.road["rntrc"],
            )

        # ---------- AUTHORIZATION ----------
        if dto.authorization:
            TransportAuthorization.objects.create(
                tenant=dto.tenant,
                document=document,
                protocol_number=dto.authorization["protocol_number"],
                authorization_datetime=dto.authorization["authorization_datetime"],
                status_code=dto.authorization["status_code"],
                status_message=dto.authorization["status_message"],
            )

        # ---------- OBSERVATIONS ----------
        for obs in dto.observations:
            TransportObservation.objects.create(
                tenant=dto.tenant,
                document=document,
                title=obs["title"],
                text=obs["text"],
            )

        return document

    def _create_party(self, document, party_dto, party_type):
        TransportParty.objects.create(
            tenant=document.tenant,
            document=document,
            type=party_type,
            cnpj=party_dto.document,
            state_registration=party_dto.state_registration,
            name=party_dto.name,
            phone=party_dto.phone,
        )