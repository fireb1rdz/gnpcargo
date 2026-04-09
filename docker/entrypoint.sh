#!/bin/sh

set -e

sleep 2

# 1. shared
python manage.py migrate_schemas --shared --noinput

# 2. cria tenant (SEM user)
python manage.py setup_tenants

# 3. cria tabelas do tenant
python manage.py migrate_schemas --tenant --noinput

# 4. cria superuser (AGORA SIM EXISTE TABELA)
python manage.py create_tenant_superuser \
  --schema=public \
  --username=admin \
  --email=admin@gnpsistemas.com.br \
  --noinput || true

# define senha (porque --noinput não seta direito)
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.filter(username="admin").first()
if u:
    u.set_password("admin")
    u.is_staff = True
    u.is_superuser = True
    u.save()
EOF

# static
python manage.py collectstatic --noinput

exec "$@"