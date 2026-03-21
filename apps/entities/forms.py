from django.forms import ModelForm
from django import forms
from apps.entities.models import Entity
from domain.bootstrap.service_container import get_party_service

class EntityForm(ModelForm):

    def clean(self):
        cleaned_data = super().clean()
        party_service = get_party_service()
        existing_roles = party_service.get_existing_roles()
        selected_roles = []

        for role, translation in existing_roles:
            if cleaned_data.get(role):
                selected_roles.append(role)

        if not selected_roles:
            raise forms.ValidationError("A entidade deve ter pelo menos um papel.")

        for role in selected_roles:
            if not party_service.can_be(entity=self.instance, role=role):
                raise forms.ValidationError(f"A entidade não pode ser um {role}.")

        self.selected_roles = selected_roles
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["economic_group"].label_from_instance = (
            lambda obj: f"{obj.id} - {obj.name}"
        )

        party_service = get_party_service()
        existing_roles = party_service.get_existing_roles()
        if self.instance.pk:
            current_roles = self.instance.parties.all()
        else:
            current_roles = []
        for role, translation in existing_roles:
            self.fields[role] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"}))
        for party in current_roles:
            self.fields[party.role].initial = True



    class Meta:
        model = Entity
        fields = [
            "name", "cpf", "cnpj", "cpforcnpj",
            "is_active", "is_branch",
            "is_system", "economic_group"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cpf": forms.TextInput(attrs={"class": "form-control"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control"}),
            "cpforcnpj": forms.Select(attrs={"class": "form-select"}),

            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_branch": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_system": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "economic_group": forms.Select(attrs={"class": "form-select select2"}),
        }
        