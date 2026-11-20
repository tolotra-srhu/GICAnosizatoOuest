from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from comptes.models import ProfilUtilisateur

from .models import (
    ANNEE_POPULATION_REFERENCE,
    SOURCE_POPULATION_REFERENCE,
    Fokontany,
    PopulationFokontany,
    annoter_population,
    totaux_population,
)


User = get_user_model()


class PopulationModeleTests(TestCase):
    def setUp(self):
        self.fokontany = Fokontany.objects.create(
            code="AO-FKT-001",
            nom="Antokotanitsara",
        )

    def test_total_est_calcule(self):
        population = PopulationFokontany.objects.create(
            fokontany=self.fokontany,
            annee=ANNEE_POPULATION_REFERENCE,
            hommes=2466,
            femmes=2606,
        )
        self.assertEqual(population.total, 5072)

    def test_unicite_par_fokontany_et_annee(self):
        PopulationFokontany.objects.create(
            fokontany=self.fokontany,
            annee=ANNEE_POPULATION_REFERENCE,
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            PopulationFokontany.objects.create(
                fokontany=self.fokontany,
                annee=ANNEE_POPULATION_REFERENCE,
            )

    def test_annotation_et_totaux(self):
        PopulationFokontany.objects.create(
            fokontany=self.fokontany,
            hommes=2466,
            femmes=2606,
        )
        donnees = annoter_population(Fokontany.objects.all()).get(
            pk=self.fokontany.pk
        )
        self.assertEqual(donnees.population_hommes, 2466)
        self.assertEqual(donnees.population_femmes, 2606)
        self.assertEqual(
            totaux_population(),
            {
                "annee": ANNEE_POPULATION_REFERENCE,
                "hommes": 2466,
                "femmes": 2606,
                "total": 5072,
            },
        )


class CommandeChargerFokontanyTests(TestCase):
    def test_responsables_selon_la_monographie(self):
        call_command("charger_fokontany", verbosity=0)

        attendus = {
            "Ampefiloha": "RATSITOHARA Bien Aimée",
            "Antokotanitsara": "RASOARISOA Charline",
            "Ambanimaso": "RAHARIMANANA Emilienne",
            "Antananambony": "RAHARISOA Jeannette",
            "Ambodivona": "RANAIVOSON Alfred",
            "Ankazotoho": "RAVONJISOA Bruno",
            "Antandrokomby": "RASOANIRINA Arimalala",
        }
        for nom, responsable in attendus.items():
            with self.subTest(nom=nom):
                self.assertEqual(
                    Fokontany.objects.get(nom=nom).responsable,
                    responsable,
                )

    def test_coordonnees_gps_selon_geonames(self):
        call_command("charger_fokontany", verbosity=0)

        attendus = {
            "Antandrokomby": ("-18.941290", "47.490280"),
            "Ampefiloha": ("-18.933830", "47.493990"),
            "Antokotanitsara": ("-18.937330", "47.492370"),
            "Antananambony": ("-18.939360", "47.497360"),
            "Ambanimaso": ("-18.939790", "47.494520"),
            "Ambodivona": ("-18.943990", "47.493350"),
            "Ankazotoho": ("-18.944830", "47.497880"),
        }
        for nom, (latitude, longitude) in attendus.items():
            with self.subTest(nom=nom):
                fokontany = Fokontany.objects.get(nom=nom)
                self.assertEqual(str(fokontany.latitude), latitude)
                self.assertEqual(str(fokontany.longitude), longitude)

    def test_mise_a_jour_sans_ecraser_le_code(self):
        Fokontany.objects.create(
            code="MG11117012001",
            nom="Ampefiloha",
            responsable="Ancien responsable",
        )
        call_command("charger_fokontany", verbosity=0)

        fokontany = Fokontany.objects.get(nom="Ampefiloha")
        self.assertEqual(fokontany.code, "MG11117012001")
        self.assertEqual(fokontany.responsable, "RATSITOHARA Bien Aimée")
        self.assertEqual(str(fokontany.latitude), "-18.933830")
        self.assertEqual(str(fokontany.longitude), "47.493990")


class CommandeChargerPopulationTests(TestCase):
    def test_charge_les_sept_fokontany_et_est_idempotente(self):
        call_command("charger_population", verbosity=0)

        self.assertEqual(Fokontany.objects.count(), 7)
        self.assertEqual(PopulationFokontany.objects.count(), 7)
        self.assertEqual(
            totaux_population(),
            {
                "annee": ANNEE_POPULATION_REFERENCE,
                "hommes": 13845,
                "femmes": 15443,
                "total": 29288,
            },
        )

        population = PopulationFokontany.objects.get(
            fokontany__nom="Antokotanitsara"
        )
        self.assertEqual(population.hommes, 2466)
        self.assertEqual(population.femmes, 2606)
        self.assertEqual(population.source, SOURCE_POPULATION_REFERENCE)

        call_command("charger_population", verbosity=0)
        self.assertEqual(PopulationFokontany.objects.count(), 7)
        self.assertEqual(totaux_population()["total"], 29288)


class PopulationVuesTests(TestCase):
    mot_de_passe = "MotDePasseTest123!"

    def setUp(self):
        self.f1 = Fokontany.objects.create(code="AO-FKT-001", nom="Ampefiloha")
        self.f2 = Fokontany.objects.create(code="AO-FKT-002", nom="Ambodivona")

        self.admin = User.objects.create_user(
            username="admin", password=self.mot_de_passe
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.admin,
            role=ProfilUtilisateur.ROLE_ADMINISTRATEUR,
        )
        self.chef = User.objects.create_user(
            username="chef", password=self.mot_de_passe
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.chef,
            role=ProfilUtilisateur.ROLE_CHEF,
            fokontany=self.f1,
        )
        PopulationFokontany.objects.create(
            fokontany=self.f1,
            hommes=1891,
            femmes=2054,
        )

    def test_liste_et_detail_affichent_la_population(self):
        self.client.login(username="admin", password=self.mot_de_passe)
        reponse = self.client.get(reverse("fokontany:liste"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "1891")
        self.assertContains(reponse, "2054")

        reponse = self.client.get(
            reverse("fokontany:detail", args=[self.f1.pk])
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "3945")

    def test_carte_transmet_les_coordonnees_gps(self):
        self.f1.latitude = "-18.933830"
        self.f1.longitude = "47.493990"
        self.f1.save(update_fields=["latitude", "longitude"])

        self.client.login(username="admin", password=self.mot_de_passe)
        reponse = self.client.get(reverse("fokontany:carte"))
        self.assertEqual(reponse.status_code, 200)

        donnees = next(
            f for f in reponse.context["fokontany"] if f["nom"] == "Ampefiloha"
        )
        self.assertEqual(str(donnees["latitude"]), "-18.933830")
        self.assertEqual(str(donnees["longitude"]), "47.493990")

    def test_admin_peut_editer_la_population(self):
        self.client.login(username="admin", password=self.mot_de_passe)
        reponse = self.client.get(reverse("fokontany:population"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(len(reponse.context["lignes"]), 2)

        reponse = self.client.post(reverse("fokontany:population"), {
            "source": "Recensement administratif 2026",
            f"hommes_{self.f1.pk}": "1891",
            f"femmes_{self.f1.pk}": "2054",
            f"hommes_{self.f2.pk}": "2520",
            f"femmes_{self.f2.pk}": "2826",
        })
        self.assertRedirects(reponse, reverse("fokontany:population"))
        self.assertEqual(
            totaux_population()["total"],
            1891 + 2054 + 2520 + 2826,
        )

    def test_chef_ne_peut_pas_acceder_a_l_edition(self):
        self.client.login(username="chef", password=self.mot_de_passe)
        reponse = self.client.get(reverse("fokontany:population"))
        self.assertEqual(reponse.status_code, 403)
