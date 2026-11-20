from django.db import models


class Personnel(models.Model):
    SEXE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]

    STATUT_CHOICES = [
        ("ACTIF", "Actif"),
        ("CONGE", "En congé"),
        ("SUSPENDU", "Suspendu"),
        ("RETRAITE", "Retraité"),
    ]

    matricule = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Matricule"
    )
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    prenoms = models.CharField(
        max_length=150,
        verbose_name="Prénoms"
    )
    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        blank=True,
        verbose_name="Sexe"
    )
    fonction = models.CharField(
        max_length=100,
        verbose_name="Fonction"
    )
    service = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Service"
    )
    fokontany = models.ForeignKey(
        "fokontany.Fokontany",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="agents",
        verbose_name="Fokontany",
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Adresse e-mail"
    )
    photo = models.ImageField(
        upload_to="personnel/",
        null=True,
        blank=True,
        verbose_name="Photo",
    )
    date_embauche = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'embauche"
    )
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default="ACTIF",
        verbose_name="Statut"
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    class Meta:
        verbose_name = "Agent communal"
        verbose_name_plural = "Personnel communal"
        ordering = ["nom", "prenoms"]

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenoms}"