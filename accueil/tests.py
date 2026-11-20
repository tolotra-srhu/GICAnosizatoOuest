from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from comptes.models import ProfilUtilisateur
from fokontany.models import Fokontany, PopulationFokontany


User = get_user_model()


class PopulationContexteTests(TestCase):
    mot_de_passe = "MotDePasseTest123!"

    def setUp(self):
        self.fokontany = Fokontany.objects.create(
            code="AO-FKT-001",
            nom="Ampefiloha",
        )
        PopulationFokontany.objects.create(
            fokontany=self.fokontany,
            hommes=1891,
            femmes=2054,
        )

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
            fokontany=self.fokontany,
        )

    def test_accueil_et_commune_affichent_les_totaux(self):
        for url in (reverse("accueil:accueil"), reverse("accueil:commune")):
            with self.subTest(url=url):
                reponse = self.client.get(url)
                self.assertEqual(reponse.status_code, 200)
                self.assertEqual(
                    reponse.context["totaux_population"]["hommes"], 1891
                )
                self.assertEqual(
                    reponse.context["totaux_population"]["femmes"], 2054
                )
                self.assertEqual(
                    reponse.context["totaux_population"]["total"], 3945
                )

    def test_dashboard_global_contient_la_population(self):
        self.client.login(username="admin", password=self.mot_de_passe)
        reponse = self.client.get(reverse("accueil:dashboard"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.context["totaux_population"]["total"], 3945)
        self.assertEqual(
            reponse.context["fokontanys"][0].population_hommes, 1891
        )

    def test_dashboard_chef_contient_sa_population(self):
        self.client.login(username="chef", password=self.mot_de_passe)
        reponse = self.client.get(reverse("accueil:dashboard"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.context["population"].total, 3945)

    def test_carte_contient_les_chiffres_par_fokontany(self):
        self.client.login(username="chef", password=self.mot_de_passe)
        reponse = self.client.get(reverse("fokontany:carte"))
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(
            reponse.context["fokontany"][0]["population_hommes"], 1891
        )
        self.assertEqual(
            reponse.context["fokontany"][0]["population_femmes"], 2054
        )
