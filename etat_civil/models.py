from django.conf import settings
from django.db import models
from django.utils import timezone


class ActeEtatCivil(models.Model):
    TYPE_ACTE_CHOICES = [
        ("NAISSANCE", "Naissance"),
        ("MARIAGE", "Mariage"),
        ("DECES", "Décès"),
    ]

    numero_acte = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de l'acte"
    )
    type_acte = models.CharField(
        max_length=20,
        choices=TYPE_ACTE_CHOICES,
        verbose_name="Type d'acte"
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="actes_etat_civil",
        verbose_name="Fokontany",
    )
    date_acte = models.DateField(
        verbose_name="Date de l'acte"
    )
    lieu_acte = models.CharField(
        max_length=200,
        verbose_name="Lieu de l'acte"
    )
    observations = models.TextField(
        blank=True,
        verbose_name="Observations"
    )
    date_enregistrement = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'enregistrement"
    )

    class Meta:
        verbose_name = "Acte d'état civil"
        verbose_name_plural = "Actes d'état civil"
        ordering = ["-date_acte", "numero_acte"]

    def __str__(self):
        return f"{self.get_type_acte_display()} - {self.numero_acte}"

class ActeNaissance(models.Model):
    SEXE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]

    numero_acte = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de l'acte",
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        related_name="actes_naissance",
        verbose_name="Fokontany",
    )
    nom_enfant = models.CharField(max_length=100, verbose_name="Nom de l'enfant")
    prenoms_enfant = models.CharField(
        max_length=150,
        verbose_name="Prénoms de l'enfant",
    )
    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        verbose_name="Sexe",
    )
    date_naissance = models.DateField(verbose_name="Date de naissance")
    heure_naissance = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de naissance",
    )
    lieu_naissance = models.CharField(
        max_length=200,
        verbose_name="Lieu de naissance",
    )
    nom_pere = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom du père",
    )
    nom_mere = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom de la mère",
    )
    declarant = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Déclarant",
    )
    date_declaration = models.DateField(
        default=timezone.localdate,
        verbose_name="Date de déclaration",
    )
    observations = models.TextField(blank=True, verbose_name="Observations")
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actes_naissance_enregistres",
        verbose_name="Enregistré par",
    )
    date_enregistrement = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'enregistrement",
    )

    class Meta:
        verbose_name = "Acte de naissance"
        verbose_name_plural = "Actes de naissance"
        ordering = ["-date_naissance", "numero_acte"]

    def __str__(self):
        return f"{self.numero_acte} - {self.nom_enfant} {self.prenoms_enfant}"


class DocumentAdministratif(models.Model):
    TYPE_CIN = "CIN"
    TYPE_BULLETIN_NAISSANCE = "BULLETIN_NAISSANCE"
    TYPE_ACTE_NAISSANCE = "ACTE_NAISSANCE"
    TYPE_CERTIFICAT_RESIDENCE = "CERTIFICAT_RESIDENCE"
    TYPE_ATTESTATION = "ATTESTATION"

    CHOIX_TYPES = [
        (TYPE_CIN, "Carte d'identité nationale (CIN)"),
        (TYPE_BULLETIN_NAISSANCE, "Bulletin de naissance"),
        (TYPE_ACTE_NAISSANCE, "Acte de naissance"),
        (TYPE_CERTIFICAT_RESIDENCE, "Certificat de résidence"),
        (TYPE_ATTESTATION, "Attestation"),
    ]

    USAGE_ETUDIANT = "ETUDIANT"
    USAGE_TRAVAIL = "TRAVAIL"
    USAGE_AUTRE = "AUTRE"

    CHOIX_USAGES = [
        (USAGE_ETUDIANT, "Dossier étudiant"),
        (USAGE_TRAVAIL, "Dossier de travail"),
        (USAGE_AUTRE, "Autre utilisation"),
    ]

    numero = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro du document",
    )
    type_document = models.CharField(
        max_length=30,
        choices=CHOIX_TYPES,
        verbose_name="Type de document",
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        related_name="documents_administratifs",
        verbose_name="Fokontany",
    )
    citoyen = models.ForeignKey(
        "citoyens.Citoyen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_administratifs",
        verbose_name="Citoyen",
    )
    nom_beneficiaire = models.CharField(
        max_length=150,
        verbose_name="Nom complet du bénéficiaire",
    )
    nom_pere = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom du père",
    )
    nom_mere = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom de la mère",
    )
    date_naissance = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de naissance",
    )
    lieu_naissance = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Lieu de naissance",
    )
    usage = models.CharField(
        max_length=20,
        choices=CHOIX_USAGES,
        default=USAGE_AUTRE,
        verbose_name="Utilisation du document",
    )
    date_delivrance = models.DateField(
        default=timezone.localdate,
        verbose_name="Date de délivrance",
    )
    delivre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents_delivres",
        verbose_name="Délivré par",
    )
    observations = models.TextField(blank=True, verbose_name="Observations")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document administratif"
        verbose_name_plural = "Documents administratifs"
        ordering = ["-date_delivrance", "-date_creation"]

    def __str__(self):
        return f"{self.numero} - {self.get_type_document_display()}"
