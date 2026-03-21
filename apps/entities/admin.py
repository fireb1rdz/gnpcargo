from .models import Party, Entity, EntityAddress, EntityPhone
from django.contrib import admin

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("id", "entity", "role")
    list_filter = ("role",)
    search_fields = ("entity__name", "id")
    ordering = ("entity__name",)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cpforcnpj")
    list_filter = ("cpforcnpj",)
    search_fields = ("name", "id", "cpf", "cnpj")
    ordering = ("name",)

@admin.register(EntityAddress)
class EntityAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "entity", "street", "number", "complement", "city", "state", "zip_code")
    list_filter = ("city", "state", "country")
    search_fields = ("entity__name", "street", "number", "complement", "city", "state", "zip_code")
    ordering = ("entity__name",)

@admin.register(EntityPhone)
class EntityPhoneAdmin(admin.ModelAdmin):
    list_display = ("id", "entity", "phone")
    list_filter = ("phone",)
    search_fields = ("entity__name", "phone")
    ordering = ("entity__name",)
