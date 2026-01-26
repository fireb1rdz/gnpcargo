from django.db import models
from apps.core.models import TenantAwareModel
from django.contrib.auth import get_user_model
from apps.stock.models import Package
from apps.entities.models import Entity


User = get_user_model()

class Conference(TenantAwareModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    )
    DOCUMENT_TYPE_CHOICES = (
        ('invoice', 'Invoice'),
    )
    source_entity = models.ForeignKey(Entity, on_delete=models.PROTECT, related_name="source_conferences")
    shipping_entity = models.ForeignKey(Entity, on_delete=models.PROTECT, related_name="shipping_conferences")
    destination_entity = models.ForeignKey(Entity, on_delete=models.PROTECT, related_name="destination_conferences")
    document_number = models.CharField(max_length=44, null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='invoice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    has_problem = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    finished_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="finished_conferences", null=True, blank=True)

class ConferenceItem(TenantAwareModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('ok', 'Ok'),
        ('faulty', 'Faulty'),
    )
    conference = models.ForeignKey(Conference, on_delete=models.PROTECT, related_name="items")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="conference_items")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="read_conference_items", null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)



