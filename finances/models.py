import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class PaiementAdidy(models.Model):
    MOIS_CHOICES = [
        (1, "Janvier"),
        (2, "Février"),
        (3, "Mars"),
        (4, "Avril"),
        (5, "Mai"),
        (6, "Juin"),
        (7, "Juillet"),
        (8, "Août"),
        (9, "Septembre"),
        (10, "Octobre"),
        (11, "Novembre"),
        (12, "Décembre"),
    ]

    MODE_ESPECES = "ESPECES"
    MODE_MOBILE = "MOBILE"
    MODE_VIREMENT = "VIREMENT"

    CHOIX_MODES = [
        (MODE_ESPECES, "Espèces"),
        (MODE_MOBILE, "Mobile money"),
        (MODE_VIREMENT, "Virement"),
    ]

    reference = models.CharField(
        max_length=24,
        unique=True,
        blank=True,
        verbose_name="Référence",
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        related_name="paiements_adidy",
        verbose_name="Fokontany",
    )
    citoyen = models.ForeignKey(
        "citoyens.Citoyen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paiements_adidy",
        verbose_name="Citoyen",
    )
    contribuable = models.CharField(
        max_length=150,
        verbose_name="Nom du contribuable",
    )
    numero_carnet = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numéro du carnet de fokontany",
        help_text="Référence inscrite dans le carnet de fokontany.",
    )
    mois = models.PositiveSmallIntegerField(
        choices=MOIS_CHOICES,
        verbose_name="Mois",
    )
    annee = models.PositiveIntegerField(
        default=timezone.now().year,
        verbose_name="Année",
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (Ar)",
    )
    mode_paiement = models.CharField(
        max_length=20,
        choices=CHOIX_MODES,
        default=MODE_ESPECES,
        verbose_name="Mode de paiement",
    )
    date_paiement = models.DateField(
        default=timezone.localdate,
        verbose_name="Date de paiement",
    )
    recu_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adidy_enregistres",
        verbose_name="Reçu par",
    )
    observations = models.TextField(blank=True, verbose_name="Observations")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement adidy"
        verbose_name_plural = "Paiements adidy"
        ordering = ["-date_paiement", "-date_creation"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ADY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def periode(self):
        return f"{self.get_mois_display()} {self.annee}"

    def __str__(self):
        return f"{self.reference} - {self.contribuable} ({self.periode})"


class FondsAssociation(models.Model):
    TYPE_ENTREE = "ENTREE"
    TYPE_SORTIE = "SORTIE"

    CHOIX_TYPES = [
        (TYPE_ENTREE, "Entrée"),
        (TYPE_SORTIE, "Sortie"),
    ]

    libelle = models.CharField(max_length=200, verbose_name="Libellé")
    type_mouvement = models.CharField(
        max_length=10,
        choices=CHOIX_TYPES,
        verbose_name="Type de mouvement",
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (Ar)",
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements_association",
        verbose_name="Fokontany",
    )
    date_mouvement = models.DateField(
        default=timezone.localdate,
        verbose_name="Date du mouvement",
    )
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mouvements_association",
        verbose_name="Enregistré par",
    )
    observations = models.TextField(blank=True, verbose_name="Observations")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de l'association"
        verbose_name_plural = "Mouvements de l'association"
        ordering = ["-date_mouvement", "-date_creation"]

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.libelle} ({self.montant} Ar)"
