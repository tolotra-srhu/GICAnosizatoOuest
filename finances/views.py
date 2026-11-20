from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.shortcuts import redirect, render

from comptes.permissions import (
    acces_communal,
    acces_global,
    fokontany_utilisateur,
    tresorerie_required,
)
from fokontany.models import Fokontany
from .forms import FondsAssociationForm, PaiementAdidyForm
from .models import FondsAssociation, PaiementAdidy


def _adidy_accessibles(user):
    paiements = PaiementAdidy.objects.select_related(
        "fokontany",
        "citoyen",
        "recu_par",
    )
    if acces_global(user):
        return paiements
    fokontany = fokontany_utilisateur(user)
    if not fokontany:
        return paiements.none()
    return paiements.filter(fokontany=fokontany)


@acces_communal
def adidy_liste(request):
    paiements = _adidy_accessibles(request.user)

    recherche = request.GET.get("q", "").strip()
    fokontany_id = request.GET.get("fokontany", "").strip()

    if recherche:
        paiements = paiements.filter(
            Q(contribuable__icontains=recherche)
            | Q(reference__icontains=recherche)
        )

    if fokontany_id and acces_global(request.user):
        paiements = paiements.filter(fokontany_id=fokontany_id)

    total = paiements.aggregate(total=Sum("montant"))["total"] or 0

    return render(request, "finances/adidy_liste.html", {
        "paiements": paiements,
        "recherche": recherche,
        "fokontany_selectionne": fokontany_id,
        "fokontanys": Fokontany.objects.all() if acces_global(request.user) else [],
        "total": total,
    })


@acces_communal
def adidy_ajouter(request):
    fokontany = fokontany_utilisateur(request.user)

    if not acces_global(request.user) and not fokontany:
        raise PermissionDenied

    if request.method == "POST":
        formulaire = PaiementAdidyForm(request.POST, fokontany=fokontany)

        if formulaire.is_valid():
            paiement = formulaire.save(commit=False)
            if fokontany:
                paiement.fokontany = fokontany
            paiement.recu_par = request.user
            if paiement.citoyen and not paiement.contribuable:
                paiement.contribuable = (
                    f"{paiement.citoyen.nom} {paiement.citoyen.prenoms}"
                )
            paiement.save()
            messages.success(
                request,
                f"Le paiement adidy {paiement.reference} a été enregistré.",
            )
            return redirect("finances:adidy_liste")
    else:
        formulaire = PaiementAdidyForm(fokontany=fokontany)

    return render(request, "finances/adidy_formulaire.html", {
        "formulaire": formulaire,
        "titre": "Enregistrer un paiement adidy",
    })


@tresorerie_required
def fonds_liste(request):
    mouvements = FondsAssociation.objects.select_related(
        "fokontany",
        "enregistre_par",
    )
    entrees = mouvements.filter(
        type_mouvement=FondsAssociation.TYPE_ENTREE
    ).aggregate(total=Sum("montant"))["total"] or 0
    sorties = mouvements.filter(
        type_mouvement=FondsAssociation.TYPE_SORTIE
    ).aggregate(total=Sum("montant"))["total"] or 0
    total_adidy = PaiementAdidy.objects.aggregate(
        total=Sum("montant")
    )["total"] or 0

    return render(request, "finances/fonds_liste.html", {
        "mouvements": mouvements,
        "entrees": entrees,
        "sorties": sorties,
        "solde": entrees - sorties,
        "total_adidy": total_adidy,
    })


@tresorerie_required
def fonds_ajouter(request):
    if request.method == "POST":
        formulaire = FondsAssociationForm(request.POST)

        if formulaire.is_valid():
            mouvement = formulaire.save(commit=False)
            mouvement.enregistre_par = request.user
            mouvement.save()
            messages.success(request, "Le mouvement a été enregistré.")
            return redirect("finances:fonds_liste")
    else:
        formulaire = FondsAssociationForm()

    return render(request, "finances/fonds_formulaire.html", {
        "formulaire": formulaire,
        "titre": "Ajouter un mouvement de caisse",
    })
