from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, get_domain_model
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Cria o tenant público e um tenant demo caso não existam'

    def handle(self, *args, **options):
        TenantModel = get_tenant_model()
        DomainModel = get_domain_model()
        User = get_user_model()

        # 1. Criar o Tenant PÚBLICO (Obrigatório para django-tenants)
        if not TenantModel.objects.filter(schema_name='public').exists():
            self.stdout.write("Criando tenant público...")
            public_tenant = TenantModel(
                schema_name='public',
                name='Sistema GNP Cargo - Principal'
            )
            public_tenant.save()

            # Adiciona o domínio para o público
            DomainModel.objects.create(
                domain='cargo.gnpsistemas.com.br', # Ou seu domínio principal
                tenant=public_tenant,
                is_primary=True
            )
        else:
            self.stdout.write(self.style.SUCCESS("Tenant público já existe."))

        # 2. Criar o Tenant DEMO
        if not TenantModel.objects.filter(schema_name='demo').exists():
            self.stdout.write("Criando tenant demo...")
            demo_tenant = TenantModel(
                schema_name='demo',
                name='Empresa Demonstração'
            )
            demo_tenant.save()

            DomainModel.objects.create(
                domain='cargo.gnpsistemas.com.br', # Ou demo.gnpsistemas.com.br
                tenant=demo_tenant,
                is_primary=True
            )

            # 3. Criar Usuário Admin dentro do Tenant Demo
            # O django-tenants exige que você mude o contexto para o schema alvo
            from django.db import connection
            connection.set_tenant(demo_tenant)

            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@demo.com',
                    password='admin' # Mude isso em produção!
                )
                self.stdout.write(self.style.SUCCESS("Usuário admin:admin criado no schema demo."))
            
            # Volta para o public (opcional)
            connection.set_schema_to_public()
        else:
            self.stdout.write(self.style.SUCCESS("Tenant demo já existe."))