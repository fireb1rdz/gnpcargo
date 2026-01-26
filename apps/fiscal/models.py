from django.db import models
from apps.core.models import TenantAwareModel
from django.core.validators import MinValueValidator

class Invoice(TenantAwareModel):
    client = models.IntegerField(help_text="ID do cliente no sistema")
    supplier = models.IntegerField(help_text="ID do fornecedor no sistema")
    carrier = models.IntegerField(help_text="ID do transportador no sistema")

    # Identificação fiscal
    access_key = models.CharField(max_length=44, unique=True)  # Id da infNFe
    uf_code = models.CharField(max_length=2)                  # cUF
    nf_number = models.CharField(max_length=20)               # nNF
    series = models.CharField(max_length=5)                   # serie
    model = models.CharField(max_length=2)                    # mod (55)
    issue_datetime = models.DateTimeField()                   # dhEmi
    exit_entry_datetime = models.DateTimeField(null=True)     # dhSaiEnt

    # Operação
    operation_nature = models.CharField(max_length=255)       # natOp
    operation_type = models.CharField(max_length=1)           # tpNF
    destination_indicator = models.CharField(max_length=1)    # idDest
    final_consumer = models.CharField(max_length=1)           # indFinal
    presence_indicator = models.CharField(max_length=1)       # indPres
    intermediary_indicator = models.CharField(max_length=1)   # indIntermed

    # Ambiente / status
    environment = models.CharField(max_length=1)              # tpAmb
    purpose = models.CharField(max_length=1)                  # finNFe
    status = models.CharField(max_length=30)                  # autorizado, cancelado, etc

    created_at = models.DateTimeField(auto_now_add=True)

class InvoiceParty(TenantAwareModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)  # EMIT, DEST, RETIRADA

    document = models.CharField(max_length=14)  # CNPJ/CPF
    name = models.CharField(max_length=255)
    state_registration = models.CharField(max_length=20, null=True)

    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20)
    complement = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255)
    city_code = models.CharField(max_length=7)
    city_name = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=8)
    country_code = models.CharField(max_length=4)
    country_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, null=True)

class InvoiceItem(TenantAwareModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item_number = models.IntegerField()             # nItem

    product_code = models.CharField(max_length=60)  # cProd
    ean = models.CharField(max_length=14, null=True)
    description = models.TextField()                # xProd
    ncm = models.CharField(max_length=8)
    cfop = models.CharField(max_length=4)

    unit = models.CharField(max_length=6)           # uCom
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    unit_price = models.DecimalField(max_digits=15, decimal_places=6)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)

    fci = models.CharField(max_length=36, null=True)  # nFCI
    additional_info = models.TextField(null=True)     # infAdProd

class InvoiceItemTax(TenantAwareModel):
    item = models.ForeignKey(InvoiceItem, on_delete=models.CASCADE)

    # ICMS
    icms_origin = models.CharField(max_length=1)
    icms_cst = models.CharField(max_length=3)
    icms_base = models.DecimalField(max_digits=15, decimal_places=2)
    icms_rate = models.DecimalField(max_digits=7, decimal_places=4)
    icms_value = models.DecimalField(max_digits=15, decimal_places=2)

    # IPI
    ipi_cst = models.CharField(max_length=3, null=True)
    ipi_base = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    ipi_rate = models.DecimalField(max_digits=7, decimal_places=4, null=True)
    ipi_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    # PIS
    pis_cst = models.CharField(max_length=3)
    pis_base = models.DecimalField(max_digits=15, decimal_places=2)
    pis_rate = models.DecimalField(max_digits=7, decimal_places=4)
    pis_value = models.DecimalField(max_digits=15, decimal_places=2)

    # COFINS
    cofins_cst = models.CharField(max_length=3)
    cofins_base = models.DecimalField(max_digits=15, decimal_places=2)
    cofins_rate = models.DecimalField(max_digits=7, decimal_places=4)
    cofins_value = models.DecimalField(max_digits=15, decimal_places=2)

    # IBS / CBS (novo sistema)
    ibs_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    cbs_value = models.DecimalField(max_digits=15, decimal_places=2, null=True)

