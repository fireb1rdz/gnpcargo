from domain.contracts.importers.fiscal import DocumentImporter
from domain.dto.fiscal import CTEDTO
from apps.entities.services.entity_service import EntityService
from apps.entities.services.entity_address_service import EntityAddressService
import xml.etree.ElementTree as ET
from decimal import Decimal
from django.utils.dateparse import parse_datetime, parse_date

class CTEImporter(DocumentImporter):
    NS = {
        "cte": "http://www.portalfiscal.inf.br/cte",
    }

    @classmethod
    def can_import(cls, xml_file) -> bool:
        if hasattr(xml_file, "read"):
            raw_xml = xml_file.read()
        else:
            raw_xml = xml_file

        root = ET.fromstring(raw_xml)
        return root.tag.endswith("CTe")

    @classmethod
    def import_document(cls, xml_file) -> CTEDTO:
        if hasattr(xml_file, "read"):
            raw_xml = xml_file.read()
        else:
            raw_xml = xml_file

        root = ET.fromstring(raw_xml)
        inf_cte = root.find(".//cte:infCte", cls.NS)

        if inf_cte is None:
            raise ValueError("XML não é um CT-e válido")

        ide = inf_cte.find("cte:ide", cls.NS)

        chave = inf_cte.attrib.get("Id", "").replace("CTe", "")

        # ========================
        # Dados básicos do CT-e
        # ========================
        model = "57"
        series = int(cls._get_text(ide, "cte:serie"))
        number = int(cls._get_text(ide, "cte:nCT"))
        issue_datetime = parse_datetime(cls._get_text(ide, "cte:dhEmi"))
        environment = "prod" if cls._get_text(ide, "cte:tpAmb") == "1" else "test"
        cfop = cls._get_text(ide, "cte:CFOP")
        nature_operation = cls._get_text(ide, "cte:natOp")
        modal = "road"

        # ========================
        # Transportador
        # ========================
        transp = inf_cte.find("cte:transp", cls.NS)
        if cls._get_text(transp, "cte:CNPJ"):
            transp_document = cls._get_text(transp, "cte:CNPJ")
            cpforcnpj = "CNPJ"
        elif cls._get_text(transp, "cte:CPF"):
            transp_document = cls._get_text(transp, "cte:CPF")
            cpforcnpj = "CPF"
        carrier, _ = EntityService().get_or_create(
            cnpj=transp_document if transp_document else None,
            cpf=transp_document if transp_document else None,
            defaults={
                "name": cls._get_text(transp, "cte:xNome"),
                "cpforcnpj": cpforcnpj,
            },
        )
        carrier_address, _ = EntityAddressService().get_or_create(
            entity=carrier,
            defaults={
                "address": cls._get_text(transp, "cte:xLgr"),
                "number": cls._get_text(transp, "cte:nro"),
                "complement": cls._get_text(transp, "cte:xCpl"),
                "district": cls._get_text(transp, "cte:xBairro"),
                "city": cls._get_text(transp, "cte:xMun"),
                "city_code": cls._get_text(transp, "cte:cMun"),
                "state": cls._get_text(transp, "cte:UF"),
                "zip_code": cls._get_text(transp, "cte:CEP"),
                "country": cls._get_text(transp, "cte:xPais"),
                "country_code": cls._get_text(transp, "cte:cPais"),
            },
        )

        # ========================
        # Remetente
        # ========================
        rem = inf_cte.find("cte:rem", cls.NS)
        if cls._get_text(rem, "cte:CNPJ"):
            rem_document = cls._get_text(rem, "cte:CNPJ")
            cpforcnpj = "CNPJ"
        elif cls._get_text(rem, "cte:CPF"):
            rem_document = cls._get_text(rem, "cte:CPF")
            cpforcnpj = "CPF"
        sender, _ = EntityService().get_or_create(
            cnpj=rem_document if rem_document else None,
            cpf=rem_document if rem_document else None,
            defaults={
                "name": cls._get_text(rem, "cte:xNome"),
                "cpforcnpj": cpforcnpj,
            },
        )
        sender_address, _ = EntityAddressService().get_or_create(
            entity=sender,
            defaults={
                "address": cls._get_text(rem, "cte:xLgr"),
                "number": cls._get_text(rem, "cte:nro"),
                "complement": cls._get_text(rem, "cte:xCpl"),
                "district": cls._get_text(rem, "cte:xBairro"),
                "city": cls._get_text(rem, "cte:xMun"),
                "city_code": cls._get_text(rem, "cte:cMun"),
                "state": cls._get_text(rem, "cte:UF"),
                "zip_code": cls._get_text(rem, "cte:CEP"),
                "country": cls._get_text(rem, "cte:xPais"),
                "country_code": cls._get_text(rem, "cte:cPais"),
            },
        )   

        # ========================
        # Destinatário
        # ========================
        dest = inf_cte.find("cte:dest", cls.NS)
        if cls._get_text(dest, "cte:CNPJ"):
            dest_document = cls._get_text(dest, "cte:CNPJ")
            cpforcnpj = "CNPJ"
        elif cls._get_text(dest, "cte:CPF"):
            dest_document = cls._get_text(dest, "cte:CPF")
            cpforcnpj = "CPF"

        destination, _ = EntityService().get_or_create(
            cnpj=dest_document if dest_document else None,
            cpf=dest_document if dest_document else None,
            defaults={
                "name": cls._get_text(dest, "cte:xNome"),
                "cpforcnpj": cpforcnpj,
            },
        )
        destination_address, _ = EntityAddressService().get_or_create(
            entity=destination,
            defaults={
                "address": cls._get_text(dest, "cte:xLgr"),
                "number": cls._get_text(dest, "cte:nro"),
                "complement": cls._get_text(dest, "cte:xCpl"),
                "district": cls._get_text(dest, "cte:xBairro"),
                "city": cls._get_text(dest, "cte:xMun"),
                "city_code": cls._get_text(dest, "cte:cMun"),
                "state": cls._get_text(dest, "cte:UF"),
                "zip_code": cls._get_text(dest, "cte:CEP"),
                "country": cls._get_text(dest, "cte:xPais"),
                "country_code": cls._get_text(dest, "cte:cPais"),
            },
        )

        # ========================
        # Rota
        # ========================
        route = {
            "origin_city_code": cls._get_text(ide, "cte:cMunIni"),
            "origin_city_name": cls._get_text(ide, "cte:xMunIni"),
            "origin_state": cls._get_text(ide, "cte:UFIni"),
            "destination_city_code": cls._get_text(ide, "cte:cMunFim"),
            "destination_city_name": cls._get_text(ide, "cte:xMunFim"),
            "destination_state": cls._get_text(ide, "cte:UFFim"),
        }

        # ========================
        # Frete
        # ========================
        v_prest = inf_cte.find("cte:vPrest", cls.NS)
        freight = {
            "total_service": cls._get_decimal(v_prest, "cte:vTPrest"),
            "total_receivable": cls._get_decimal(v_prest, "cte:vRec"),
            "components": [
                {
                    "description": cls._get_text(comp, "cte:xNome"),
                    "amount": cls._get_decimal(comp, "cte:vComp"),
                }
                for comp in v_prest.findall("cte:Comp", cls.NS)
            ],
        }

        # ========================
        # ICMS
        # ========================
        icms00 = inf_cte.find(".//cte:ICMS00", cls.NS)
        icms = {
            "cst": cls._get_text(icms00, "cte:CST"),
            "base_value": cls._get_decimal(icms00, "cte:vBC"),
            "rate": cls._get_decimal(icms00, "cte:pICMS"),
            "tax_value": cls._get_decimal(icms00, "cte:vICMS"),
        }

        # ========================
        # Carga
        # ========================
        inf_carga = inf_cte.find("cte:infCarga", cls.NS)
        cargo = {
            "declared_value": cls._get_decimal(inf_carga, "cte:vCarga"),
            "description": cls._get_text(inf_carga, "cte:proPred"),
            "packaging": cls._get_text(inf_carga, "cte:xOutCat"),
            "measurements": [
                {
                    "type": "weight" if cls._get_text(q, "cte:tpMed") == "PESO BRUTO" else "volume",
                    "unit": cls._get_text(q, "cte:cUnid"),
                    "value": Decimal(cls._get_text(q, "cte:qCarga")),
                }
                for q in inf_carga.findall("cte:infQ", cls.NS)
            ],
        }

        # ========================
        # NF-es relacionadas
        # ========================
        related_nfes = [
            {
                "access_key": cls._get_text(nfe, "cte:chave"),
                "expected_delivery_date": parse_date(cls._get_text(nfe, "cte:dPrev")),
            }
            for nfe in inf_cte.findall(".//cte:infNFe", cls.NS)
        ]

        # ========================
        # Modal rodoviário
        # ========================
        rodo = inf_cte.find(".//cte:rodo", cls.NS)
        road = {"rntrc": cls._get_text(rodo, "cte:RNTRC")} if rodo is not None else None

        # ========================
        # Autorização
        # ========================
        prot = root.find(".//cte:protCTe", cls.NS)
        authorization = None
        if prot is not None:
            inf_prot = prot.find("cte:infProt", cls.NS)
            authorization = {
                "protocol_number": cls._get_text(inf_prot, "cte:nProt"),
                "authorization_datetime": parse_datetime(cls._get_text(inf_prot, "cte:dhRecbto")),
                "status_code": cls._get_text(inf_prot, "cte:cStat"),
                "status_message": cls._get_text(inf_prot, "cte:xMotivo"),
            }

        # ========================
        # Observações
        # ========================
        observations = [
            {
                "title": cls._get_text(obs, "cte:xCampo"),
                "text": cls._get_text(obs, "cte:xTexto"),
            }
            for obs in inf_cte.findall(".//cte:ObsCont", cls.NS)
        ]

        return CTEDTO(
            id=chave,
            model=model,
            series=series,
            number=number,
            issue_datetime=issue_datetime,
            environment=environment,
            cfop=cfop,
            nature_operation=nature_operation,
            modal=modal,
            supplier=sender,
            carrier=carrier,
            client=destination,
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