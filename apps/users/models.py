from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import TenantAwareModel
from apps.entities.models import Entity

class User(AbstractUser, TenantAwareModel):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT, null=True, blank=True)
    pass