class InvoiceTotals(TenantAwareModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    products_value = models.DecimalField(max_digits=15, decimal_places=2)
    icms_base = models.DecimalField(max_digits=15, decimal_places=2)
    icms_value = models.DecimalField(max_digits=15, decimal_places=2)

    pis_value = models.DecimalField(max_digits=15, decimal_places=2)
    cofins_value = models.DecimalField(max_digits=15, decimal_places=2)

    freight_value = models.DecimalField(max_digits=15, decimal_places=2)
    insurance_value = models.DecimalField(max_digits=15, decimal_places=2)
    discount_value = models.DecimalField(max_digits=15, decimal_places=2)
    other_value = models.DecimalField(max_digits=15, decimal_places=2)

    invoice_value = models.DecimalField(max_digits=15, decimal_places=2)

class InvoiceTransport(TenantAwareModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

    freight_mode = models.CharField(max_length=1)   # modFrete
    transporter_document = models.CharField(max_length=14)
    transporter_name = models.CharField(max_length=255)
    state_registration = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)

class InvoiceVolume(TenantAwareModel):
    transport = models.ForeignKey(InvoiceTransport, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    kind = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    number = models.CharField(max_length=20)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3)

class InvoiceXml(TenantAwareModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    xml = models.TextField()
    version = models.CharField(max_length=10)

#### CTE
class TransportDocument(TenantAwareModel):
    MODEL_CHOICES = (
        ("57", "CT-e"),
    )
    STATUS_CHOICES = (
        ("draft", "Rascunho"),
        ("authorized", "Autorizado"),
        ("cancelled", "Cancelado"),
        ("denied", "Denegado"),
    )
    internal_code = models.CharField(
        max_length=30,
        unique=True,
        help_text="Identificador interno do ERP"
    )
    fiscal_key = models.CharField(
        max_length=44,
        unique=True,
        null=True,
        blank=True,
        help_text="Chave de acesso do CT-e"
    )
    model = models.CharField(max_length=2, choices=MODEL_CHOICES, default="57")
    series = models.PositiveIntegerField()
    number = models.PositiveIntegerField()
    issue_datetime = models.DateTimeField()
    environment = models.CharField(
        max_length=10,
        choices=(("prod", "Produção"), ("test", "Homologação"))
    )
    cfop = models.CharField(max_length=4)
    nature_operation = models.CharField(max_length=255)
    modal = models.CharField(
        max_length=10,
        choices=(("road", "Rodoviário"),)
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="draft"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("model", "series", "number")
        verbose_name = "Documento de Transporte"
        verbose_name_plural = "Documentos de Transporte"
    def __str__(self):
        return f"CT-e {self.series}/{self.number}"

class TransportRoute(TenantAwareModel):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="route"
    )
    origin_city_code = models.CharField(max_length=7)
    origin_city_name = models.CharField(max_length=100)
    origin_state = models.CharField(max_length=2)
    destination_city_code = models.CharField(max_length=7)
    destination_city_name = models.CharField(max_length=100)
    destination_state = models.CharField(max_length=2)

class Issuer(TenantAwareModel):
    entity = models.IntegerField(null=True, blank=True)
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="issuer"
    )
    cnpj = models.CharField(max_length=14)
    state_registration = models.CharField(max_length=20)
    legal_name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255)

    tax_regime = models.CharField(
        max_length=20,
        choices=(
            ("simple", "Simples Nacional"),
            ("real", "Lucro Real"),
            ("presumed", "Lucro Presumido"),
        )
    )

class TransportParty(TenantAwareModel):
    PARTY_TYPE = (
        ("sender", "Remetente"),
        ("recipient", "Destinatário"),
    )
    document = models.ForeignKey(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="parties"
    )
    type = models.CharField(max_length=10, choices=PARTY_TYPE)
    cnpj = models.CharField(max_length=14)
    state_registration = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

class FreightValue(TenantAwareModel):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="freight_value"
    )
    total_service = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    total_receivable = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

class FreightComponent(TenantAwareModel):
    freight = models.ForeignKey(
        FreightValue,
        on_delete=models.CASCADE,
        related_name="components"
    )
    description = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

class ICMS(TenantAwareModel):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="icms"
    )
    cst = models.CharField(max_length=3)
    base_value = models.DecimalField(max_digits=15, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_value = models.DecimalField(max_digits=15, decimal_places=2)

class Cargo(models.Model):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="cargo"
    )
    declared_value = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    packaging = models.CharField(max_length=20)

class CargoMeasurement(models.Model):
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.CASCADE,
        related_name="measurements"
    )
    type = models.CharField(
        max_length=10,
        choices=(
            ("weight", "Peso"),
            ("volume", "Volume"),
        )
    )
    unit = models.CharField(max_length=5)
    value = models.DecimalField(max_digits=15, decimal_places=4)

class RelatedNFe(TenantAwareModel):
    document = models.ForeignKey(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="related_nfes"
    )
    access_key = models.CharField(max_length=44)
    expected_delivery_date = models.DateField(null=True, blank=True)

class RoadTransport(TenantAwareModel):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="road"
    )
    rntrc = models.CharField(max_length=15)

class TransportAuthorization(TenantAwareModel):
    document = models.OneToOneField(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="authorization"
    )
    protocol_number = models.CharField(max_length=20)
    authorization_datetime = models.DateTimeField()
    status_code = models.CharField(max_length=3)
    status_message = models.CharField(max_length=255)

class TransportObservation(TenantAwareModel):
    document = models.ForeignKey(
        TransportDocument,
        on_delete=models.CASCADE,
        related_name="observations"
    )
    title = models.CharField(max_length=100)
    text = models.TextField()
