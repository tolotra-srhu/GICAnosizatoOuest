from django.db import models
from django.db.models import OuterRef, Subquery, Sum


ANNEE_POPULATION_REFERENCE = 2026
SOURCE_POPULATION_REFERENCE = "Recensement administratif 2026"


class Fokontany(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code du fokontany",
    )
    nom = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du fokontany",
    )
    responsable = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Nom du responsable",
    )
    adresse = models.TextField(
        blank=True,
        verbose_name="Adresse",
    )
    specificites = models.TextField(
        blank=True,
        verbose_name="Spécificités du fokontany",
        help_text="Activités, sites remarquables, particularités locales…",
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Latitude",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Longitude",
    )
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    class Meta:
        verbose_name = "Fokontany"
        verbose_name_plural = "Fokontany"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.code} - {self.nom}"


class PopulationFokontany(models.Model):
    fokontany = models.ForeignKey(
        Fokontany,
        on_delete=models.PROTECT,
        related_name="populations",
        verbose_name="Fokontany",
    )
    annee = models.PositiveIntegerField(
        default=ANNEE_POPULATION_REFERENCE,
        verbose_name="Année de référence",
    )
    hommes = models.PositiveIntegerField(
        default=0,
        verbose_name="Hommes",
    )
    femmes = models.PositiveIntegerField(
        default=0,
        verbose_name="Femmes",
    )
    source = models.CharField(
        max_length=200,
        blank=True,
        default=SOURCE_POPULATION_REFERENCE,
        verbose_name="Source des données",
    )
    date_mise_a_jour = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de mise à jour",
    )

    class Meta:
        verbose_name = "Population de fokontany"
        verbose_name_plural = "Populations des fokontany"
        ordering = ["-annee", "fokontany__nom"]
        constraints = [
            models.UniqueConstraint(
                fields=["fokontany", "annee"],
                name="population_unique_par_fokontany_annee",
            ),
        ]

    def __str__(self):
        return f"{self.fokontany.nom} — {self.annee}"

    @property
    def total(self):
        return self.hommes + self.femmes


def annoter_population(queryset, annee=ANNEE_POPULATION_REFERENCE):
    population = PopulationFokontany.objects.filter(
        fokontany=OuterRef("pk"),
        annee=annee,
    )
    return queryset.annotate(
        population_hommes=Subquery(population.values("hommes")[:1]),
        population_femmes=Subquery(population.values("femmes")[:1]),
    )


def totaux_population(annee=ANNEE_POPULATION_REFERENCE):
    totaux = PopulationFokontany.objects.filter(annee=annee).aggregate(
        hommes=Sum("hommes"),
        femmes=Sum("femmes"),
    )
    hommes = totaux["hommes"] or 0
    femmes = totaux["femmes"] or 0
    return {
        "annee": annee,
        "hommes": hommes,
        "femmes": femmes,
        "total": hommes + femmes,
    }
