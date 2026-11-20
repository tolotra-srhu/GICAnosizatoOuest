from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from comptes.models import ProfilUtilisateur
from comptes.permissions import (
    acces_communal,
    filtrer_fokontany,
    gestion_comptes_required,
)
from .forms import FokontanyForm
from .models import (
    ANNEE_POPULATION_REFERENCE,
    SOURCE_POPULATION_REFERENCE,
    Fokontany,
    PopulationFokontany,
    annoter_population,
    totaux_population,
)


def _lignes_population(fokontanys, annee, valeurs=None):
    populations = {
        population.fokontany_id: population
        for population in PopulationFokontany.objects.filter(annee=annee)
    }
    lignes = []

    for fokontany in fokontanys:
        population = populations.get(fokontany.pk)
        if valeurs is None:
            hommes = population.hommes if population else ""
            femmes = population.femmes if population else ""
        else:
            hommes = valeurs.get(f"hommes_{fokontany.pk}", "")
            femmes = valeurs.get(f"femmes_{fokontany.pk}", "")

        try:
            total = int(hommes) + int(femmes)
        except (TypeError, ValueError):
            total = ""

        lignes.append({
            "fokontany": fokontany,
            "hommes": hommes,
            "femmes": femmes,
            "total": total,
            "source": population.source if population else SOURCE_POPULATION_REFERENCE,
        })

    return lignes


@acces_communal
def liste_fokontany(request):
    recherche = request.GET.get("q", "").strip()

    fokontany = filtrer_fokontany(
        Fokontany.objects.all(),
        request.user,
        champ="pk",
    )

    if recherche:
        fokontany = fokontany.filter(nom__icontains=recherche)

    fokontany = annoter_population(fokontany)

    return render(request, "fokontany/liste.html", {
        "fokontany": fokontany,
        "recherche": recherche,
        "annee_population": ANNEE_POPULATION_REFERENCE,
    })


@gestion_comptes_required
def ajouter_fokontany(request):
    if request.method == "POST":
        formulaire = FokontanyForm(request.POST)

        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "Le fokontany a été ajouté avec succès.")
            return redirect("fokontany:liste")
    else:
        formulaire = FokontanyForm()

    return render(request, "fokontany/formulaire.html", {
        "formulaire": formulaire,
        "titre": "Ajouter un fokontany",
    })


@gestion_comptes_required
def modifier_fokontany(request, pk):
    fokontany = get_object_or_404(Fokontany, pk=pk)

    if request.method == "POST":
        formulaire = FokontanyForm(request.POST, instance=fokontany)

        if formulaire.is_valid():
            formulaire.save()
            messages.success(request, "Le fokontany a été modifié avec succès.")
            return redirect("fokontany:liste")
    else:
        formulaire = FokontanyForm(instance=fokontany)

    return render(request, "fokontany/formulaire.html", {
        "formulaire": formulaire,
        "titre": "Modifier un fokontany",
    })


@gestion_comptes_required
def population(request):
    annee = ANNEE_POPULATION_REFERENCE
    fokontanys = Fokontany.objects.filter(actif=True).order_by("nom")
    source = request.POST.get(
        "source", SOURCE_POPULATION_REFERENCE
    ).strip() if request.method == "POST" else SOURCE_POPULATION_REFERENCE

    if request.method == "POST":
        erreurs = []
        donnees = []

        for fokontany in fokontanys:
            try:
                hommes = int(request.POST.get(f"hommes_{fokontany.pk}", ""))
                femmes = int(request.POST.get(f"femmes_{fokontany.pk}", ""))
                if hommes < 0 or femmes < 0:
                    raise ValueError
            except (TypeError, ValueError):
                erreurs.append(
                    f"Valeurs invalides pour {fokontany.nom} : "
                    "saisissez des nombres entiers positifs."
                )
                continue
            donnees.append((fokontany, hommes, femmes))

        if not source:
            erreurs.append("La source des données est obligatoire.")

        if erreurs:
            messages.error(request, " ".join(erreurs))
        else:
            for fokontany, hommes, femmes in donnees:
                PopulationFokontany.objects.update_or_create(
                    fokontany=fokontany,
                    annee=annee,
                    defaults={
                        "hommes": hommes,
                        "femmes": femmes,
                        "source": source,
                    },
                )
            messages.success(
                request,
                f"Population {annee} enregistrée pour {len(donnees)} fokontany.",
            )
            return redirect("fokontany:population")

    return render(request, "fokontany/population.html", {
        "lignes": _lignes_population(
            fokontanys,
            annee,
            request.POST if request.method == "POST" else None,
        ),
        "annee": annee,
        "source": source,
        "totaux": totaux_population(annee),
    })


@acces_communal
def detail_fokontany(request, pk):
    from django.db.models import Sum

    from accueil.models import Actualite
    from demandes.models import Demande
    from etat_civil.models import ActeNaissance, DocumentAdministratif
    from finances.models import PaiementAdidy
    from personnel.models import Personnel

    fokontany = get_object_or_404(
        filtrer_fokontany(Fokontany.objects.all(), request.user, champ="pk"),
        pk=pk,
    )

    total_adidy = PaiementAdidy.objects.filter(
        fokontany=fokontany
    ).aggregate(total=Sum("montant"))["total"] or 0

    return render(request, "fokontany/detail.html", {
        "fokontany": fokontany,
        "population": fokontany.populations.filter(
            annee=ANNEE_POPULATION_REFERENCE
        ).first(),
        "annee_population": ANNEE_POPULATION_REFERENCE,
        "total_adidy": total_adidy,
        "citoyens_recents": fokontany.citoyens.all()[:6],
        "naissances_recentes": fokontany.actes_naissance.all()[:6],
        "documents_recents": fokontany.documents_administratifs.all()[:6],
        "demandes_recentes": fokontany.demandes.select_related(
            "demandeur"
        )[:6],
        "personnels": fokontany.agents.all()[:8],
        "chefs": fokontany.profils_utilisateurs.filter(
            role=ProfilUtilisateur.ROLE_CHEF
        ).select_related("utilisateur"),
        "total_demandes_attente": fokontany.demandes.filter(
            statut__in=[
                Demande.STATUT_EN_ATTENTE,
                Demande.STATUT_MISE_EN_ATTENTE,
            ]
        ).count(),
        "actualites": Actualite.objects.filter(publiee=True)[:3],
    })


@acces_communal
def carte_fokontany(request):
    fokontany = annoter_population(
        filtrer_fokontany(
            Fokontany.objects.filter(actif=True),
            request.user,
            champ="pk",
        )
    ).values(
        "id",
        "nom",
        "code",
        "responsable",
        "adresse",
        "telephone",
        "latitude",
        "longitude",
        "population_hommes",
        "population_femmes",
    )

    return render(request, "fokontany/carte.html", {
        "fokontany": list(fokontany),
        "annee_population": ANNEE_POPULATION_REFERENCE,
    })
