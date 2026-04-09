#!/bin/sh
set -e

echo "Aguardando banco..."

until python manage.py shell -c "from django.db import connections; connections['default'].cursor()" 2>/dev/null; do
  sleep 2
done

echo "Banco OK"

# 1) Migra shared apps no public
python manage.py migrate_schemas --shared --noinput

# 2) Garante tenant e domínio
python manage.py setup_tenants

# 3) Agora que o tenant existe, migra tenant apps
python manage.py migrate_schemas --tenant --noinput

# 4) Cria/ajusta superuser no schema public
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, tenant_context

User = get_user_model()
Tenant = get_tenant_model()

tenant = Tenant.objects.get(schema_name="gnp")

with tenant_context(tenant):
    user = User.objects.filter(username="admin").first()
    if not user:
        User.objects.create_superuser(
            username="admin",
            email="admin@gnpsistemas.com.br",
            password="admin",
            tenant=tenant
        )
        print("Superuser criado")
    else:
        changed = False
        if user.email != "admin@gnpsistemas.com.br":
            user.email = "admin@gnpsistemas.com.br"
            changed = True
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        user.set_password("admin")
        changed = True

        if changed:
            user.save()
            print("Superuser atualizado")
        else:
            print("Superuser já existe")
EOF

# 5) Static
python manage.py collectstatic --noinput

exec "$@"