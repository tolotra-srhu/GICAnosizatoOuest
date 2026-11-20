from django import forms

from fokontany.models import Fokontany
from .models import Personnel


class PersonnelForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = [
            "matricule",
            "nom",
            "prenoms",
            "sexe",
            "fonction",
            "service",
            "fokontany",
            "telephone",
            "email",
            "date_embauche",
            "statut",
        ]
        widgets = {
            "date_embauche": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, fokontany=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fokontany"].required = True

        if fokontany:
            self.fields["fokontany"].queryset = Fokontany.objects.filter(
                pk=fokontany.pk
            )
            self.fields["fokontany"].initial = fokontany
            self.fields["fokontany"].disabled = True
