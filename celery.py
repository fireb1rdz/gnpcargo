import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GNP-ERP.settings.dev")

app = Celery("GNP-ERP")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()