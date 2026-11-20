from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from fokontany.models import Fokontany
from .forms import ConnexionForm
from .models import ParametrePlateforme, ProfilUtilisateur
from .permissions import (
    acces_global,
    est_administrateur,
    est_chef,
    est_maire,
    est_secretaire,
    est_tresorier,
    filtrer_fokontany,
    nom_role,
    role_required,
)

User = get_user_model()


class BaseComptesTestCase(TestCase):
    mot_de_passe = "MotDePasseTest123!"

    def setUp(self):
        self.f1 = Fokontany.objects.create(code="FKT-001", nom="Fokontany Un")
        self.f2 = Fokontany.objects.create(code="FKT-002", nom="Fokontany Deux")

    def creer_profil(self, username, role, fokontany=None, superuser=False):
        modele = User.objects.create_superuser if superuser else User.objects.create_user
        kwargs = {
            "username": username,
            "password": self.mot_de_passe,
            "email": f"{username}@example.com" if superuser else "",
        }
        if not superuser:
            kwargs.pop("email")
        utilisateur = modele(**kwargs)
        if not superuser:
            ProfilUtilisateur.objects.create(
                utilisateur=utilisateur,
                role=role,
                fokontany=fokontany,
            )
        return utilisateur

    def connexion(self, utilisateur):
        self.assertTrue(
            self.client.login(
                username=utilisateur.username,
                password=self.mot_de_passe,
            )
        )


class PermissionsTests(BaseComptesTestCase):
    def test_predicats_des_nouveaux_roles(self):
        admin = self.creer_profil("admin", ProfilUtilisateur.ROLE_ADMINISTRATEUR)
        tresorier = self.creer_profil("tresor", ProfilUtilisateur.ROLE_TRESORIER)
        secretaire = self.creer_profil("secret", ProfilUtilisateur.ROLE_SECRETAIRE)
        maire = self.creer_profil("maire", ProfilUtilisateur.ROLE_MAIRE)
        chef = self.creer_profil("chef", ProfilUtilisateur.ROLE_CHEF, self.f1)

        self.assertTrue(est_administrateur(admin))
        self.assertTrue(est_tresorier(tresorier))
        self.assertTrue(est_secretaire(secretaire))
        self.assertTrue(est_maire(maire))
        self.assertTrue(est_chef(chef))
        self.assertFalse(est_tresorier(secretaire))
        self.assertFalse(est_chef(admin))
        for utilisateur in (admin, tresorier, secretaire, maire):
            self.assertTrue(acces_global(utilisateur))
        self.assertFalse(acces_global(chef))

    def test_filtrer_fokontany_pour_chef_et_role_global(self):
        chef = self.creer_profil("chef", ProfilUtilisateur.ROLE_CHEF, self.f1)
        secretaire = self.creer_profil("secret", ProfilUtilisateur.ROLE_SECRETAIRE)

        self.assertEqual(
            list(filtrer_fokontany(Fokontany.objects.all(), chef, champ="pk")),
            [self.f1],
        )
        self.assertEqual(
            filtrer_fokontany(
                Fokontany.objects.all(), secretaire, champ="pk"
            ).count(),
            2,
        )

    def test_role_required_refuse_un_role_non_autorise(self):
        tresorier = self.creer_profil("tresor", ProfilUtilisateur.ROLE_TRESORIER)

        @role_required(ProfilUtilisateur.ROLE_SECRETAIRE)
        def vue_protegee(request):
            return HttpResponse("ok")

        requete = RequestFactory().get("/")
        requete.user = tresorier
        with self.assertRaises(PermissionDenied):
            vue_protegee(requete)

    def test_nom_role_du_superuser_est_administrateur(self):
        superuser = self.creer_profil("root", "", superuser=True)
        self.assertEqual(nom_role(superuser), "Administrateur")


