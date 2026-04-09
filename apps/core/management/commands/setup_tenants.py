from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from django.utils.text import slugify
from django_tenants.utils import (
    get_tenant_model,
    get_public_schema_name,
)


def get_domain_model():
    return apps.get_model(settings.TENANT_DOMAIN_MODEL)


class Command(BaseCommand):
    help = "Garante tenant público + tenant principal com domínio."

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="cargo.gnpsistemas.com.br",
        )
        parser.add_argument(
            "--tenant-name",
            default="GNP Sistemas",
        )
        parser.add_argument(
            "--schema",
            default="gnp",  # 👈 tenant real
        )

    def handle(self, *args, **options):
        TenantModel = get_tenant_model()
        DomainModel = get_domain_model()

        domain_name = options["domain"].strip().lower()
        tenant_name = options["tenant_name"].strip()
        schema_name = options["schema"].strip().lower()
        public_schema = get_public_schema_name()

        self.stdout.write(f"Inicializando tenants...")

        # =========================================
        # 1) GARANTE PUBLIC (infra)
        # =========================================
        public = TenantModel.objects.filter(schema_name=public_schema).first()

        if not public:
            public = TenantModel.objects.create(
                schema_name=public_schema,
                name="Public"
            )
            self.stdout.write(self.style.SUCCESS("Public criado"))
        else:
            self.stdout.write("Public já existe")

        # =========================================
        # 2) GARANTE TENANT REAL (gnp)
        # =========================================
        tenant = TenantModel.objects.filter(schema_name=schema_name).first()

        if not tenant:
            tenant = TenantModel.objects.create(
                schema_name=schema_name,
                name=tenant_name,
                slug=slugify(tenant_name),
            )
            self.stdout.write(
                self.style.SUCCESS(f"Tenant '{schema_name}' criado")
            )
        else:
            changed = False

            if hasattr(tenant, "name") and tenant.name != tenant_name:
                tenant.name = tenant_name
                changed = True

            if hasattr(tenant, "slug"):
                new_slug = slugify(tenant_name)
                if tenant.slug != new_slug:
                    tenant.slug = new_slug
                    changed = True

            if changed:
                tenant.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Tenant '{schema_name}' atualizado")
                )
            else:
                self.stdout.write(f"Tenant '{schema_name}' já existe")

        # =========================================
        # 3) GARANTE DOMAIN
        # =========================================
        domain = DomainModel.objects.filter(domain=domain_name).first()

        if not domain:
            DomainModel.objects.create(
                domain=domain_name,
                tenant=tenant,  # 👈 IMPORTANTE (não é public)
                is_primary=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Domínio '{domain_name}' criado")
            )
        else:
            changed = False

            if domain.tenant_id != tenant.id:
                domain.tenant = tenant
                changed = True

            if not domain.is_primary:
                domain.is_primary = True
                changed = True

            if changed:
                domain.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Domínio '{domain_name}' atualizado")
                )
            else:
                self.stdout.write(f"Domínio '{domain_name}' já existe")

        self.stdout.write(self.style.SUCCESS("Ambiente pronto "))