from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from django.apps import apps
from django.db import transaction
from django_tenants.utils import (
    get_tenant_model,
    get_public_schema_name,
    schema_context,
)

def get_domain_model():
    return apps.get_model(settings.TENANT_DOMAIN_MODEL)


class Command(BaseCommand):
    help = (
        "Garante a existência do tenant inicial no domínio "
        "cargo.gnpsistemas.com.br e de um superuser no schema desse tenant."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            default="cargo.gnpsistemas.com.br",
            help="Domínio principal do tenant inicial.",
        )
        parser.add_argument(
            "--username",
            default="admin",
            help="Username do superuser inicial.",
        )
        parser.add_argument(
            "--email",
            default="admin@gnpsistemas.com.br",
            help="E-mail do superuser inicial.",
        )
        parser.add_argument(
            "--password",
            default="admin",
            help="Senha do superuser inicial.",
        )
        parser.add_argument(
            "--tenant-name",
            default="GNP Sistemas",
            help="Nome do tenant inicial.",
        )

    def handle(self, *args, **options):
        TenantModel = get_tenant_model()
        DomainModel = get_domain_model()
        User = get_user_model()

        domain_name = options["domain"].strip().lower()
        username = options["username"].strip()
        email = options["email"].strip().lower()
        password = options["password"]
        tenant_name = options["tenant_name"].strip()

        public_schema = get_public_schema_name()

        self.stdout.write(
            f"Verificando tenant inicial para domínio {domain_name}..."
        )

        # 1) Garante tenant público
        tenant = TenantModel.objects.filter(schema_name=public_schema).first()

        if tenant is None:
            tenant = self._create_public_tenant(
                TenantModel=TenantModel,
                schema_name=public_schema,
                tenant_name=tenant_name,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Tenant público criado com schema '{public_schema}'."
                )
            )
        else:
            changed = False

            # Se o model tiver campo "name" e estiver vazio, preenche
            if hasattr(tenant, "name") and not getattr(tenant, "name", None):
                tenant.name = tenant_name
                changed = True

            if changed:
                tenant.save()
                self.stdout.write(
                    self.style.SUCCESS("Tenant público atualizado.")
                )
            else:
                self.stdout.write("Tenant público já existe.")

        # 2) Garante domínio principal apontando para o tenant público
        domain_obj = DomainModel.objects.filter(domain=domain_name).first()

        if domain_obj is None:
            DomainModel.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Domínio '{domain_name}' criado e vinculado ao schema '{tenant.schema_name}'."
                )
            )
        else:
            changed = False

            if domain_obj.tenant_id != tenant.pk:
                domain_obj.tenant = tenant
                changed = True

            if not getattr(domain_obj, "is_primary", False):
                domain_obj.is_primary = True
                changed = True

            if changed:
                domain_obj.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Domínio '{domain_name}' atualizado."
                    )
                )
            else:
                self.stdout.write(f"Domínio '{domain_name}' já existe.")

        # 3) Garante superuser no schema do tenant público
        with schema_context(tenant.schema_name):
            user = None

            if user is None:
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Superuser '{username}' criado no schema '{tenant.schema_name}'."
                    )
                )
            else:
                changed = False

                if email and getattr(user, "email", "") != email:
                    user.email = email
                    changed = True

                if not user.is_staff:
                    user.is_staff = True
                    changed = True

                if not user.is_superuser:
                    user.is_superuser = True
                    changed = True

                if changed:
                    user.save(update_fields=["email", "is_staff", "is_superuser"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Superuser '{username}' ajustado no schema '{tenant.schema_name}'."
                        )
                    )
                else:
                    self.stdout.write(
                        f"Superuser '{username}' já existe no schema '{tenant.schema_name}'."
                    )

        self.stdout.write(self.style.SUCCESS("Ambiente inicial garantido com sucesso."))

    def _create_public_tenant(self, TenantModel, schema_name, tenant_name):
        """
        Cria o tenant público preenchendo apenas campos realmente necessários.
        Isso evita quebrar caso seu model tenha campos diferentes do exemplo da doc.
        """
        data = {"schema_name": schema_name}

        field_names = {field.name for field in TenantModel._meta.fields}

        # Campo comum em muitos exemplos/projetos
        if "name" in field_names:
            data["name"] = tenant_name

        # Campos comuns do exemplo oficial; só seta se existirem e aceitarem nulo/blank
        if "paid_until" in field_names:
            data["paid_until"] = None

        if "on_trial" in field_names:
            data["on_trial"] = False

        # save() é o fluxo recomendado para criar o tenant,
        # pois o django-tenants sincroniza o schema nesse processo.
        tenant = TenantModel(**data)
        tenant.save()
        return tenant