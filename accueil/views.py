from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from django.utils import timezone

from citoyens.models import Citoyen
from comptes.permissions import (
    acces_global,
    est_administrateur,
    est_chef,
    est_maire,
    est_secretaire,
    est_tresorier,
    fokontany_utilisateur,
    nom_role,
)
from demandes.models import Demande
from etat_civil.models import ActeEtatCivil, ActeNaissance, DocumentAdministratif
from finances.models import FondsAssociation, PaiementAdidy
from fokontany.models import (
    ANNEE_POPULATION_REFERENCE,
    Fokontany,
    annoter_population,
    totaux_population,
)
from personnel.models import Personnel
from .models import Actualite


MOIS_FR = [
    "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sep", "Oct", "Nov", "Déc",
]


def _derniers_mois(nombre=12):
    aujourdhui = timezone.localdate()
    index = aujourdhui.year * 12 + aujourdhui.month - 1
    mois = []
    for decalage in range(nombre - 1, -1, -1):
        valeur = index - decalage
        annee, mois_num = divmod(valeur, 12)
        mois.append((annee, mois_num + 1))
    return mois


def _serie_mensuelle(queryset, champ, periodes):
    valeurs = (
        queryset.annotate(periode_mois=TruncMonth(champ))
        .values("periode_mois")
        .annotate(total=Count("id"))
        .values_list("periode_mois", "total")
    )
    index = {}
    for valeur, total in valeurs:
        if valeur is None:
            continue
        index[(valeur.year, valeur.month)] = total
    return [index.get(periode, 0) for periode in periodes]


def _donnees_graphique(periodes, fokontany=None):
    citoyens = Citoyen.objects.all()
    naissances = ActeNaissance.objects.all()
    demandes = Demande.objects.all()
    adidy = PaiementAdidy.objects.all()

    if fokontany:
        citoyens = citoyens.filter(fokontany=fokontany)
        naissances = naissances.filter(fokontany=fokontany)
        demandes = demandes.filter(fokontany=fokontany)
        adidy = adidy.filter(fokontany=fokontany)

    return {
        "labels": [f"{MOIS_FR[m - 1]} {str(a)[2:]}" for a, m in periodes],
        "recensements": _serie_mensuelle(
            citoyens, "date_enregistrement", periodes
        ),
        "naissances": _serie_mensuelle(
            naissances, "date_naissance", periodes
        ),
        "demandes": _serie_mensuelle(
            demandes, "date_creation", periodes
        ),
        "adidy": _serie_mensuelle(
            adidy, "date_paiement", periodes
        ),
    }


def _donnees_carte():
    return list(
        annoter_population(Fokontany.objects.filter(actif=True))
        .order_by("nom")
        .values(
            "id",
            "nom",
            "code",
            "responsable",
            "adresse",
            "specificites",
            "telephone",
            "latitude",
            "longitude",
            "population_hommes",
            "population_femmes",
        )
    )


def accueil(request):
    fokontanys = annoter_population(
        Fokontany.objects.filter(actif=True).annotate(
            nb_citoyens=Count("citoyens", distinct=True),
            nb_demandes=Count("demandes", distinct=True),
        )
    )
    actualites = Actualite.objects.filter(publiee=True)[:3]

    return render(request, "accueil/accueil.html", {
        "fokontanys": fokontanys,
        "actualites": actualites,
        "carte_fokontany": _donnees_carte(),
        "annee_population": ANNEE_POPULATION_REFERENCE,
        "totaux_population": totaux_population(),
        "total_fokontany": fokontanys.count(),
        "total_citoyens": Citoyen.objects.count(),
        "total_actes": ActeEtatCivil.objects.count() + ActeNaissance.objects.count(),
        "total_demandes": Demande.objects.count(),
    })


def commune(request):
    fokontanys = annoter_population(
        Fokontany.objects.filter(actif=True).annotate(
            nb_citoyens=Count("citoyens", distinct=True),
            nb_naissances=Count("actes_naissance", distinct=True),
            nb_demandes=Count("demandes", distinct=True),
        )
    ).order_by("nom")

    return render(request, "accueil/commune.html", {
        "fokontanys": fokontanys,
        "carte_fokontany": _donnees_carte(),
        "annee_population": ANNEE_POPULATION_REFERENCE,
        "totaux_population": totaux_population(),
        "total_fokontany": fokontanys.count(),
    })


