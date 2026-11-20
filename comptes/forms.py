from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import ProfilUtilisateur


class ConnexionForm(AuthenticationForm):
    role = forms.ChoiceField(
        label="Je me connecte en tant que",
        choices=ProfilUtilisateur.CHOIX_ROLES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Nom d'utilisateur",
            "autocomplete": "username",
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Mot de passe",
            "autocomplete": "current-password",
        })

    def clean(self):
        donnees = super().clean()
        role = donnees.get("role")

        if role and getattr(self, "user_cache", None):
            utilisateur = self.user_cache

            if utilisateur.is_superuser:
                if role != ProfilUtilisateur.ROLE_ADMINISTRATEUR:
                    raise ValidationError(
                        "Le compte superutilisateur doit sélectionner le rôle "
                        "« Administrateur ».",
                        code="role_invalide",
                    )
                return donnees

            profil = getattr(utilisateur, "profil_gic", None)

            if not profil:
                raise ValidationError(
                    "Ce compte n'a aucun rôle configuré. Contactez "
                    "l'administration de la commune.",
                    code="profil_absent",
                )

            if profil.role != role:
                raise ValidationError(
                    "Le rôle sélectionné ne correspond pas à votre compte.",
                    code="role_invalide",
                )

        return donnees
