from django.core.management.base import BaseCommand
from fokontany.models import Fokontany


class Command(BaseCommand):
    help = (
        "Charge les 7 fokontany de la commune d'Anosizato Ouest "
        "et leurs responsables selon la monographie"
    )

    RESPONSABLES = [
        ("Ampefiloha", "RATSITOHARA Bien Aimée"),
        ("Antokotanitsara", "RASOARISOA Charline"),
        ("Ambanimaso", "RAHARIMANANA Emilienne"),
        ("Antananambony", "RAHARISOA Jeannette"),
        ("Ambodivona", "RANAIVOSON Alfred"),
        ("Ankazotoho", "RAVONJISOA Bruno"),
        ("Antandrokomby", "RASOANIRINA Arimalala"),
    ]

    COORDONNEES = {
        "Antandrokomby": ("-18.941290", "47.490280"),
        "Ampefiloha": ("-18.933830", "47.493990"),
        "Antokotanitsara": ("-18.937330", "47.492370"),
        "Antananambony": ("-18.939360", "47.497360"),
        "Ambanimaso": ("-18.939790", "47.494520"),
        "Ambodivona": ("-18.943990", "47.493350"),
        "Ankazotoho": ("-18.944830", "47.497880"),
    }

    def handle(self, *args, **options):
        for index, (nom, responsable) in enumerate(self.RESPONSABLES, start=1):
            latitude, longitude = self.COORDONNEES[nom]
            objet, cree = Fokontany.objects.get_or_create(
                nom=nom,
                defaults={
                    "code": f"AO-FKT-{index:03d}",
                    "responsable": responsable,
                    "latitude": latitude,
                    "longitude": longitude,
                    "actif": True,
                },
            )

            if cree:
                self.stdout.write(
                    self.style.SUCCESS(f"Ajouté : {objet.nom} — {responsable}")
                )
                continue

            champs_a_maj = []

            if objet.responsable != responsable:
                objet.responsable = responsable
                champs_a_maj.append("responsable")

            if (
                str(objet.latitude or "") != latitude or
                str(objet.longitude or "") != longitude
            ):
                objet.latitude = latitude
                objet.longitude = longitude
                champs_a_maj.extend(["latitude", "longitude"])

            if champs_a_maj:
                objet.save(update_fields=champs_a_maj)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Mis à jour : {objet.nom} — {', '.join(champs_a_maj)}"
                    )
                )
            else:
                self.stdout.write(f"Déjà présent : {objet.nom}")

        self.stdout.write(
            self.style.SUCCESS("Chargement des fokontany terminé.")
        )
