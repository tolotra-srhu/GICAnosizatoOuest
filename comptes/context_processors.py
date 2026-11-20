from .permissions import (
    acces_global,
    est_administrateur,
    est_chef,
    est_maire,
    est_secretaire,
    est_tresorier,
    fokontany_utilisateur,
    nom_role,
    profil_utilisateur,
)


def navigation(request):
    profil = profil_utilisateur(request.user)
    return {
        "est_administrateur": est_administrateur(request.user),
        "est_maire": est_maire(request.user),
        "est_administration": est_maire(request.user),
        "est_tresorier": est_tresorier(request.user),
        "est_secretaire": est_secretaire(request.user),
        "est_chef": est_chef(request.user),
        "acces_global": acces_global(request.user),
        "role_libelle": nom_role(request.user),
        "role_code": profil.role if profil else "",
        "fokontany_connecte": fokontany_utilisateur(request.user),
    }
