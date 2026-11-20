import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Demande(models.Model):
    TYPE_ROUTE = "ROUTE"
    TYPE_ECOLE = "ECOLE"
    TYPE_COMMUNE = "COMMUNE"
    TYPE_CSBII = "CSBII"
    TYPE_WC_PUBLIC = "WC_PUBLIC"
    TYPE_POMPE = "POMPE"
    TYPE_CERTIFICAT_RESIDENCE = "CERTIFICAT_RESIDENCE"
    TYPE_RECENSEMENT = "RECENSEMENT"
    TYPE_ADIDY = "ADIDY"
    TYPE_TRAVAUX = "TRAVAUX"
    TYPE_EQUIPEMENT = "EQUIPEMENT"
    TYPE_DOCUMENT = "DOCUMENT"
    TYPE_AUTRE = "AUTRE"

    CHOIX_TYPES = [
        (TYPE_ROUTE, "Amélioration — Route"),
        (TYPE_ECOLE, "Amélioration — École"),
        (TYPE_COMMUNE, "Amélioration — Commune"),
        (TYPE_CSBII, "Amélioration — CSBII"),
        (TYPE_WC_PUBLIC, "Amélioration — WC public"),
        (TYPE_POMPE, "Amélioration — Pompe à eau"),
        (TYPE_CERTIFICAT_RESIDENCE, "Certificat de résidence"),
        (TYPE_RECENSEMENT, "Recensement"),
        (TYPE_ADIDY, "Paiement adidy"),
        (TYPE_TRAVAUX, "Travaux / route"),
        (TYPE_EQUIPEMENT, "Équipement / outillage"),
        (TYPE_DOCUMENT, "Document administratif"),
        (TYPE_AUTRE, "Autre"),
    ]

    TYPES_AMELIORATION = [
        TYPE_ROUTE,
        TYPE_ECOLE,
        TYPE_COMMUNE,
        TYPE_CSBII,
        TYPE_WC_PUBLIC,
        TYPE_POMPE,
    ]

    STATUT_EN_ATTENTE = "EN_ATTENTE"
    STATUT_MISE_EN_ATTENTE = "MISE_EN_ATTENTE"
    STATUT_ACCEPTEE = "ACCEPTEE"
    STATUT_REFUSEE = "REFUSEE"
    STATUT_ANNULEE = "ANNULEE"

    CHOIX_STATUTS = [
        (STATUT_EN_ATTENTE, "En attente"),
        (STATUT_MISE_EN_ATTENTE, "Mise en attente"),
        (STATUT_ACCEPTEE, "Acceptée"),
        (STATUT_REFUSEE, "Refusée"),
        (STATUT_ANNULEE, "Annulée"),
    ]

    STATUTS_FINIS = [STATUT_ACCEPTEE, STATUT_REFUSEE]

    PRIORITE_BASSE = "BASSE"
    PRIORITE_NORMALE = "NORMALE"
    PRIORITE_HAUTE = "HAUTE"
    PRIORITE_URGENTE = "URGENTE"

    CHOIX_PRIORITES = [
        (PRIORITE_BASSE, "Basse"),
        (PRIORITE_NORMALE, "Normale"),
        (PRIORITE_HAUTE, "Haute"),
        (PRIORITE_URGENTE, "Urgente"),
    ]

    reference = models.CharField(
        max_length=24,
        unique=True,
        blank=True,
        verbose_name="Référence",
    )
    type_demande = models.CharField(
        max_length=30,
        choices=CHOIX_TYPES,
        verbose_name="Type de demande",
    )
    objet = models.CharField(
        max_length=200,
        verbose_name="Objet",
    )
    description = models.TextField(
        verbose_name="Description de la demande",
    )
    priorite = models.CharField(
        max_length=10,
        choices=CHOIX_PRIORITES,
        default=PRIORITE_NORMALE,
        verbose_name="Priorité",
    )
    statut = models.CharField(
        max_length=20,
        choices=CHOIX_STATUTS,
        default=STATUT_EN_ATTENTE,
        verbose_name="Statut",
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        related_name="demandes",
        verbose_name="Fokontany",
    )
    demandeur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="demandes_envoyees",
        verbose_name="Demandeur",
    )
    citoyen = models.ForeignKey(
        "citoyens.Citoyen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes",
        verbose_name="Citoyen concerné",
    )
    document_souhaite = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Document souhaité",
        help_text="Ex. certificat de résidence, attestation de travail.",
    )
    reponse = models.TextField(
        blank=True,
        verbose_name="Réponse du maire",
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de la demande",
    )
    cachet_applique = models.BooleanField(
        default=False,
        verbose_name="Cachet officiel appliqué",
    )
    date_cachet = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'application du cachet",
    )
    date_traitement = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement",
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="demandes_traitees",
        verbose_name="Traitée par",
    )

    class Meta:
        verbose_name = "Demande"
        verbose_name_plural = "Demandes"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.reference} - {self.objet}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"DEM-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def en_attente(self):
        return self.statut == self.STATUT_EN_ATTENTE

    @property
    def est_finie(self):
        return self.statut in self.STATUTS_FINIS

    @property
    def contenu_qr(self):
        return f"{self.reference} - {self.objet}"

    def clean(self):
        if self.type_demande == self.TYPE_DOCUMENT and not self.document_souhaite:
            raise ValidationError({
                "document_souhaite": "Précisez le document demandé."
            })

        if self.citoyen_id and self.fokontany_id:
            if self.citoyen.fokontany_id != self.fokontany_id:
                raise ValidationError({
                    "citoyen": "Le citoyen doit appartenir au même fokontany."
                })