class GestionComptesTests(BaseComptesTestCase):
    def setUp(self):
        super().setUp()
        self.admin = self.creer_profil(
            "admin", ProfilUtilisateur.ROLE_ADMINISTRATEUR
        )
        self.maire = self.creer_profil("maire", ProfilUtilisateur.ROLE_MAIRE)

    def test_administrateur_cree_un_tresorier(self):
        self.connexion(self.admin)
        reponse = self.client.post(reverse("comptes:gestion_chefs"), {
            "action": "role",
            "username": "tresorier2",
            "password": self.mot_de_passe,
            "nom_complet": "Rasoamanana",
            "role": ProfilUtilisateur.ROLE_TRESORIER,
            "fokontany": "",
        })
        self.assertEqual(reponse.status_code, 302)
        profil = ProfilUtilisateur.objects.get(
            utilisateur__username="tresorier2"
        )
        self.assertEqual(profil.role, ProfilUtilisateur.ROLE_TRESORIER)

    def test_role_unique_ne_peut_pas_etre_duplique(self):
        self.connexion(self.admin)
        self.client.post(reverse("comptes:gestion_chefs"), {
            "action": "role",
            "username": "maire2",
            "password": self.mot_de_passe,
            "role": ProfilUtilisateur.ROLE_MAIRE,
            "fokontany": "",
        })
        self.assertEqual(
            ProfilUtilisateur.objects.filter(
                role=ProfilUtilisateur.ROLE_MAIRE
            ).count(),
            1,
        )

    def test_chef_doit_etre_affecte_a_un_fokontany(self):
        self.connexion(self.admin)
        self.client.post(reverse("comptes:gestion_chefs"), {
            "action": "role",
            "username": "chef_sans_fok",
            "password": self.mot_de_passe,
            "role": ProfilUtilisateur.ROLE_CHEF,
            "fokontany": "",
        })
        self.assertFalse(User.objects.filter(username="chef_sans_fok").exists())

    def test_modification_et_suppression_d_un_compte(self):
        self.connexion(self.admin)
        profil = ProfilUtilisateur.objects.get(utilisateur=self.maire)
        self.client.post(reverse("comptes:gestion_chefs"), {
            "action": "modifier_role",
            "profil_id": profil.pk,
            "role": ProfilUtilisateur.ROLE_SECRETAIRE,
            "fokontany": "",
        })
        profil.refresh_from_db()
        self.assertEqual(profil.role, ProfilUtilisateur.ROLE_SECRETAIRE)

        self.client.post(reverse("comptes:gestion_chefs"), {
            "action": "supprimer",
            "profil_id": profil.pk,
        })
        self.assertFalse(User.objects.filter(username="maire").exists())

    def test_maire_ne_peut_pas_gerer_les_comptes(self):
        self.connexion(self.maire)
        self.assertEqual(
            self.client.get(reverse("comptes:gestion_chefs")).status_code,
            403,
        )


class ParametresTests(BaseComptesTestCase):
    def test_administrateur_enregistre_les_parametres(self):
        admin = self.creer_profil(
            "admin", ProfilUtilisateur.ROLE_ADMINISTRATEUR
        )
        self.connexion(admin)
        reponse = self.client.post(reverse("comptes:parametres"), {
            "nom_commune": "Commune Test",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(
            ParametrePlateforme.objects.get(cle="nom_commune").valeur,
            "Commune Test",
        )


class ConnexionFormTests(BaseComptesTestCase):
    def test_superuser_doit_choisir_le_role_administrateur(self):
        self.creer_profil("root", "", superuser=True)
        with_role_maire = ConnexionForm(data={
            "username": "root",
            "password": self.mot_de_passe,
            "role": ProfilUtilisateur.ROLE_MAIRE,
        })
        self.assertFalse(with_role_maire.is_valid())

        with_role_admin = ConnexionForm(data={
            "username": "root",
            "password": self.mot_de_passe,
            "role": ProfilUtilisateur.ROLE_ADMINISTRATEUR,
        })
        self.assertTrue(with_role_admin.is_valid())
