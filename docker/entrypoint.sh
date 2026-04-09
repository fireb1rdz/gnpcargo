#!/bin/sh

echo "Aguardando banco de dados..."
sleep 1

python manage.py migrate_schemas --shared --noinput
python manage.py migrate_schemas --tenant --noinput 
python manage.py setup_tenants
python manage.py collectstatic --noinput

exec "$@"
