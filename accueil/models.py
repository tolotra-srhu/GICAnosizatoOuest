from django.conf import settings
from django.db import models
from django.utils import timezone


class Actualite(models.Model):
    CATEGORIE_REUNION = "REUNION"
    CATEGORIE_FETE = "FETE"
    CATEGORIE_TRAVAUX = "TRAVAUX"
    CATEGORIE_INFORMATION = "INFORMATION"

    CHOIX_CATEGORIES = [
        (CATEGORIE_REUNION, "Réunion"),
        (CATEGORIE_FETE, "Fête"),
        (CATEGORIE_TRAVAUX, "Travaux"),
        (CATEGORIE_INFORMATION, "Information"),
    ]

    titre = models.CharField(max_length=200, verbose_name="Titre")
    contenu = models.TextField(verbose_name="Contenu")
    categorie = models.CharField(
        max_length=20,
        choices=CHOIX_CATEGORIES,
        default=CATEGORIE_INFORMATION,
        verbose_name="Catégorie",
    )
    image = models.ImageField(
        upload_to="actualites/",
        null=True,
        blank=True,
        verbose_name="Image",
    )
    publiee = models.BooleanField(default=True, verbose_name="Publiée")
    date_publication = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de publication",
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actualites",
        verbose_name="Auteur",
    )

    class Meta:
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre
