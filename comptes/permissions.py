from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import ProfilUtilisateur


def profil_utilisateur(user):
    if not user.is_authenticated:
        return None
    return getattr(user, "profil_gic", None)


def est_administrateur(user):
    """Gestion des comptes, des rôles et des paramètres de la plateforme."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profil = profil_utilisateur(user)
    return bool(
        profil
        and profil.role in ProfilUtilisateur.ROLES_GESTION_COMPTES
    )


def est_maire(user):
    """Vrai pour le Maire et ses adjoints (supervision communale)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profil = profil_utilisateur(user)
    return bool(
        profil
        and profil.role in ProfilUtilisateur.ROLES_ADMINISTRATION
    )


def est_administration(user):
    return est_maire(user)


def est_tresorier(user):
    """Gestion et suivi des opérations de trésorerie."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profil = profil_utilisateur(user)
    return bool(
        profil
        and profil.role in ProfilUtilisateur.ROLES_TRESORERIE
    )


def est_secretaire(user):
    """Gestion des informations et opérations administratives."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profil = profil_utilisateur(user)
    return bool(
        profil
        and profil.role in ProfilUtilisateur.ROLES_SECRETARIAT
    )


def est_chef(user):
    profil = profil_utilisateur(user)
    return bool(profil and profil.role == ProfilUtilisateur.ROLE_CHEF)


def acces_global(user):
    """Vrai pour tous les rôles qui interviennent sur toute la commune."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profil = profil_utilisateur(user)
    return bool(profil and profil.role in ProfilUtilisateur.ROLES_GLOBAUX)


def fokontany_utilisateur(user):
    profil = profil_utilisateur(user)
    if profil and profil.role == ProfilUtilisateur.ROLE_CHEF:
        return profil.fokontany
    return None


def nom_role(user):
    if user.is_superuser:
        return "Administrateur"
    profil = profil_utilisateur(user)
    if not profil:
        return "Utilisateur"
    return profil.get_role_display()


def filtrer_fokontany(queryset, user, champ="fokontany"):
    if acces_global(user):
        return queryset
    fokontany = fokontany_utilisateur(user)
    if not fokontany:
        return queryset.none()

    if champ == "pk":
        return queryset.filter(pk=fokontany.pk)

    return queryset.filter(**{champ: fokontany})


def _roles_autorises(roles):
    autorises = set(roles)
    if ProfilUtilisateur.ROLE_MAIRE in autorises:
        autorises.update(ProfilUtilisateur.ROLES_ADMINISTRATION)
    return autorises


def role_required(*roles):
    autorises = _roles_autorises(roles)

    def decorateur(vue):
        @login_required
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            if request.user.is_superuser:
                return vue(request, *args, **kwargs)

            profil = profil_utilisateur(request.user)
            if not profil or profil.role not in autorises:
                raise PermissionDenied

            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur


gestion_comptes_required = role_required(
    *ProfilUtilisateur.ROLES_GESTION_COMPTES,
)

tresorerie_required = role_required(
    *ProfilUtilisateur.ROLES_TRESORERIE,
    *ProfilUtilisateur.ROLES_SUPERVISION,
)

secretariat_required = role_required(
    *ProfilUtilisateur.ROLES_SECRETARIAT,
    *ProfilUtilisateur.ROLES_SUPERVISION,
)

acces_supervision = role_required(*ProfilUtilisateur.ROLES_SUPERVISION)

acces_communal = role_required(
    *ProfilUtilisateur.ROLES_SUPERVISION,
    *ProfilUtilisateur.ROLES_TRESORERIE,
    *ProfilUtilisateur.ROLES_SECRETARIAT,
    ProfilUtilisateur.ROLE_CHEF,
)
