from django.db import models
from apps.core.models import TenantAwareModel
from django.utils.text import slugify

class Entity(TenantAwareModel):
    choices = {
        'CPF': 'CPF',
        'CNPJ': 'CNPJ',
    }
    name = models.CharField(max_length=100)
    fantasy_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True)
    cpforcnpj = models.CharField(max_length=4, choices=choices.items(), default='CPF')
    is_active = models.BooleanField(default=True)
    is_client = models.BooleanField(default=False)
    is_shipping_company = models.BooleanField(default=False)
    is_branch = models.BooleanField(default=False)
    is_main = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False, help_text='Allow access to the entity as system company')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.cpf:
            self.cpfoucnpj = self.choices['CPF']
        else:
            self.cpfoucnpj = self.choices['CNPJ']
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'
        ordering = ['name']

class EntityAddress(TenantAwareModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='entity_addresses')
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10, blank=True, null=True)
    complement = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=8)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.entity.name} - {self.city} - {self.state}"

class EntityPhone(TenantAwareModel):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='entity_phones')
    phone = models.CharField(max_length=20)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.entity.name} - {self.phone}"