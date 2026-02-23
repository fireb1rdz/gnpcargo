from celery import shared_task
from django_tenants.utils import schema_context
from tenants.models import Client
from finance.services import generate_monthly_billing


@shared_task
def generate_billing_for_tenant(schema_name):
    with schema_context(schema_name):
        generate_monthly_billing()