from django.db import transaction
from apps.stock.models import Package, TrackingSequence
from apps.core.services.stock import PackageServiceInterface

def generate_tracking_code(tenant):
    with transaction.atomic():
        seq = (
            TrackingSequence.objects
            .select_for_update()
            .get(tenant=tenant)
        )

        seq.current_value += 1
        seq.save(update_fields=['current_value'])

        return str(seq.current_value).zfill(11)

class PackageService(PackageServiceInterface):
    def generate_tracking_code(tenant):
        with transaction.atomic():
            seq = (
                TrackingSequence.objects
                .select_for_update()
                .get(tenant=tenant)
            )

            seq.current_value += 1
            seq.save(update_fields=['current_value'])

            return str(seq.current_value).zfill(11)

    def create_generated_package(self, tenant, **data):
        tracking_code = generate_tracking_code(tenant)
        return Package.objects.create(
            tenant=tenant,
            tracking_code=tracking_code,
            status='generated',
            **data
        )