@login_required
def dashboard(request):
    contexte = {
        "role_libelle": nom_role(request.user),
        "peut_gerer_comptes": est_administrateur(request.user),
        "peut_traiter_demandes": est_maire(request.user) or est_secretaire(request.user),
        "peut_gerer_caisse": est_tresorier(request.user) or est_maire(request.user),
    }

    if acces_global(request.user):
        fokontanys = annoter_population(Fokontany.objects.annotate(
            nb_citoyens=Count("citoyens", distinct=True),
            nb_actes=Count("actes_etat_civil", distinct=True),
            nb_naissances=Count("actes_naissance", distinct=True),
            nb_documents=Count("documents_administratifs", distinct=True),
            nb_agents=Count("agents", distinct=True),
            nb_demandes=Count("demandes", distinct=True),
            nb_demandes_attente=Count(
                "demandes",
                filter=Q(
                    demandes__statut__in=[
                        Demande.STATUT_EN_ATTENTE,
                        Demande.STATUT_MISE_EN_ATTENTE,
                    ]
                ),
                distinct=True,
            ),
            nb_mariages=Count(
                "actes_etat_civil",
                filter=Q(actes_etat_civil__type_acte="MARIAGE"),
                distinct=True,
            ),
            nb_deces=Count(
                "actes_etat_civil",
                filter=Q(actes_etat_civil__type_acte="DECES"),
                distinct=True,
            ),
        )).order_by("nom")

        periodes = _derniers_mois()
        total_adidy = PaiementAdidy.objects.aggregate(
            total=Sum("montant")
        )["total"] or 0
        entrees = FondsAssociation.objects.filter(
            type_mouvement=FondsAssociation.TYPE_ENTREE
        ).aggregate(total=Sum("montant"))["total"] or 0
        sorties = FondsAssociation.objects.filter(
            type_mouvement=FondsAssociation.TYPE_SORTIE
        ).aggregate(total=Sum("montant"))["total"] or 0
        total_naissances = ActeNaissance.objects.count() + ActeEtatCivil.objects.filter(
            type_acte="NAISSANCE"
        ).count()

        contexte.update({
            "fokontanys": fokontanys,
            "annee_population": ANNEE_POPULATION_REFERENCE,
            "totaux_population": totaux_population(),
            "total_fokontany": fokontanys.count(),
            "total_citoyens": Citoyen.objects.count(),
            "total_actes": ActeEtatCivil.objects.count(),
            "total_naissances": total_naissances,
            "total_mariages": ActeEtatCivil.objects.filter(
                type_acte="MARIAGE"
            ).count(),
            "total_deces": ActeEtatCivil.objects.filter(
                type_acte="DECES"
            ).count(),
            "total_personnel": Personnel.objects.count(),
            "total_documents": DocumentAdministratif.objects.count(),
            "total_cin": DocumentAdministratif.objects.filter(
                type_document=DocumentAdministratif.TYPE_CIN
            ).count(),
            "total_bulletins": DocumentAdministratif.objects.filter(
                type_document=DocumentAdministratif.TYPE_BULLETIN_NAISSANCE
            ).count(),
            "total_demandes": Demande.objects.count(),
            "total_demandes_attente": Demande.objects.filter(
                statut__in=[
                    Demande.STATUT_EN_ATTENTE,
                    Demande.STATUT_MISE_EN_ATTENTE,
                ]
            ).count(),
            "total_demandes_amelioration": Demande.objects.filter(
                type_demande__in=Demande.TYPES_AMELIORATION
            ).count(),
            "total_adidy": total_adidy,
            "solde_association": entrees - sorties,
            "total_entrees_association": entrees,
            "total_sorties_association": sorties,
            "demandes_recentes": Demande.objects.select_related(
                "fokontany", "demandeur"
            ).order_by("-date_creation")[:8],
            "mariages_recents": ActeEtatCivil.objects.filter(
                type_acte="MARIAGE"
            ).select_related("fokontany").order_by("-date_acte")[:5],
            "naissances_recentes": ActeNaissance.objects.select_related(
                "fokontany"
            ).order_by("-date_naissance")[:5],
            "actualites": Actualite.objects.filter(publiee=True)[:4],
            "responsables": Personnel.objects.filter(
                statut="ACTIF"
            ).select_related("fokontany").order_by("-photo", "nom")[:8],
            "graphique": _donnees_graphique(periodes),
        })

        return render(request, "accueil/dashboard_maire.html", contexte)

    if est_chef(request.user):
        fokontany = fokontany_utilisateur(request.user)

        if not fokontany:
            return render(request, "accueil/sans_role.html", {
                "message": "Votre compte chef n'est affecté à aucun fokontany.",
            })

        periodes = _derniers_mois(6)
        total_adidy = PaiementAdidy.objects.filter(
            fokontany=fokontany
        ).aggregate(total=Sum("montant"))["total"] or 0

        contexte.update({
            "fokontany": fokontany,
            "population": fokontany.populations.filter(
                annee=ANNEE_POPULATION_REFERENCE
            ).first(),
            "annee_population": ANNEE_POPULATION_REFERENCE,
            "total_citoyens": fokontany.citoyens.count(),
            "total_actes": fokontany.actes_etat_civil.count(),
            "total_naissances": fokontany.actes_naissance.count(),
            "total_documents": fokontany.documents_administratifs.count(),
            "total_personnel": fokontany.agents.count(),
            "total_adidy": total_adidy,
            "total_demandes": fokontany.demandes.count(),
            "total_demandes_attente": fokontany.demandes.filter(
                statut__in=[
                    Demande.STATUT_EN_ATTENTE,
                    Demande.STATUT_MISE_EN_ATTENTE,
                ]
            ).count(),
            "demandes_recentes": fokontany.demandes.select_related(
                "demandeur"
            ).order_by("-date_creation")[:8],
            "naissances_recentes": fokontany.actes_naissance.order_by(
                "-date_naissance"
            )[:5],
            "adidy_recents": fokontany.paiements_adidy.select_related(
                "citoyen"
            ).order_by("-date_paiement")[:5],
            "actualites": Actualite.objects.filter(publiee=True)[:4],
            "graphique": _donnees_graphique(periodes, fokontany=fokontany),
        })

        return render(request, "accueil/dashboard_chef.html", contexte)

    return render(request, "accueil/sans_role.html", {
        "message": "Votre compte n'a aucun rôle actif dans la plateforme.",
    })
