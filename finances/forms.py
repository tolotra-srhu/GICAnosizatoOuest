from django import forms

from citoyens.models import Citoyen
from fokontany.models import Fokontany
from .models import FondsAssociation, PaiementAdidy


class PaiementAdidyForm(forms.ModelForm):
    class Meta:
        model = PaiementAdidy
        fields = [
            "fokontany",
            "citoyen",
            "contribuable",
            "numero_carnet",
            "mois",
            "annee",
            "montant",
            "mode_paiement",
            "date_paiement",
            "observations",
        ]
        widgets = {
            "date_paiement": forms.DateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
            "montant": forms.NumberInput(attrs={"min": 0, "step": "100"}),
            "annee": forms.NumberInput(attrs={"min": 2000, "max": 2100}),
        }

    def __init__(self, *args, fokontany=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fokontany"].required = True
        self.fields["citoyen"].required = False

        if fokontany:
            self.fields["fokontany"].queryset = Fokontany.objects.filter(pk=fokontany.pk)
            self.fields["fokontany"].initial = fokontany
            self.fields["fokontany"].disabled = True
            self.fields["citoyen"].queryset = Citoyen.objects.filter(
                fokontany=fokontany,
                actif=True,
            )
        else:
            self.fields["citoyen"].queryset = Citoyen.objects.filter(actif=True)


class FondsAssociationForm(forms.ModelForm):
    class Meta:
        model = FondsAssociation
        fields = [
            "libelle",
            "type_mouvement",
            "montant",
            "fokontany",
            "date_mouvement",
            "observations",
        ]
        widgets = {
            "date_mouvement": forms.DateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
            "montant": forms.NumberInput(attrs={"min": 0, "step": "100"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fokontany"].required = False
