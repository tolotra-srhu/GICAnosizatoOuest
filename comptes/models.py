
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class ProfilUtilisateur(models.Model):

    ROLE_ADMINISTRATEUR = "ADMINISTRATEUR"
    ROLE_MAIRE = "MAIRE"
    ROLE_ADJOINT_1 = "ADJOINT_1"
    ROLE_ADJOINT_2 = "ADJOINT_2"
    ROLE_CHEF = "CHEF_FOKONTANY"
    ROLE_TRESORIER = "TRESORIER"
    ROLE_SECRETAIRE = "SECRETAIRE"

    CHOIX_ROLES = [
        (ROLE_ADMINISTRATEUR, "Administrateur"),
        (ROLE_MAIRE, "Maire"),
        (ROLE_ADJOINT_1, "Premier Adjoint"),
        (ROLE_ADJOINT_2, "Deuxième Adjoint"),
        (ROLE_CHEF, "Chef Fokontany"),
        (ROLE_TRESORIER, "Trésorier"),
        (ROLE_SECRETAIRE, "Secrétaire"),
    ]

    ROLES_ADMINISTRATION = [
        ROLE_MAIRE,
        ROLE_ADJOINT_1,
        ROLE_ADJOINT_2,
    ]

    ROLES_SUPERVISION = (
        [ROLE_ADMINISTRATEUR] + ROLES_ADMINISTRATION
    )

    ROLES_GESTION_COMPTES = [ROLE_ADMINISTRATEUR]
    ROLES_TRESORERIE = [ROLE_TRESORIER]
    ROLES_SECRETARIAT = [ROLE_SECRETAIRE]

    ROLES_GLOBAUX = (
        ROLES_SUPERVISION
        + ROLES_TRESORERIE
        + ROLES_SECRETARIAT
    )

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profil_gic",
    )

    role = models.CharField(
        max_length=20,
        choices=CHOIX_ROLES,
    )

    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="profils_utilisateurs",
    )

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def clean(self):
        super().clean()

        if self.role == self.ROLE_CHEF:

            if not self.fokontany_id:
                raise ValidationError({
                    "fokontany": (
                        "Un chef doit être affecté à un fokontany."
                    )
                })

            chef_existant = ProfilUtilisateur.objects.filter(
                role=self.ROLE_CHEF,
                fokontany_id=self.fokontany_id,
            ).exclude(pk=self.pk)

            if chef_existant.exists():
                raise ValidationError({
                    "fokontany": (
                        "Ce fokontany possède déjà un chef."
                    )
                })

        if (
            self.role in self.ROLES_GLOBAUX
            and self.fokontany_id
        ):
            raise ValidationError({
                "fokontany": (
                    "Ce rôle intervient sur l'ensemble de la commune."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.utilisateur.username} - "
            f"{self.get_role_display()}"
        )


class ParametrePlateforme(models.Model):
    cle = models.CharField(max_length=50, unique=True)
    libelle = models.CharField(max_length=100)
    valeur = models.TextField(blank=True)

    class Meta:
        verbose_name = "Paramètre de la plateforme"
        verbose_name_plural = "Paramètres de la plateforme"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle
