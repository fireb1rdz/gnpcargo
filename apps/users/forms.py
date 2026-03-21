from django.forms import ModelForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from .models import User
from apps.entities.models import Entity

class CustomAuthenticationForm(AuthenticationForm):
    entity = forms.ModelChoiceField(
        queryset=Entity.objects.filter(is_system=True),
        widget=forms.Select(attrs={"class": "form-select select2"}),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Usuário"
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Senha"
        })
        self.fields["entity"].widget.attrs.update({
            "class": "form-select select2",
            "placeholder": "Empresa"
        })


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "email",
            "first_name", "last_name",
            "is_active", "is_staff", "is_superuser"
        ]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),

            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_staff": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
