# apps/conference/services.py
import xml.etree.ElementTree as ET
from django.utils.timezone import now

from apps.logistics.models import Conference, ConferenceItem
from domain.contracts.stock import PackageServiceInterface
from domain.contracts.entity import PartyServiceInterface
from domain.dto.fiscal import CTEDTO
from apps.logistics.exceptions import PackageAlreadyReadError, PackageNotFoundError
from django.db import transaction

class ConferenceApplicationService:
    def __init__(self, package_service: PackageServiceInterface, party_service: PartyServiceInterface):
        self.package_service = package_service
        self.party_service = party_service

    def create_conference_by_access_key(
        self, tenant, user, origin, destination, event_type, access_keys
    ):
        conferences = []

        with transaction.atomic():
            for access_key in access_keys:

                last_conference = (
                    Conference.objects
                    .filter(tenant=tenant, document_number=access_key, status="finished")
                    .order_by("-id")
                    .first()
                )

                mode = "read" if last_conference else "write"

                conference = Conference.objects.create(
                    tenant=tenant,
                    created_by=user,
                    origin=origin,
                    destination=destination,
                    event_type=event_type,
                    document_number=access_key,
                    document_type="invoice",
                    mode=mode
                )

                if last_conference:
                    items = ConferenceItem.objects.filter(
                        tenant=tenant,
                        conference=last_conference
                    )

                    new_items = [
                        ConferenceItem(
                            tenant=tenant,
                            conference=conference,
                            package=item.package,
                            status="pending"
                        )
                        for item in items
                    ]

                    ConferenceItem.objects.bulk_create(new_items)

                conferences.append(conference)

        return conferences

    def create_from_dto(self, tenant, user, supplier, carrier, client, dto: CTEDTO):
        for nfe in dto.related_nfes:
            conference = Conference.objects.create(
                tenant=tenant,
                supplier=supplier,
                carrier=carrier,
                client=client,
                document_number=nfe.access_key,
                status="pending",
                created_by=user,
            )

        self.create_items_from_dto(
            tenant=tenant,
            conference=conference,
            dto=dto,
        )

    def create_items_from_dto(self, tenant, conference, dto):
        for _ in range(dto.quantity):
            package = self.package_service.create_generated_package(
                tenant=tenant,
                product_description=dto.description,
            )

            ConferenceItem.objects.create(
                tenant=tenant,
                conference=conference,
                package=package,
                status="pending",
            )

    def add_package_to_conference(self, tenant, user, conference_id, package_code, status):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        package = self.package_service.create_generated_package(
            tenant=tenant,
            user=user,
            holder=conference.origin,
            package_code=package_code,
        )
        conference_item = ConferenceItem.objects.create(
            tenant=tenant,
            conference=conference,
            package=package,
            status=status,
        )

        conference.items.add(conference_item)

    def remove_package_from_conference(self, tenant, conference_id, package_code):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        package = self.package_service.get_package_by_code(tenant, package_code)
        conference_item = ConferenceItem.objects.filter(tenant=tenant, conference=conference, package=package).first()
        if conference_item:
            conference_item.delete()

    def get_origin(self, tenant, conference_id):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        return conference.origin

    def get_conference_items(self, tenant, conference_id):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        return conference.items.all()

    def finish_conference(self, tenant, conference_id, user):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        if self.party_service.party_is_system(conference.destination):
            self.create_conference_in_destination(tenant, conference_id, user)
        conference.status = "finished"
        conference.finished_by = user
        conference.end_date = now()
        conference.save()

    def start_conference(self, tenant, conference_id, user):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        conference.status = "in_progress"
        conference.started_by = user
        conference.start_date = now()
        conference.save()

    def create_conference_in_destination(self, tenant, conference_id, user):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        conference_items = conference.items.all()
        conference_in_destination = Conference.objects.create(
            tenant=tenant,
            created_by=user,
            parent_conference=conference,
            origin=conference.origin,
            destination=conference.destination,
            status="pending",
            event_type="unload",
            document_number=conference.document_number,
            document_type=conference.document_type,
            mode="read"
        )
        conference_in_destination_items = []
        for conference_item in conference_items:
            conference_in_destination_items.append(ConferenceItem(tenant=tenant, conference=conference_in_destination, package=conference_item.package, status="pending"))
        
        ConferenceItem.objects.bulk_create(conference_in_destination_items)

    def read_package_from_conference(self, tenant, conference_id, package_code, user):
        conference = Conference.objects.get(tenant=tenant, id=conference_id)
        package = self.package_service.get_package_by_code(tenant, package_code)
        if not package:
            raise PackageNotFoundError("Package not found in conference")
        conference_item = ConferenceItem.objects.filter(tenant=tenant, conference=conference, package=package).first()
        if not conference_item:
            raise PackageNotFoundError("Package not found in conference")
        if conference_item.status == "ok":
            raise PackageAlreadyReadError("Package already read")
        conference_item.status = "ok"
        conference_item.read_by = user
        conference_item.read_at = now()
        conference_item.save()