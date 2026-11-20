from django import forms
from .models import Fokontany


class FokontanyForm(forms.ModelForm):
    class Meta:
        model = Fokontany
        fields = [
            "code",
            "nom",
            "responsable",
            "adresse",
            "specificites",
            "telephone",
            "actif",
            "latitude",
            "longitude",
        ]
        widgets = {
            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Code du fokontany",
            }),
            "nom": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom du fokontany",
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom du responsable",
            }),
            "adresse": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Adresse ou localisation",
            }),
            "specificites": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Spécificités, activités et sites remarquables",
            }),
            "telephone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Téléphone",
            }),
            "actif": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }