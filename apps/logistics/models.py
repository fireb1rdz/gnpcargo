from django.db import models
from apps.core.models import TenantAwareModel
from django.contrib.auth import get_user_model
from apps.stock.models import Package
from apps.entities.models import Party
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()

class Conference(TenantAwareModel):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('finished', _('Finished')),
        ('cancelled', _('Cancelled')),
    )
    DOCUMENT_TYPE_CHOICES = (
        ('invoice', _('Invoice')),
    )
    EVENT_TYPE_CHOICES = (
        ("load", _("Load in the vehicle")),
        ("unload", _("Unload from the vehicle")),
    )
    MODE_CHOICES = (
        ('read', _('Read')),
        ('write', _('Write')),
    )
    origin = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name="origin_conferences"
    )
    destination = models.ForeignKey(
        Party,
        on_delete=models.PROTECT,
        related_name="destination_conferences"
    )
    parent_conference = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derived_conferences"
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    document_number = models.CharField(max_length=44, null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='invoice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    has_problem = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    started_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="started_conferences", null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    finished_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="finished_conferences", null=True, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='read')

class ConferenceItem(TenantAwareModel):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('ok', _('Ok')),
        ('faulty', _('Faulty')),
    )
    conference = models.ForeignKey(Conference, on_delete=models.PROTECT, related_name="items")
    package = models.ForeignKey(Package, on_delete=models.PROTECT, related_name="conference_packages")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="read_conference_items", null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.conference} - {self.package}"

class ConferenceSession(TenantAwareModel):
    conference = models.ForeignKey(Conference, on_delete=models.PROTECT, related_name="sessions")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="conference_sessions")
    start_date = models.DateTimeField(auto_now_add=True)
    last_start = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    total_seconds = models.IntegerField(default=0)
    paused = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    
    def total_time_actual(self):
        if not self.paused and not self.finished and self.last_start:
            delta = timezone.now() - self.last_start
            return self.total_seconds + int(delta.total_seconds())
        return self.total_seconds

    def __str__(self):
        return f"{self.conference} - {self.user}"

    class Meta:
        unique_together = ('conference', 'user')
        verbose_name = _("Conference Session")
        verbose_name_plural = _("Conference Sessions")