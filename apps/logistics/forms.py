# apps/logistics/forms.py
from django import forms
from apps.entities.models import Entity


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


class ConferenceCreateForm(forms.Form):
    CREATION_MODE_CHOICES = (
        ("cte", "Via CT-e"),
        ("manual", "Manual"),
    )

    DOCUMENT_TYPE_CHOICES = (
        ("invoice", "Nota Fiscal"),
    )

    creation_mode = forms.ChoiceField(
        choices=CREATION_MODE_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    cte_files = MultipleCTEFileField(required=False)

    document_type = forms.ChoiceField(
        choices=DOCUMENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    document_number = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    source_entity = forms.ModelChoiceField(
        queryset=Entity.objects.all(),
        widget=forms.Select(attrs={"class": "form-select select2"}),
    )

    destination_entity = forms.ModelChoiceField(
        queryset=Entity.objects.all(),
        widget=forms.Select(attrs={"class": "form-select select2"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔹 Exibição: "ID - Nome"
        self.fields["source_entity"].label_from_instance = (
            lambda obj: f"{obj.id} - {obj.name}"
        )
        self.fields["destination_entity"].label_from_instance = (
            lambda obj: f"{obj.id} - {obj.name}"
        )

    def clean(self):
        cleaned = super().clean()

        mode = cleaned.get("creation_mode")
        cte_files = cleaned.get("cte_files", [])
        doc_number = cleaned.get("document_number")
        doc_type = cleaned.get("document_type")

        if mode == "cte" and not cte_files:
            raise forms.ValidationError(
                "No modo CT-e é obrigatório anexar pelo menos um arquivo."
            )

        if mode == "manual" and doc_type == "invoice" and not doc_number:
            raise forms.ValidationError(
                "No modo manual com documento tipo Nota Fiscal é obrigatório informar a chave de acesso."
            )

        return cleaned
