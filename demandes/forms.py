from django import forms

from citoyens.models import Citoyen
from .models import Demande


class DemandeForm(forms.ModelForm):
    class Meta:
        model = Demande
        fields = [
            "type_demande",
            "fokontany",
            "objet",
            "description",
            "priorite",
            "citoyen",
            "document_souhaite",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "document_souhaite": forms.TextInput(attrs={
                "placeholder": "Ex. certificat de résidence",
            }),
        }

    def __init__(self, *args, fokontany=None, **kwargs):
        super().__init__(*args, **kwargs)

        if fokontany:
            self.fields.pop("fokontany", None)
            self.fields["citoyen"].queryset = Citoyen.objects.filter(
                fokontany=fokontany,
                actif=True,
            )
        else:
            from fokontany.models import Fokontany

            self.fields["fokontany"].queryset = Fokontany.objects.filter(
                actif=True
            )
            self.fields["citoyen"].queryset = Citoyen.objects.filter(actif=True)
        self.fields["citoyen"].required = False


class TraitementDemandeForm(forms.Form):
    DECISION_ACCEPTER = "ACCEPTEE"
    DECISION_REFUSER = "REFUSEE"
    DECISION_ATTENTE = "MISE_EN_ATTENTE"

    decision = forms.ChoiceField(
        choices=[
            (DECISION_ACCEPTER, "Accepter la demande"),
            (DECISION_REFUSER, "Refuser la demande"),
            (DECISION_ATTENTE, "Mettre en attente"),
        ],
        widget=forms.RadioSelect,
        label="Décision",
    )
    reponse = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        label="Réponse / motif",
    )

    def clean(self):
        donnees = super().clean()
        decision = donnees.get("decision")
        reponse = (donnees.get("reponse") or "").strip()

        if decision in (
            self.DECISION_REFUSER,
            self.DECISION_ATTENTE,
        ) and not reponse:
            raise forms.ValidationError(
                "Indiquez le motif du refus ou de la mise en attente."
            )

        return donnees
