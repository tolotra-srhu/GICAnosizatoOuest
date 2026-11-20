from django.core.management import call_command
from django.core.management.base import BaseCommand

from fokontany.models import (
    ANNEE_POPULATION_REFERENCE,
    SOURCE_POPULATION_REFERENCE,
    Fokontany,
    PopulationFokontany,
)


DONNEES_POPULATION = [
    ("Antokotanitsara", 2466, 2606),
    ("Ambodivona", 2520, 2826),
    ("Ampefiloha", 1891, 2054),
    ("Antananambony", 1643, 2269),
    ("Ankazotoho", 1966, 1904),
    ("Antandrokomby", 1937, 1989),
    ("Ambanimaso", 1422, 1795),
]


class Command(BaseCommand):
    help = "Charge la population de référence des 7 fokontany (hommes/femmes)"

    def handle(self, *args, **options):
        call_command("charger_fokontany", verbosity=0)

        for nom, hommes, femmes in DONNEES_POPULATION:
            fokontany = Fokontany.objects.get(nom=nom)
            population, cree = PopulationFokontany.objects.update_or_create(
                fokontany=fokontany,
                annee=ANNEE_POPULATION_REFERENCE,
                defaults={
                    "hommes": hommes,
                    "femmes": femmes,
                    "source": SOURCE_POPULATION_REFERENCE,
                },
            )

            action = "Ajouté" if cree else "Mis à jour"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} : {population.fokontany.nom} "
                    f"({hommes} H / {femmes} F / {hommes + femmes} habitants)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Chargement de la population {ANNEE_POPULATION_REFERENCE} terminé."
            )
        )
