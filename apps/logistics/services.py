# apps/conference/services.py
import xml.etree.ElementTree as ET
from django.utils.timezone import now

from .models import Conference, ConferenceItem
from apps.stock.services import PackageService
from apps.core.services.base import ModuleRegistry
from apps.core.services.logistics import ConferenceServiceInterface

class ConferenceService(ConferenceServiceInterface):

    @staticmethod
    def create_from_cte(*, tenant, user, carrier_entity, cte_files):
        fiscal = ModuleRegistry.get("fiscal")

        if not fiscal:
            raise RuntimeError("Módulo fiscal não disponível")

        for xml in cte_files:
            cte = fiscal.import_cte(xml)

            conference = Conference.objects.create(
                tenant=tenant,
                source_entity=cte.supplier,
                shipping_entity=carrier_entity,
                destination_entity=cte.client,
                invoice=cte.id,
                status="pending",
                start_date=now(),
                created_by=user,
            )

            ConferenceService._create_items_from_cte(
                tenant=tenant,
                conference=conference,
                cte=cte,
            )

    @staticmethod
    def _create_items_from_cte(*, tenant, conference, cte):
        """
        Para cada volume/produto da NF:
        - cria um Package
        - gera tracking_code sequencial
        - cria ConferenceItem
        """

        package_service = PackageService()

        for item in cte.items:
            # Se a NF não tiver volume, assume 1
            quantity = item.quantity or 1

            for _ in range(quantity):
                package = package_service.create_generated_package(
                    tenant=tenant,
                    product_description=item.description,
                )

                ConferenceItem.objects.create(
                    tenant=tenant,
                    conference=conference,
                    package=package,
                    status="pending",
                )
