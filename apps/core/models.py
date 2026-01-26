import uuid
from django.db import models, connection
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_tenants.models import TenantMixin, DomainMixin

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Tenant(TenantMixin, TimeStampedModel):
    """
    Each customer is an Tenant.
    Modules can be enabled/disabled per Tenant (feature flags).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    

    def __str__(self):
        return self.name

    def has_module(self, module_name):
        return self.tenant_modules.filter(module__name=module_name).exists()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Domain(DomainMixin):
    pass

class TenantAwareModel(TimeStampedModel):
    """
    Mixin for models that belong to a specific tenant.
    """
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name="%(class)s_tenant"
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            tenant = getattr(connection, "tenant", None)

            if tenant is None:
                raise RuntimeError(
                    "Nenhum tenant ativo no contexto da conexão"
                )

            self.tenant = tenant

        super().save(*args, **kwargs)
        
class Module(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TenantModule(TimeStampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="tenant_modules")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="tenant_modules")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.module}"

