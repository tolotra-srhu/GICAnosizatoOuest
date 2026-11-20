from django import forms

from fokontany.models import Fokontany
from .models import Citoyen


class CitoyenForm(forms.ModelForm):
    class Meta:
        model = Citoyen
        fields = [
            "numero_citoyen",
            "nom",
            "prenoms",
            "date_naissance",
            "sexe",
            "adresse",
            "telephone",
            "fokontany",
            "actif",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "adresse": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, fokontany=None, **kwargs):
        super().__init__(*args, **kwargs)

        if fokontany:
            self.fields["fokontany"].queryset = Fokontany.objects.filter(
                pk=fokontany.pk
            )
            self.fields["fokontany"].initial = fokontany
            self.fields["fokontany"].disabled = True
