from apps.core.services.fiscal import FiscalServiceInterface
from fiscal.dto import CTeDTO, CTeVolumeDTO
from apps.entities.services import EntityService, EntityAddressService

import xml.etree.ElementTree as ET
from decimal import Decimal
from django.utils.dateparse import parse_datetime, parse_date


NS = {"cte": "http://www.portalfiscal.inf.br/cte"}


def _get_text(node, path, default=None):
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else default


def _get_decimal(node, path, default=Decimal("0.00")):
    value = _get_text(node, path)
    return Decimal(value) if value else default


class FiscalService(FiscalServiceInterface):

    def import_cte(self, xml_file) -> CTeDTO:
        if hasattr(xml_file, "read"):
            raw_xml = xml_file.read()
        else:
            raw_xml = xml_file

        root = ET.fromstring(raw_xml)
        inf_cte = root.find(".//cte:infCte", NS)

        if inf_cte is None:
            raise ValueError("XML não é um CT-e válido")

        ide = inf_cte.find("cte:ide", NS)

        chave = inf_cte.attrib.get("Id", "").replace("CTe", "")

        # ========================
        # Dados básicos do CT-e
        # ========================
        model = "57"
        series = int(_get_text(ide, "cte:serie"))
        number = int(_get_text(ide, "cte:nCT"))
        issue_datetime = parse_datetime(_get_text(ide, "cte:dhEmi"))
        environment = "prod" if _get_text(ide, "cte:tpAmb") == "1" else "test"
        cfop = _get_text(ide, "cte:CFOP")
        nature_operation = _get_text(ide, "cte:natOp")
        modal = "road"

        # ========================
        # Remetente
        # ========================
        rem = inf_cte.find("cte:rem", NS)
        if _get_text(rem, "cte:CNPJ"):
            rem_document = _get_text(rem, "cte:CNPJ")
            cpforcnpj = "CNPJ"
        elif _get_text(rem, "cte:CPF"):
            rem_document = _get_text(rem, "cte:CPF")
            cpforcnpj = "CPF"
        sender, _ = EntityService().get_or_create(
            cnpj=rem_document if rem_document else None,
            cpf=rem_document if rem_document else None,
            defaults={
                "name": _get_text(rem, "cte:xNome"),
                "cpforcnpj": cpforcnpj,
            },
        )
        sender_address, _ = EntityAddressService().get_or_create(
            entity=sender,
            defaults={
                "address": _get_text(rem, "cte:xLgr"),
                "number": _get_text(rem, "cte:nro"),
                "complement": _get_text(rem, "cte:xCpl"),
                "district": _get_text(rem, "cte:xBairro"),
                "city": _get_text(rem, "cte:xMun"),
                "city_code": _get_text(rem, "cte:cMun"),
                "state": _get_text(rem, "cte:UF"),
                "zip_code": _get_text(rem, "cte:CEP"),
                "country": _get_text(rem, "cte:xPais"),
                "country_code": _get_text(rem, "cte:cPais"),
            },
        )   

        # ========================
        # Destinatário
        # ========================
        dest = inf_cte.find("cte:dest", NS)
        if _get_text(dest, "cte:CNPJ"):
            dest_document = _get_text(dest, "cte:CNPJ")
            cpforcnpj = "CNPJ"
        elif _get_text(dest, "cte:CPF"):
            dest_document = _get_text(dest, "cte:CPF")
            cpforcnpj = "CPF"

        destination, _ = EntityService().get_or_create(
            cnpj=dest_document if dest_document else None,
            cpf=dest_document if dest_document else None,
            defaults={
                "name": _get_text(dest, "cte:xNome"),
                "cpforcnpj": cpforcnpj,
            },
        )
        destination_address, _ = EntityAddressService().get_or_create(
            entity=destination,
            defaults={
                "address": _get_text(dest, "cte:xLgr"),
                "number": _get_text(dest, "cte:nro"),
                "complement": _get_text(dest, "cte:xCpl"),
                "district": _get_text(dest, "cte:xBairro"),
                "city": _get_text(dest, "cte:xMun"),
                "city_code": _get_text(dest, "cte:cMun"),
                "state": _get_text(dest, "cte:UF"),
                "zip_code": _get_text(dest, "cte:CEP"),
                "country": _get_text(dest, "cte:xPais"),
                "country_code": _get_text(dest, "cte:cPais"),
            },
        )

        # ========================
        # Rota
        # ========================
        route = {
            "origin_city_code": _get_text(ide, "cte:cMunIni"),
            "origin_city_name": _get_text(ide, "cte:xMunIni"),
            "origin_state": _get_text(ide, "cte:UFIni"),
            "destination_city_code": _get_text(ide, "cte:cMunFim"),
            "destination_city_name": _get_text(ide, "cte:xMunFim"),
            "destination_state": _get_text(ide, "cte:UFFim"),
        }

        # ========================
        # Frete
        # ========================
        v_prest = inf_cte.find("cte:vPrest", NS)
        freight = {
            "total_service": _get_decimal(v_prest, "cte:vTPrest"),
            "total_receivable": _get_decimal(v_prest, "cte:vRec"),
            "components": [
                {
                    "description": _get_text(comp, "cte:xNome"),
                    "amount": _get_decimal(comp, "cte:vComp"),
                }
                for comp in v_prest.findall("cte:Comp", NS)
            ],
        }

        # ========================
        # ICMS
        # ========================
        icms00 = inf_cte.find(".//cte:ICMS00", NS)
        icms = {
            "cst": _get_text(icms00, "cte:CST"),
            "base_value": _get_decimal(icms00, "cte:vBC"),
            "rate": _get_decimal(icms00, "cte:pICMS"),
            "tax_value": _get_decimal(icms00, "cte:vICMS"),
        }

        # ========================
        # Carga
        # ========================
        inf_carga = inf_cte.find("cte:infCarga", NS)
        cargo = {
            "declared_value": _get_decimal(inf_carga, "cte:vCarga"),
            "description": _get_text(inf_carga, "cte:proPred"),
            "packaging": _get_text(inf_carga, "cte:xOutCat"),
            "measurements": [
                {
                    "type": "weight" if _get_text(q, "cte:tpMed") == "PESO BRUTO" else "volume",
                    "unit": _get_text(q, "cte:cUnid"),
                    "value": Decimal(_get_text(q, "cte:qCarga")),
                }
                for q in inf_carga.findall("cte:infQ", NS)
            ],
        }

        # ========================
        # NF-es relacionadas
        # ========================
        related_nfes = [
            {
                "access_key": _get_text(nfe, "cte:chave"),
                "expected_delivery_date": parse_date(_get_text(nfe, "cte:dPrev")),
            }
            for nfe in inf_cte.findall(".//cte:infNFe", NS)
        ]

        # ========================
        # Modal rodoviário
        # ========================
        rodo = inf_cte.find(".//cte:rodo", NS)
        road = {"rntrc": _get_text(rodo, "cte:RNTRC")} if rodo is not None else None

        # ========================
        # Autorização
        # ========================
        prot = root.find(".//cte:protCTe", NS)
        authorization = None
        if prot is not None:
            inf_prot = prot.find("cte:infProt", NS)
            authorization = {
                "protocol_number": _get_text(inf_prot, "cte:nProt"),
                "authorization_datetime": parse_datetime(_get_text(inf_prot, "cte:dhRecbto")),
                "status_code": _get_text(inf_prot, "cte:cStat"),
                "status_message": _get_text(inf_prot, "cte:xMotivo"),
            }

        # ========================
        # Observações
        # ========================
        observations = [
            {
                "title": _get_text(obs, "cte:xCampo"),
                "text": _get_text(obs, "cte:xTexto"),
            }
            for obs in inf_cte.findall(".//cte:ObsCont", NS)
        ]

        return CTeDTO(
            id=chave,
            model=model,
            series=series,
            number=number,
            issue_datetime=issue_datetime,
            environment=environment,
            cfop=cfop,
            nature_operation=nature_operation,
            modal=modal,
            supplier=supplier,
            client=client,
            route=route,
            freight=freight,
            icms=icms,
            cargo=cargo,
            related_nfes=related_nfes,
            road=road,
            authorization=authorization,
            observations=observations,
            raw_xml=raw_xml.decode() if isinstance(raw_xml, bytes) else raw_xml,
        )

    def import_nfe(self, xml):
        pass