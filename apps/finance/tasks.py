from celery import shared_task
from django_tenants.utils import schema_context
from apps.finance.services.billing_service import FinanceService
from apps.core.models import Tenant
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_billing_for_tenant(self, schema_name, reference_month, reference_year, username):
    logger.info(
        "Iniciando geração de cobrança",
        extra={
            "schema": schema_name,
            "reference_month": reference_month,
            "reference_year": reference_year,
        },
    )
    try:
        with schema_context(schema_name):
            tenant = Tenant.objects.get(schema_name=schema_name)
            user = User.objects.get(username=username)
            finance_service = FinanceService()
            billing = finance_service.generate_monthly_billing(tenant, reference_month, reference_year, user)
            logger.info(
                "Cobrança gerada com sucesso",
                extra={
                    "schema": schema_name,
                    "billing_id": billing.id,
                    "amount": str(billing.amount),
                },
            )
    except Exception as exc:
        logger.exception(
            "Erro ao gerar cobrança",
            extra={
                "schema": schema_name,
                "reference_month": reference_month,
                "reference_year": reference_year,
            },
        )

        # retry automático
        raise self.retry(exc=exc)