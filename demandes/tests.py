from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from citoyens.models import Citoyen
from comptes.models import ProfilUtilisateur
from fokontany.models import Fokontany
from .models import Demande

User = get_user_model()


class BaseGICTestCase(TestCase):
    mot_de_passe = "MotDePasseTest123!"

    def setUp(self):
        self.f1 = Fokontany.objects.create(code="FKT-001", nom="Fokontany Un")
        self.f2 = Fokontany.objects.create(code="FKT-002", nom="Fokontany Deux")

        self.administrateur = User.objects.create_user(
            username="administrateur",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.administrateur,
            role=ProfilUtilisateur.ROLE_ADMINISTRATEUR,
        )

        self.maire = User.objects.create_user(
            username="maire",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.maire,
            role=ProfilUtilisateur.ROLE_MAIRE,
        )

        self.tresorier = User.objects.create_user(
            username="tresorier",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.tresorier,
            role=ProfilUtilisateur.ROLE_TRESORIER,
        )

        self.secretaire = User.objects.create_user(
            username="secretaire",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.secretaire,
            role=ProfilUtilisateur.ROLE_SECRETAIRE,
        )

        self.chef1 = User.objects.create_user(
            username="chef1",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.chef1,
            role=ProfilUtilisateur.ROLE_CHEF,
            fokontany=self.f1,
        )

        self.chef2 = User.objects.create_user(
            username="chef2",
            password=self.mot_de_passe,
        )
        ProfilUtilisateur.objects.create(
            utilisateur=self.chef2,
            role=ProfilUtilisateur.ROLE_CHEF,
            fokontany=self.f2,
        )

        self.citoyen1 = Citoyen.objects.create(
            numero_citoyen="C-001",
            nom="Rakoto",
            prenoms="Jean",
            fokontany=self.f1,
        )
        self.citoyen2 = Citoyen.objects.create(
            numero_citoyen="C-002",
            nom="Rabe",
            prenoms="Marie",
            fokontany=self.f2,
        )

    def connexion(self, utilisateur):
        self.assertTrue(
            self.client.login(
                username=utilisateur.username,
                password=self.mot_de_passe,
            )
        )


