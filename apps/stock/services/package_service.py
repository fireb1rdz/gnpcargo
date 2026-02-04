from django.db import transaction
from apps.stock.models import Package, TrackingSequence
from domain.contracts.stock import PackageServiceInterface

class PackageService(PackageServiceInterface):
    def generate_tracking_code(self, tenant):
        with transaction.atomic():
            seq = (
                TrackingSequence.objects
                .select_for_update()
                .get(tenant=tenant)
            )

            seq.current_value += 1
            seq.save(update_fields=['current_value'])

            return str(seq.current_value).zfill(11)

    def create_generated_package(self, tenant, user, holder, package_code=None):
        if not package_code:
            tracking_code = self.generate_tracking_code(tenant)
        else:
            tracking_code = package_code
        return Package.objects.create(
            tenant=tenant,
            tracking_code=tracking_code,
            status='generated',
            created_by=holder,
            holder=holder
        )
    
    def get_package_by_code(self, tenant, package_code):
        return Package.objects.get(tenant=tenant, tracking_code=package_code)