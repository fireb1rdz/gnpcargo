from django.db import models
from apps.core.models import TenantAwareModel
from apps.entities.models import Party
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

class FinancialEntry(TenantAwareModel):
    direction = models.CharField(
        max_length=10,
        choices=[
            ("receivable", _("Receivable")),
            ("payable", _("Payable")),
        ]
    )

    counterparty = models.ForeignKey(
        Party,  # cliente ou fornecedor
        on_delete=models.PROTECT
    )

    description = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("open", _("Open")),
            ("paid", _("Paid")),
            ("cancelled", _("Cancelled")),
        ],
        default="open"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Financial Entry")
        verbose_name_plural = _("Financial Entries")
        constraints = [
            models.UniqueConstraint(
                fields=["counterparty", "reference_month", "reference_year", "direction"],
                name="unique_monthly_billing"
            )
        ]

class Installment(models.Model):
    financial_entry = models.ForeignKey(
        FinancialEntry,
        related_name="installments",
        on_delete=models.PROTECT
    )

    number = models.IntegerField()  # 1, 2, 3...
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ("open", _("Open")),
            ("paid", _("Paid")),
        ],
        default="open"
    )

class Payment(models.Model):
    installment = models.ForeignKey(
        Installment,
        related_name="payments",
        on_delete=models.PROTECT
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField()
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

