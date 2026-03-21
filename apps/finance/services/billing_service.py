

from decimal import Decimal
from datetime import date
from django.db import transaction
from django.utils import timezone
import calendar
from apps.finance.models import FinancialEntry, Installment

class FinanceService:

    @transaction.atomic
    def generate_monthly_billing(self, tenant, reference_month, reference_year, user):

        packages_read = self.conference_service.get_packages_read_in_month(
            tenant,
            reference_month,
            reference_year
        )

        if packages_read <= 0:
            raise ValueError("Não há volumes no período.")

        total_value = Decimal(packages_read) * Decimal(tenant.value_per_read_package)

        today = timezone.now().date()

        # 🔥 Vencimento no mês atual (mês de geração)
        due_year = today.year
        due_month = today.month

        last_day = calendar.monthrange(due_year, due_month)[1]
        due_day = min(tenant.default_due_day, last_day)

        due_date = date(due_year, due_month, due_day)

        financial_entry = FinancialEntry.objects.create(
            direction="receivable",
            counterparty=tenant.party,
            description=f"Cobrança referente a {reference_month:02d}/{reference_year}",
            amount=total_value,
            due_date=due_date,
            created_by=user,
        )

        Installment.objects.create(
            financial_entry=financial_entry,
            number=1,
            due_date=due_date,
            amount=total_value,
        )

        return financial_entry