from django.db import models
from fokontany.models import Fokontany


class Citoyen(models.Model):
    SEXE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]

    numero_citoyen = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Numéro du citoyen"
    )
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    prenoms = models.CharField(
        max_length=150,
        verbose_name="Prénoms"
    )
    date_naissance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance"
    )
    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        blank=True,
        verbose_name="Sexe"
    )
    adresse = models.TextField(
        blank=True,
        verbose_name="Adresse"
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )
    fokontany = models.ForeignKey(
        Fokontany,
        on_delete=models.PROTECT,
        related_name="citoyens",
        verbose_name="Fokontany"
    )
    date_enregistrement = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'enregistrement"
    )
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )

    class Meta:
        verbose_name = "Citoyen"
        verbose_name_plural = "Citoyens"
        ordering = ["nom", "prenoms"]

    def __str__(self):
        return f"{self.nom} {self.prenoms} ({self.numero_citoyen})"