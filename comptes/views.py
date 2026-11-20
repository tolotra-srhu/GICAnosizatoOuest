from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect, render

from fokontany.models import Fokontany
from .models import ParametrePlateforme, ProfilUtilisateur
from .permissions import gestion_comptes_required

User = get_user_model()

ROLES_UNIQUES = [
    ProfilUtilisateur.ROLE_ADMINISTRATEUR,
    ProfilUtilisateur.ROLE_MAIRE,
    ProfilUtilisateur.ROLE_TRESORIER,
    ProfilUtilisateur.ROLE_SECRETAIRE,
]

PARAMETRES_DEFAUT = [
    ("nom_commune", "Nom de la commune", "Commune d'Anosizato Ouest"),
    ("slogan", "Slogan de la plateforme", "Plateforme de Gestion Intégrée Communale"),
    ("adresse", "Adresse de la commune", "Anosizato Ouest, Antananarivo Atsimondrano"),
    ("telephone", "Téléphone", ""),
    ("email", "Adresse e-mail", ""),
]


def _creer_utilisateur(username, password, role, fokontany=None, nom_complet=""):
    utilisateur_provisoire = User(username=username)
    validate_password(password, user=utilisateur_provisoire)

    utilisateur = User.objects.create_user(
        username=username,
        password=password,
        first_name=nom_complet,
    )
    try:
        profil = ProfilUtilisateur(
            utilisateur=utilisateur,
            role=role,
            fokontany=fokontany,
        )
        profil.full_clean()
        profil.save()
    except Exception:
        utilisateur.delete()
        raise
    return utilisateur


def _verifier_role(role, fokontany_id):
    if role not in dict(ProfilUtilisateur.CHOIX_ROLES):
        return "Rôle invalide."
    if role == ProfilUtilisateur.ROLE_CHEF and not fokontany_id:
        return "Choisissez le fokontany à affecter au chef."
    if role != ProfilUtilisateur.ROLE_CHEF and fokontany_id:
        return "Ce rôle intervient sur l'ensemble de la commune."
    return None


@gestion_comptes_required
def gestion_chefs(request):
    if request.method == "POST":
        action = request.POST.get("action", "role")
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        nom_complet = request.POST.get("nom_complet", "").strip()
        role = request.POST.get("role", "")
        fokontany_id = request.POST.get("fokontany", "")
        profil_id = request.POST.get("profil_id", "")

        error = None

        if action in ("chef", "role"):
            if not username or not password:
                error = "Le nom d'utilisateur et le mot de passe sont obligatoires."
            elif User.objects.filter(username=username).exists():
                error = "Ce nom d'utilisateur existe déjà."
            else:
                error = _verifier_role(role, fokontany_id)

            if not error and role == ProfilUtilisateur.ROLE_CHEF:
                if ProfilUtilisateur.objects.filter(
                    role=ProfilUtilisateur.ROLE_CHEF,
                    fokontany_id=fokontany_id,
                ).exists():
                    error = "Ce fokontany a déjà un chef affecté."

            if not error and role in ROLES_UNIQUES:
                if ProfilUtilisateur.objects.filter(role=role).exists():
                    error = "Un compte existe déjà pour ce rôle."

            if not error:
                try:
                    fokontany = None
                    if fokontany_id:
                        fokontany = Fokontany.objects.get(pk=fokontany_id)
                    _creer_utilisateur(
                        username,
                        password,
                        role,
                        fokontany=fokontany,
                        nom_complet=nom_complet,
                    )
                    messages.success(request, "Compte créé avec succès.")
                    return redirect("comptes:gestion_chefs")
                except Fokontany.DoesNotExist:
                    error = "Fokontany invalide."
                except ValidationError as erreur:
                    error = " ".join(erreur.messages)
                except IntegrityError:
                    error = "Impossible de créer ce compte."

        elif action == "modifier_role":
            profil = ProfilUtilisateur.objects.filter(pk=profil_id).first()
            if not profil:
                error = "Compte introuvable."
            elif profil.utilisateur_id == request.user.pk:
                error = "Vous ne pouvez pas modifier votre propre rôle."
            else:
                error = _verifier_role(role, fokontany_id)
                if not error and role == ProfilUtilisateur.ROLE_CHEF:
                    if ProfilUtilisateur.objects.filter(
                        role=ProfilUtilisateur.ROLE_CHEF,
                        fokontany_id=fokontany_id,
                    ).exclude(pk=profil.pk).exists():
                        error = "Ce fokontany a déjà un chef affecté."
                if not error and role in ROLES_UNIQUES:
                    if ProfilUtilisateur.objects.filter(role=role).exclude(pk=profil.pk).exists():
                        error = "Un compte existe déjà pour ce rôle."

                if not error:
                    try:
                        profil.role = role
                        profil.fokontany = (
                            Fokontany.objects.get(pk=fokontany_id)
                            if fokontany_id else None
                        )
                        profil.full_clean()
                        profil.save()
                        messages.success(request, "Rôle mis à jour avec succès.")
                        return redirect("comptes:gestion_chefs")
                    except Fokontany.DoesNotExist:
                        error = "Fokontany invalide."
                    except (ValidationError, IntegrityError) as erreur:
                        error = " ".join(erreur.messages) if isinstance(erreur, ValidationError) else "Mise à jour impossible."

        elif action == "supprimer":
            profil = ProfilUtilisateur.objects.filter(pk=profil_id).first()
            if not profil:
                error = "Compte introuvable."
            elif profil.utilisateur.pk == request.user.pk:
                error = "Vous ne pouvez pas supprimer votre propre compte."
            elif profil.utilisateur.is_superuser:
                error = "Le compte superutilisateur ne peut pas être supprimé."
            else:
                profil.utilisateur.delete()
                messages.success(request, "Compte supprimé avec succès.")
                return redirect("comptes:gestion_chefs")

        if error:
            messages.error(request, error)

    profils = ProfilUtilisateur.objects.select_related(
        "utilisateur", "fokontany"
    ).order_by("role", "utilisateur__username")

    return render(request, "comptes/gestion_chefs.html", {
        "profils": profils,
        "roles": ProfilUtilisateur.CHOIX_ROLES,
        "fokontanys": Fokontany.objects.filter(actif=True),
    })


@gestion_comptes_required
def parametres(request):
    for cle, libelle, valeur in PARAMETRES_DEFAUT:
        ParametrePlateforme.objects.get_or_create(
            cle=cle,
            defaults={"libelle": libelle, "valeur": valeur},
        )

    if request.method == "POST":
        for parametre in ParametrePlateforme.objects.all():
            parametre.valeur = request.POST.get(parametre.cle, "").strip()
            parametre.save()
        messages.success(request, "Paramètres enregistrés avec succès.")
        return redirect("comptes:parametres")

    return render(request, "comptes/parametres.html", {
        "parametres": ParametrePlateforme.objects.all(),
    })
