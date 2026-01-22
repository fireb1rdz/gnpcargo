from django.forms import ModelForm
from django import forms
from apps.entities.models import Entity

class EntityForm(ModelForm):
    class Meta:
        model = Entity
        fields = [
            "name", "cpf", "cnpj", "cpforcnpj",
            "is_active", "is_client",
            "is_shipping_company", "is_branch",
            "is_system", "is_main"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cpf": forms.TextInput(attrs={"class": "form-control"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control"}),
            "cpforcnpj": forms.Select(attrs={"class": "form-select"}),

            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_client": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_shipping_company": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_branch": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_system": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_main": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