class AuthentificationTests(BaseGICTestCase):
    def test_tableau_de_bord_necessite_connexion(self):
        reponse = self.client.get(reverse("accueil:dashboard"))
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(reverse("login"), reponse["Location"])

    def test_maire_voit_tableau_de_bord_global(self):
        self.connexion(self.maire)
        reponse = self.client.get(reverse("accueil:dashboard"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Vue globale")

    def test_deconnexion_redirige_vers_la_connexion(self):
        self.connexion(self.maire)
        reponse = self.client.post(reverse("logout"))
        self.assertEqual(reponse.status_code, 302)
        self.assertIn(reverse("login"), reponse["Location"])

    def test_chef_voit_son_fokontany(self):
        self.connexion(self.chef1)
        reponse = self.client.get(reverse("accueil:dashboard"))
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Fokontany Un")


class SansRoleTests(BaseGICTestCase):
    def test_utilisateur_sans_role_ne_peut_pas_acceder_aux_modules(self):
        utilisateur = User.objects.create_user(
            username="sansrole",
            password=self.mot_de_passe,
        )
        self.connexion(utilisateur)

        urls = [
            reverse("citoyens:liste"),
            reverse("etat_civil:liste"),
            reverse("personnel:liste"),
            reverse("demandes:liste"),
            reverse("fokontany:liste"),
        ]

        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403)


class CloisonnementFokontanyTests(BaseGICTestCase):
    def test_chef_ne_voit_que_les_citoyens_de_son_fokontany(self):
        self.connexion(self.chef1)
        reponse = self.client.get(reverse("citoyens:liste"))
        self.assertContains(reponse, "Rakoto")
        self.assertNotContains(reponse, "Rabe")

    def test_maire_voit_tous_les_citoyens(self):
        self.connexion(self.maire)
        reponse = self.client.get(reverse("citoyens:liste"))
        self.assertContains(reponse, "Rakoto")
        self.assertContains(reponse, "Rabe")

    def test_chef_cree_un_citoyen_dans_son_fokontany_uniquement(self):
        self.connexion(self.chef1)
        reponse = self.client.post(
            reverse("citoyens:ajouter"),
            {
                "numero_citoyen": "C-003",
                "nom": "Andria",
                "prenoms": "Paul",
                "date_naissance": "",
                "sexe": "M",
                "adresse": "",
                "telephone": "",
                "fokontany": self.f2.pk,
                "actif": "on",
            },
        )
        self.assertEqual(reponse.status_code, 302)

        citoyen = Citoyen.objects.get(numero_citoyen="C-003")
        self.assertEqual(citoyen.fokontany, self.f1)

    def test_chef_ne_peut_pas_modifier_un_citoyen_du_voisin(self):
        self.connexion(self.chef1)
        reponse = self.client.get(
            reverse("citoyens:modifier", args=[self.citoyen2.pk])
        )
        self.assertEqual(reponse.status_code, 404)

    def test_chef_ne_peut_pas_acceder_aux_comptes_des_chefs(self):
        self.connexion(self.chef1)
        reponse = self.client.get(reverse("comptes:gestion_chefs"))
        self.assertEqual(reponse.status_code, 403)

    def test_administrateur_peut_acceder_aux_comptes_et_parametres(self):
        self.connexion(self.administrateur)
        self.assertEqual(
            self.client.get(reverse("comptes:gestion_chefs")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("comptes:parametres")).status_code,
            200,
        )

    def test_maire_ne_peut_pas_acceder_aux_comptes(self):
        self.connexion(self.maire)
        reponse = self.client.get(reverse("comptes:gestion_chefs"))
        self.assertEqual(reponse.status_code, 403)


class WorkflowDemandeTests(BaseGICTestCase):
    def creer_demande(self, utilisateur, **extra):
        donnees = {
            "type_demande": Demande.TYPE_TRAVAUX,
            "objet": "Réparer la route principale",
            "description": "La route est dégradée après les pluies.",
            "priorite": Demande.PRIORITE_HAUTE,
            "citoyen": "",
            "document_souhaite": "",
        }
        donnees.update(extra)
        return self.client.post(reverse("demandes:creer"), donnees)

    def test_chef_cree_une_demande_pour_son_fokontany(self):
        self.connexion(self.chef1)
        reponse = self.creer_demande(self.chef1)
        self.assertEqual(reponse.status_code, 302)

        demande = Demande.objects.get()
        self.assertEqual(demande.fokontany, self.f1)
        self.assertEqual(demande.demandeur, self.chef1)
        self.assertEqual(demande.statut, Demande.STATUT_EN_ATTENTE)

    def test_maire_accepte_une_demande(self):
        self.connexion(self.chef1)
        self.creer_demande(self.chef1)
        demande = Demande.objects.get()

        self.client.logout()
        self.connexion(self.maire)
        reponse = self.client.post(
            reverse("demandes:traiter", args=[demande.pk]),
            {
                "decision": "ACCEPTEE",
                "reponse": "Travaux autorisés.",
            },
        )
        self.assertEqual(reponse.status_code, 302)

        demande.refresh_from_db()
        self.assertEqual(demande.statut, Demande.STATUT_ACCEPTEE)
        self.assertEqual(demande.traite_par, self.maire)
        self.assertIsNotNone(demande.date_traitement)

    def test_refus_sans_motif_est_refuse(self):
        self.connexion(self.chef1)
        self.creer_demande(self.chef1)
        demande = Demande.objects.get()

        self.client.logout()
        self.connexion(self.maire)
        self.client.post(
            reverse("demandes:traiter", args=[demande.pk]),
            {"decision": "REFUSEE", "reponse": ""},
        )

        demande.refresh_from_db()
        self.assertEqual(demande.statut, Demande.STATUT_EN_ATTENTE)

    def test_chef_ne_peut_pas_voir_la_demande_d_un_autre_fokontany(self):
        self.connexion(self.chef1)
        self.creer_demande(self.chef1)
        demande = Demande.objects.get()

        self.client.logout()
        self.connexion(self.chef2)
        reponse = self.client.get(
            reverse("demandes:detail", args=[demande.pk])
        )
        self.assertEqual(reponse.status_code, 404)

    def test_demande_de_document_exige_le_document(self):
        self.connexion(self.chef1)
        reponse = self.creer_demande(
            self.chef1,
            type_demande=Demande.TYPE_DOCUMENT,
            document_souhaite="",
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(Demande.objects.count(), 0)

    def test_maire_ne_peut_pas_creer_une_demande_de_chef(self):
        self.connexion(self.maire)
        reponse = self.client.get(reverse("demandes:creer"))
        self.assertEqual(reponse.status_code, 403)


class RolesMetierTests(BaseGICTestCase):
    def test_tresorier_accede_a_la_caisse_pas_le_secretaire(self):
        self.connexion(self.tresorier)
        self.assertEqual(
            self.client.get(reverse("finances:fonds_liste")).status_code,
            200,
        )
        self.client.logout()
        self.connexion(self.secretaire)
        self.assertEqual(
            self.client.get(reverse("finances:fonds_liste")).status_code,
            403,
        )

    def test_secretaire_voit_tous_les_citoyens(self):
        self.connexion(self.secretaire)
        reponse = self.client.get(reverse("citoyens:liste"))
        self.assertContains(reponse, "Rakoto")
        self.assertContains(reponse, "Rabe")

    def test_secretaire_cree_une_demande_avec_fokontany_choisi(self):
        self.connexion(self.secretaire)
        reponse = self.client.post(reverse("demandes:creer"), {
            "type_demande": Demande.TYPE_TRAVAUX,
            "fokontany": self.f2.pk,
            "objet": "Éclairage public",
            "description": "Installer des lampes sur la route.",
            "priorite": Demande.PRIORITE_NORMALE,
            "citoyen": "",
            "document_souhaite": "",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(Demande.objects.get().fokontany, self.f2)

    def test_tresorier_ne_peut_pas_creer_de_demande(self):
        self.connexion(self.tresorier)
        self.assertEqual(
            self.client.get(reverse("demandes:creer")).status_code,
            403,
        )

    def test_secretaire_traite_une_demande(self):
        self.connexion(self.chef1)
        self.client.post(reverse("demandes:creer"), {
            "type_demande": Demande.TYPE_TRAVAUX,
            "objet": "Réparer la route",
            "description": "Route dégradée.",
            "priorite": Demande.PRIORITE_HAUTE,
            "citoyen": "",
            "document_souhaite": "",
        })
        demande = Demande.objects.get()
        self.client.logout()

        self.connexion(self.secretaire)
        reponse = self.client.post(
            reverse("demandes:traiter", args=[demande.pk]),
            {"decision": "ACCEPTEE", "reponse": "Travaux autorisés."},
        )
        self.assertEqual(reponse.status_code, 302)
        demande.refresh_from_db()
        self.assertEqual(demande.statut, Demande.STATUT_ACCEPTEE)
        self.assertEqual(demande.traite_par, self.secretaire)
