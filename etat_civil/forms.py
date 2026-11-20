from django import forms

from citoyens.models import Citoyen
from fokontany.models import Fokontany
from .models import ActeEtatCivil, ActeNaissance, DocumentAdministratif


class ActeEtatCivilForm(forms.ModelForm):
    class Meta:
        model = ActeEtatCivil
        fields = [
            "numero_acte",
            "type_acte",
            "fokontany",
            "date_acte",
            "lieu_acte",
            "observations",
        ]
        widgets = {
            "date_acte": forms.DateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
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


class ActeNaissanceForm(forms.ModelForm):
    class Meta:
        model = ActeNaissance
        fields = [
            "numero_acte",
            "fokontany",
            "nom_enfant",
            "prenoms_enfant",
            "sexe",
            "date_naissance",
            "heure_naissance",
            "lieu_naissance",
            "nom_pere",
            "nom_mere",
            "declarant",
            "date_declaration",
            "observations",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "date_declaration": forms.DateInput(attrs={"type": "date"}),
            "heure_naissance": forms.TimeInput(attrs={"type": "time"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, fokontany=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fokontany"].required = True
        if fokontany:
            self.fields["fokontany"].queryset = Fokontany.objects.filter(pk=fokontany.pk)
            self.fields["fokontany"].initial = fokontany
            self.fields["fokontany"].disabled = True


class DocumentAdministratifForm(forms.ModelForm):
    class Meta:
        model = DocumentAdministratif
        fields = [
            "numero",
            "type_document",
            "fokontany",
            "citoyen",
            "nom_beneficiaire",
            "nom_pere",
            "nom_mere",
            "date_naissance",
            "lieu_naissance",
            "usage",
            "date_delivrance",
            "observations",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
            "date_delivrance": forms.DateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, fokontany=None, type_document=None, **kwargs):
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

        if type_document:
            self.fields["type_document"].initial = type_document
            self.fields["type_document"].disabled = True
