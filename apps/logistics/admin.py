from .models import Conference, ConferenceItem
from django.contrib import admin

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'mode', 'event_type', 'document_number', 'document_type', 'status', 'created_at', 'updated_at')
    list_filter = ('event_type', 'document_number', 'document_type', 'status', 'created_at', 'updated_at')
    search_fields = ('document_number', 'document_type', 'status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

@admin.register(ConferenceItem)
class ConferenceItemAdmin(admin.ModelAdmin):
    list_display = ('conference', 'package', 'status', 'created_at', 'updated_at')
    list_filter = ('conference', 'package', 'status', 'created_at', 'updated_at')
    search_fields = ('conference', 'package', 'status', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25