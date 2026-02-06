# apps/logistics/forms.py
from django import forms
from apps.entities.models import Party
from apps.logistics.models import Conference


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleCTEFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]

        return [single_file_clean(data, initial)]

class MultipleNFEFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"multiple": True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]

        return [single_file_clean(data, initial)]

class ConferenceCreateForm(forms.Form):
    CREATION_MODE_CHOICES = (
        # ("cte", "Via CT-e"),
        # ("nfe", "Via NF-e"),
        ("access_key", "Chave de Acesso"),
    )

    creation_mode = forms.ChoiceField(
        choices=CREATION_MODE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        initial="access_key"
    )

    cte_files = MultipleCTEFileField(required=False)

    nfe_files = MultipleNFEFileField(required=False)

    access_keys = forms.CharField(
        max_length=9999,
        required=False,
    )

    origin = forms.ModelChoiceField(
        queryset=Party.objects.filter(role="sender"),
        widget=forms.Select(attrs={"class": "form-select select2"}),
    )

    destination = forms.ModelChoiceField(
        queryset=Party.objects.filter(role="receiver"),
        widget=forms.Select(attrs={"class": "form-select select2"}),
    )

    event_type = forms.ChoiceField(
        choices=Conference.EVENT_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select select2"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["origin"].label_from_instance = (
            lambda obj: f"{obj.entity.id} - {obj.entity.name}"
        )
        self.fields["destination"].label_from_instance = (
            lambda obj: f"{obj.entity.id} - {obj.entity.name}"
        )

    def clean(self):
        cleaned = super().clean()

        mode = cleaned.get("creation_mode")
        cte_files = cleaned.get("cte_files", [])
        nfe_files = cleaned.get("nfe_files", [])
        access_keys = cleaned.get("access_keys", [])

        if mode == "cte" and not cte_files:
            raise forms.ValidationError(
                "No modo CT-e é obrigatório anexar pelo menos um arquivo."
            )

        if mode == "nfe" and not nfe_files:
            raise forms.ValidationError(
                "No modo NF-e é obrigatório anexar pelo menos um arquivo."
            )

        if mode == "access_key" and not access_keys:
            raise forms.ValidationError(
                "No modo Chave de Acesso é obrigatório informar pelo menos uma chave de acesso."
            )

        return cleaned

    def clean_access_keys(self):
        raw_keys = self.cleaned_data.get("access_keys", "")

        if not raw_keys:
            return []

        # Normalização da string
        keys = raw_keys.replace('"', '')
        keys = keys.replace('[', '')
        keys = keys.replace(']', '')

        # Quebra por vírgula
        keys = [k.strip() for k in keys.split(',') if k.strip()]

        # Validação opcional de tamanho/formato
        for key in keys:
            if len(key) != 44:
                raise forms.ValidationError(
                    f"Chave de acesso inválida: {key}"
                )

        return keys

